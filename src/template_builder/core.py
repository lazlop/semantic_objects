from typing import List, Dict, Tuple, Type, Union, get_origin
from dataclasses import dataclass, field, fields
from semantic_mpc_interface.namespaces import PARAM, RDF, bind_prefixes
import yaml
from rdflib import Graph

# a relation that can be used
def valid_field(relation, label=None, comment=None):
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

# a relation that is optional, and will be templatized
def optional_field(relation, label=None, comment=None):
    return field(
        default=None,
        init=False,
        metadata={
            'relation': relation,
            'label': label,
            'comment': comment
        }
    )

# a field that is required
# TODO: maybe add cardinality constraints
def required_field(relation, min = 1, max = None, label=None, comment=None):
    return field(
        metadata={
            'relation': relation,
            'min': min,
            'max': max,
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

    relations = []

    @classmethod
    def _get_iri(cls):
        if not hasattr(cls, '_iri'):
            raise Exception('Class must have _iri attribute')
        return cls._ns[cls._iri]
    
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
    def generate_yaml_template(cls, template_name):
        """Generate complete YAML template"""
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
    def to_yaml(cls, template_name=None):
        """Convert to YAML string"""
        if template_name == None:
            template_name = cls.__name__.lower()
        template = cls.generate_yaml_template(template_name)
        # return yaml.dump(template, default_flow_style=False, sort_keys=False)
        template[template_name]['body'] = FoldedString(template[template_name]['body'])
        return yaml.dump(template, explicit_end=False)

    @classmethod
    def get_field_relations(cls):
        """Extract relations from field metadata"""
        field_relations = []
        
        if hasattr(cls, '__dataclass_fields__'):
            for field_name, field_obj in cls.__dataclass_fields__.items():
                relation = field_obj.metadata.get('relation')
                if relation:
                    field_relations.append((relation, field_name))
        
        return field_relations

    @classmethod
    def validate_relations(cls):
        # Check if we have either legacy relations or field-based relations
        has_legacy_relations = hasattr(cls, 'relations') and cls.relations != []
        has_field_relations = bool(cls.get_field_relations())
        
        if not has_legacy_relations and not has_field_relations:
            raise Exception('No relations defined')
        
        # Validate legacy relations if they exist
        if has_legacy_relations:
            # Get all relations for this class
            all_relations = []
            for base in reversed(cls.__mro__):
                if hasattr(base, 'relations'):
                    relations = getattr(base, 'relations')
                    if relations != []:
                        all_relations += relations
            
            # NOTE: not totally sure if I want to allow this behavior, or if I just want to check the current class
            # Get all annotations from the class hierarchy
            all_annotations = {}
            for base in reversed(cls.__mro__):
                if hasattr(base, '__annotations__'):
                    all_annotations.update(base.__annotations__)
            
            # Validate each relation
            for pred, objects in all_relations:
                if isinstance(objects, str):
                    objects = [objects]
                if not isinstance(objects, list):
                    raise TypeError(f'{objects=} must be a list or str')
                
                for obj in objects:
                    non_relation_attributes = [k for k in cls._get_attributes().keys() if k != 'relations']
                    if obj not in list(all_annotations.keys()) + non_relation_attributes:
                        raise ValueError(f'{obj} must be an existing attribute or annotation')
            
    @classmethod
    def get_relations(cls):
        """
        Accumulate relations from all bases up the MRO (excluding 'object').
        Supports both legacy relations and field-based relations.
        """
        cls.validate_relations()
        all_relations = []
        seen_relations = set()
        
        # Get legacy relations from class attributes
        for base in reversed(cls.__mro__):
            if hasattr(base, 'relations'):
                relations = getattr(base, 'relations')
                if relations == []:
                    continue
                for relation in relations:
                    # Create a hashable representation of the relation
                    relation_key = (relation[0]._iri, tuple(relation[1]) if isinstance(relation[1], list) else relation[1])
                    if relation_key not in seen_relations:
                        all_relations.append(relation)
                        seen_relations.add(relation_key)
        
        # Get field-based relations from dataclass fields
        for base in reversed(cls.__mro__):
            if hasattr(base, '__dataclass_fields__'):
                for field_name, field_obj in base.__dataclass_fields__.items():
                    relation = field_obj.metadata.get('relation')
                    if relation:
                        # Skip fields with init=False and templatize=False
                        if (field_obj.init == False and 
                            field_obj.metadata.get('templatize', True) == False):
                            continue
                        
                        # Create a hashable representation of the relation
                        relation_key = (relation._iri, field_name)
                        if relation_key not in seen_relations:
                            all_relations.append((relation, field_name))
                            seen_relations.add(relation_key)
        
        return all_relations
    
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
