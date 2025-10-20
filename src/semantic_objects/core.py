from typing import List, Dict, Tuple, Type, Union, get_origin, get_args
from dataclasses import dataclass, field, fields
from semantic_mpc_interface.namespaces import PARAM, RDF, RDFS, SH, bind_prefixes
import yaml
import sys
from rdflib import Graph, Literal, BNode

# a relation that CAN be used (fulfilling closed world requirement)
def valid_field(relation = None, label=None, comment=None):
    return field(
        default=None,
        init=False,
        metadata={
            'relation': relation,
            'templatize': False,
            'label': label,
            'comment': comment
        }
    )

# a relation that is optional, and will be templatized (optional in bmotif template, used to query semantic data into objects)
def optional_field(relation= None, label=None, comment=None):
    return field(
        default=None,
        init=False,
        metadata={
            'relation': relation,
            'label': label,
            'comment': comment
        }
    )

# a field that is required (A SHACL qualified value shape requirement)
# TODO: Consider how to handle qualified vs nonqualified constraints
def required_field(relation = None, min = 1, max = None, qualified = True, label=None, comment=None):
    # If the relation is none, it will use a default relation from the types of each thing.
    return field(
        metadata={
            'relation': relation,
            'min': min,
            'max': max,
            'qualified': qualified,
            'label': label,
            'comment': comment
        }
    )

# Define a custom class for folded style text
class FoldedString(str):
    pass

# Create a custom representer for the folded style
def folded_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

# Register the representer
yaml.add_representer(FoldedString, folded_str_representer)

@dataclass
class Resource:

    @classmethod
    def _get_iri(cls):
        if not hasattr(cls, '_local_name'):
            raise Exception('Class must have _local_name attribute')
        return cls._ns[cls._local_name]
    
    @classmethod
    # TODO: have to edit this to get other attributes
    def _get_attributes(cls):
        attrs = {k: v for k, v in cls.__dict__.items()
            if not k.startswith('_') and not callable(v)}
        return attrs

    @classmethod
    def generate_turtle_body(cls, subject_name="name"):
        """Generate RDF/Turtle body for template"""
        
        g = Graph()
        relations = cls.get_relations()
        
        # Generate prefix declarations
        # TODO: replace this with some thing like in semantic_mpc_interface.namespaces
        bind_prefixes(g)
        
        g.add((PARAM['name'], RDF.type, cls._get_iri()))
        
        # Get all annotations from the class hierarchy
        all_annotations = {}
        for base in reversed(cls.__mro__):
            if hasattr(base, '__annotations__'):
                all_annotations.update(base.__annotations__)
        
        # Generate property triples
        for pred, objs in relations:
            if isinstance(objs, str):
                objs = [objs]
            if isinstance(objs, list):
                for obj in objs:
                    if obj in all_annotations.keys():
                        g.add((PARAM['name'], pred._get_iri(), PARAM[obj]))
                    elif obj in cls._get_attributes().keys():
                        attr_value = cls._get_attributes()[obj]
                        g.add((PARAM['name'], pred._get_iri(), attr_value))
            
        return g.serialize(format = 'ttl')

    @classmethod
    def get_dependencies(cls):
        """Get template dependencies based on annotations and field metadata"""
        dependencies = []
        
        # Check if this is a dataclass with fields
        if hasattr(cls, '__dataclass_fields__'):
            for field_name, field_obj in cls.__dataclass_fields__.items():
                annotation_type = field_obj.type
                # Skip if field has init=False and templatize=False
                if (field_obj.init == False and 
                    field_obj.metadata.get('templatize', True) == False):
                    continue
                    
                # Get the base type name for the dependency
                if hasattr(annotation_type, '__name__'):
                    template_name = annotation_type.__name__.lower()
                else:
                    template_name = str(annotation_type).lower()
                
                dependencies.append({
                    'template': template_name,
                    'args': {'name': field_name}
                })
        else:
            # Fallback to annotations for non-dataclass classes
            for annotation_name, annotation_type in cls.__annotations__.items():
                # Get the base type name for the dependency
                if hasattr(annotation_type, '__name__'):
                    template_name = annotation_type.__name__.lower()
                else:
                    template_name = str(annotation_type).lower()
                
                dependencies.append({
                    'template': template_name,
                    'args': {'name': annotation_name}
                })
        
        return dependencies

    @classmethod
    def get_optional_fields(cls):
        """Get list of optional field names from field metadata"""
        optional_fields = []
        
        # Check if this is a dataclass with fields
        if hasattr(cls, '__dataclass_fields__'):
            for field_name, field_obj in cls.__dataclass_fields__.items():
                # Fields with explicit optional metadata
                if field_obj.metadata.get('optional', False):
                    optional_fields.append(field_name)
                # Fields with init=False are optional (unless templatize=False)
                elif (field_obj.init == False and 
                      field_obj.metadata.get('templatize', True) != False):
                    optional_fields.append(field_name)
        
        # Also check for legacy _optional attribute
        if hasattr(cls, '_optional'):
            optional_fields.extend(cls._optional)
        
        return optional_fields

    @classmethod
    def generate_yaml_template(cls, template_name = None):
        """Generate complete YAML template"""
        if template_name == None:
            template_name = cls.__name__.lower()
            
        template = {
            template_name: {
                'body': cls.generate_turtle_body(),
                'dependencies': cls.get_dependencies()
            }
        }
        
        # Add optional fields if they exist
        optional_fields = cls.get_optional_fields()
        if optional_fields:
            # If only one optional field, use scalar format like in the YAML example
            if len(optional_fields) == 1:
                template[template_name]['optional'] = optional_fields[0]
            else:
                template[template_name]['optional'] = optional_fields
        
        return template

    @classmethod
    def to_yaml_str(cls, template_name=None):
        """Convert to YAML string"""
        if template_name == None:
            template_name = cls.__name__.lower()
        template = cls.generate_yaml_template(template_name)
        # return yaml.dump(template, default_flow_style=False, sort_keys=False)
        template[template_name]['body'] = FoldedString(template[template_name]['body'])
        return yaml.dump(template, explicit_end=False)

    @classmethod
    def _infer_relation_for_field(cls, field_name, field_obj):
        """
        Infer the relation for a field based on class type hierarchies.
        
        Looks up the relation in the ontology-specific DEFAULT_RELATIONS registry
        by checking (source_class, target_class) pairs, walking up both hierarchies.
        
        Args:
            field_name: Name of the field
            field_obj: The dataclass field object
            
        Returns:
            The inferred relation object
            
        Raises:
            ValueError: If no default relation can be found
        """
        # If relation is explicitly provided, use it
        if field_obj.metadata.get('relation') is not None:
            return field_obj.metadata['relation']
        
        # Get the target type from field annotation
        target_type = field_obj.type
        
        # Handle Optional, List, etc. - extract the actual type
        origin = get_origin(target_type)
        if origin is not None:
            # For Optional[X], List[X], etc., get X
            args = get_args(target_type)
            if args:
                target_type = args[0]
        
        # Handle Self reference
        if target_type == cls or str(target_type) == 'Self':
            target_type = cls
        
        # Find the ontology-specific DEFAULT_RELATIONS registry
        # Walk up the MRO to find a module that has DEFAULT_RELATIONS
        default_relations = None
        for base in cls.__mro__:
            if hasattr(base, '__module__'):
                module = sys.modules.get(base.__module__)
                if module and hasattr(module, 'DEFAULT_RELATIONS'):
                    default_relations = module.DEFAULT_RELATIONS
                    break
        
        if default_relations is None:
            raise ValueError(
                f"No DEFAULT_RELATIONS registry found for {cls.__name__}.{field_name}. "
                f"Please add a DEFAULT_RELATIONS dictionary to the ontology module."
            )
        
        # Try to find a matching relation by walking up both class hierarchies
        for source_class in cls.__mro__:
            if not hasattr(source_class, '__name__'):
                continue
            source_name = source_class.__name__
            
            # Walk up target class hierarchy
            target_mro = target_type.__mro__ if hasattr(target_type, '__mro__') else [target_type]
            for target_class in target_mro:
                if not hasattr(target_class, '__name__'):
                    continue
                target_name = target_class.__name__
                
                # Check if this pair exists in the registry
                key = (source_name, target_name)
                if key in default_relations:
                    return default_relations[key]
        
        # No matching relation found
        target_type_name = target_type.__name__ if hasattr(target_type, '__name__') else str(target_type)
        raise ValueError(
            f"No default relation found for {cls.__name__}.{field_name} "
            f"(source: {cls.__name__}, target: {target_type_name}). "
            f"Please either specify the relation explicitly in the field definition, "
            f"or add a mapping to DEFAULT_RELATIONS in the ontology module."
        )
                    
    @classmethod
    def get_relations(cls):
        """
        Accumulate relations from all bases up the MRO (excluding 'object').
        Infers relations when not explicitly provided.
        """
        # could validate that there are relations to get here
        all_relations = []
        seen_relations = set()
        
        # Get field-based relations from dataclass fields
        for base in reversed(cls.__mro__):
            if hasattr(base, '__dataclass_fields__'):
                for field_name, field_obj in base.__dataclass_fields__.items():
                    # Skip fields with init=False and templatize=False
                    if (field_obj.init == False and 
                        field_obj.metadata.get('templatize', True) == False):
                        continue
                    
                    # Infer or get the relation
                    try:
                        relation = cls._infer_relation_for_field(field_name, field_obj)
                    except ValueError:
                        # If no relation can be inferred and none is provided, skip
                        continue
                    
                    if relation:
                        # Create a hashable representation of the relation
                        relation_key = (relation._local_name, field_name)
                        if relation_key not in seen_relations:
                            all_relations.append((relation, field_name))
                            seen_relations.add(relation_key)
        
        return all_relations

    @classmethod
    def generate_rdf_class_definition(cls):
        """Generate RDF class definition with SHACL constraints like the example"""
        g = Graph()
        bind_prefixes(g)
        
        # Get class IRI
        class_iri = cls._get_iri()
        
        # TODO: Class definitions should come from node
        # Add basic class declarations
        g.add((class_iri, RDF.type, cls._type))
        for type in cls._other_types:
            g.add((class_iri, RDF.type, type))
        
        # Add comment if available
        if hasattr(cls, 'comment'):
            g.add((class_iri, RDFS.comment, Literal(cls.comment)))
        
        # Add label if available
        if hasattr(cls, 'label'):
            g.add((class_iri, RDFS.label, Literal(cls.label)))
        
        # Add subclass relationship - look for meaningful parent classes
        for base in cls.__mro__[1:]:  # Skip self
            if (hasattr(base, '_local_name') and hasattr(base, '_ns') and 
                base != Resource and base._local_name != cls._local_name and
                base.__name__ not in ['Node', 'Value', 'Predicate', 'NamedNode']):
                parent_iri = base._ns[base._local_name]
                g.add((class_iri, RDFS.subClassOf, parent_iri))
                break  # Only add the immediate parent
        
        # If no meaningful parent found, add subClassOf Concept for s223 classes
        if hasattr(cls, '_ns') and 's223' in str(cls._ns):
            # Check if we already added a subclass relationship
            has_subclass = any(g.triples((class_iri, RDFS.subClassOf, None)))
            if not has_subclass:
                g.add((class_iri, RDFS.subClassOf, cls._ns.Concept))
        
        # Add SHACL property constraints for dataclass fields
        if hasattr(cls, '__dataclass_fields__'):
            processed_relations = set()  # Track processed relations to avoid duplicates
            
            for field_name, field_obj in cls.__dataclass_fields__.items():
                # Infer or get the relation
                try:
                    relation = cls._infer_relation_for_field(field_name, field_obj)
                except ValueError:
                    # If no relation can be inferred and none is provided, skip
                    continue
                
                if relation:
                    # Create unique key for this relation to avoid duplicates
                    relation_key = relation._local_name
                    if relation_key in processed_relations:
                        continue
                    processed_relations.add(relation_key)
                    
                    # Create blank node for property constraint
                    prop_node = BNode()
                    g.add((class_iri, SH.property, prop_node))
                    g.add((prop_node, SH.path, relation._get_iri()))
                    
                    # Add comment from field metadata or generate one
                    field_comment = field_obj.metadata.get('comment')
                    target_class_name = None
                    
                    # Handle Self type annotation
                    if hasattr(field_obj, 'type'):
                        type_str = str(field_obj.type)
                        if field_obj.type == cls or type_str == 'Self' or 'Self' in type_str:
                            target_class_name = cls.__name__
                        elif hasattr(field_obj.type, '__name__'):
                            target_class_name = field_obj.type.__name__
                        else:
                            target_class_name = str(field_obj.type)
                    
                    if not field_comment and target_class_name:
                        field_comment = f"If the relation `{relation._local_name}` is present it must associate the `{cls.__name__}` with a `{target_class_name}`."
                    
                    if field_comment:
                        g.add((prop_node, RDFS.comment, Literal(field_comment)))
                    
                    # Add target class constraint based on field type annotation
                    if hasattr(field_obj, 'type') and hasattr(field_obj.type, '_get_iri'):
                        target_class = field_obj.type._get_iri()
                        g.add((prop_node, SH['class'], target_class))
                        
                        # Generate SHACL message
                        relation_name = relation._local_name
                        message = f"s223: If the relation `{relation_name}` is present it must associate the `{cls.__name__}` with a `{target_class_name}`."
                        g.add((prop_node, SH.message, Literal(message)))
                    elif field_obj.type == cls or 'Self' in str(field_obj.type):
                        # Handle Self reference
                        g.add((prop_node, SH['class'], class_iri))
                        
                        # Generate SHACL message for Self reference
                        relation_name = relation._local_name
                        message = f"s223: If the relation `{relation_name}` is present it must associate the `{cls.__name__}` with a `{cls.__name__}`."
                        g.add((prop_node, SH.message, Literal(message)))
                    
                    # Add cardinality constraints if specified
                    min_count = field_obj.metadata.get('min')
                    max_count = field_obj.metadata.get('max')
                    if min_count is not None:
                        g.add((prop_node, SH.minCount, Literal(min_count)))
                    if max_count is not None:
                        g.add((prop_node, SH.maxCount, Literal(max_count)))
        
        return g.serialize(format='turtle')
    
class Predicate(Resource):
    # currently just used for typecheck later 
    pass 

class Node(Resource):
    # A Node with a URI Ref
    pass

class Value(Resource):
    # A Literal
    pass

# Probably don't need a NamedNode class, since can just directly use rdflib URIRefs
class NamedNode(Resource):
    # A Named Node 
    pass
