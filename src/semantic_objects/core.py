from typing import List, Dict, Tuple, Type, Union, get_origin, get_args, Self
from dataclasses import dataclass, field, fields, _MISSING_TYPE
from semantic_mpc_interface.namespaces import PARAM, RDF, RDFS, SH, bind_prefixes
import yaml
import sys
from pathlib import Path
from rdflib import Graph, Literal, BNode

# TODO: Clean up implementation

def export_templates(dclass_lst: List[Type], dir_path_str: str, overwrite = True):
    class_lsts = get_related_classes(dclass_lst)
    dir = Path(dir_path_str)
    dir.mkdir(parents=True, exist_ok=True)
    # TODO: After addressing in semantic_mpc_interface, values will become properties
    files =  [dir / 'relations.yml', dir / 'entities.yml', dir / 'values.yml']
    for file, lst in zip(files, class_lsts):
        if file.exists() and not overwrite:
            continue
        if file.exists():
            file.unlink()
        for klass in lst:
            klass.to_yaml(file_path = file)
            
def get_related_classes(dclass: Union[Type, List[Type]], get_recursive = True):
    if isinstance(dclass, list):
        return _get_related_classes_lst(dclass, get_recursive)
    else:
        return _get_related_classes_type(dclass, get_recursive)
    
def _get_related_classes_type(dclass: Type, get_recursive = True, include_abstract = False):
    relations = [relation for relation, field_name in dclass.get_relations()]
    entities_and_values = [field.type for entity, field in dclass.__dataclass_fields__.items()]
    all_classes = [dclass] + relations + entities_and_values
    all_classes = list(set(all_classes))

    if get_recursive:
        new_classes = all_classes.copy()
        next_new_classes = []
        for i in range(100):
            for klass in new_classes:
                relations = [relation for relation, field_name in klass.get_relations()]
                entities_and_values = [field.type for entity, field in klass.__dataclass_fields__.items()]
                next_classes = relations + entities_and_values
                new_next_classes = set(next_classes) - set(all_classes)
                if new_classes == []:
                    break
                all_classes.extend(list(new_next_classes))
                new_classes = new_next_classes.copy()
                if i == 99:
                    raise RecursionError("Max depth reached")
            
    predicate_lst, entity_lst, value_lst = [], [], []
    # TODO: consider if we want to keep these distinctions, and have them as predicate, entity, property
    for lst, parent in [(predicate_lst, Predicate), (entity_lst, Node), (value_lst, Node)]:
        for klass in all_classes:
            if not include_abstract and klass.abstract:
                continue
            if issubclass(klass, parent):
                lst.append(klass)

    return predicate_lst, entity_lst, value_lst   

def _get_related_classes_lst(dclass_lst: List[Type], get_recursive = True):
    predicate_lst, entity_lst, value_lst = [], [], []
    for dclass in dclass_lst:
        class_lsts = _get_related_classes_type(dclass, get_recursive)
        for lst, new_klasses in zip([predicate_lst, entity_lst, value_lst], class_lsts): 
            for klass in new_klasses: 
                if klass not in lst:
                    lst.append(klass)
    return predicate_lst, entity_lst, value_lst        

def get_module_classes(module_lst):
    predicate_lst, entity_lst, value_lst = [], [], []
    for module in module_lst:
        for k, v in module.__dict__.items():
            if not isinstance(v, type):
                continue
            if issubclass(v, Resource):
                class_lsts = get_related_classes(v)
                for lst, new_klasses in zip([predicate_lst, entity_lst, value_lst], class_lsts): 
                    for klass in new_klasses: 
                        if klass not in lst:
                            lst.append(klass)
    return predicate_lst, entity_lst, value_lst

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

# TODO: consider an alternative way of defining the maximum and minimum 
def exclusive_field(relation = None, min = 1, max = 1, qualified = True, label=None, comment=None):
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
def semantic_object(cls):
    # Get parent class fields and their types
    parent_fields = {}
    for base in cls.__mro__[1:]:
        if hasattr(base, '__dataclass_fields__'):
            parent_fields.update(base.__dataclass_fields__)
    
    # Ensure cls has __annotations__
    if not hasattr(cls, '__annotations__'):
        cls.__annotations__ = {}
    
    # Check which ones are redefined in this class
    for field_name, parent_field in parent_fields.items():
        if field_name in cls.__dict__ and not isinstance(getattr(cls, field_name), type(field)):
            fixed_value = cls.__dict__[field_name]
            # Copy the type annotation from parent
            cls.__annotations__[field_name] = parent_field.type
            # Set as required_field with the fixed value as default
            # Preserve any existing metadata from parent field
            parent_metadata = parent_field.metadata.copy() if parent_field.metadata else {}
            # Create a new field with init=False since it has a fixed default
            new_field = field(
                default=fixed_value,
                init=False,
                metadata={
                    'relation': parent_metadata.get('relation'),
                    'min': parent_metadata.get('min', 1),
                    'max': parent_metadata.get('max'),
                    'qualified': parent_metadata.get('qualified', True),
                    'label': parent_metadata.get('label'),
                    'comment': parent_metadata.get('comment')
                }
            )
            setattr(cls, field_name, new_field)
    
    # Set _name if not already defined in this class's __dict__
    if '_name' not in cls.__dict__:
        cls._name = cls.__name__
    
    # Set abstract to False if not already defined in this class's __dict__
    if 'abstract' not in cls.__dict__:
        cls.abstract = False
    
    return dataclass(cls)

# Define a custom class for folded style text
class FoldedString(str):
    pass

# Create a custom representer for the folded style
def folded_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

# Register the representer
yaml.add_representer(FoldedString, folded_str_representer)

@semantic_object
class Resource:

    @classmethod
    def _get_iri(cls):
        if not hasattr(cls, '_name'):
            if cls.abstract:
                raise Exception(f'Class {cls} is abstract, has no iri')
            raise Exception(f'Class {cls} must have _name attribute')
        return cls._ns[cls._name]
    
    @classmethod
    # TODO: not sure this works in all cases
    def _get_attributes(cls):
        attrs = {k: v for k, v in cls.__dict__.items()
            if not k.startswith('_')}
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
        
        # TODO: May also want to get the class variables, or consider making all class variables fields
        # currently things have to be written as fields in order to be templated 
        seen_fields = set()
        for base in cls.__mro__:
            if hasattr(base, '__dataclass_fields__'):
                for field_name, field_obj in base.__dataclass_fields__.items():
                    # Skip fields with init=False and templatize=False
                    if (field_obj.init == False and 
                        field_obj.metadata.get('templatize', True) == False):
                        continue
                    if field_name in seen_fields:
                        continue
                    seen_fields.add(field_name)
                    relation = cls._infer_relation_for_field(field_name, field_obj)
                    if not isinstance(field_obj.default,_MISSING_TYPE):
                        g.add((PARAM['name'], relation._get_iri(), field_obj.default._get_iri()))
                    else:
                        # Following lead from how we get args, not exactly aligned with Semantic_MPC_Interface
                        g.add((PARAM['name'], relation._get_iri(), PARAM[field_name]))
            
        return g.serialize(format = 'ttl')

    # TODO: Decide if this is how we want to handle named node dependencies
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

                if issubclass(annotation_type, NamedNode):
                    continue

                if not isinstance(field_obj.default,_MISSING_TYPE):
                    continue

                dependencies.append({
                    'template': annotation_type.__name__,
                    'args': {'name': field_name}
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
        
        return optional_fields

    @classmethod
    def generate_yaml_template(cls, template_name = None):
        """Generate complete YAML template"""
        if template_name == None:
            template_name = cls.__name__
            
        template = {
            template_name: {
                'body': cls.generate_turtle_body(),
                'dependencies': cls.get_dependencies()
            }
        }
        # NOTE: Only adding dependencies if they exist
        # template = {}
        # template[template_name] = {}
        # template[template_name]['body'] = cls.generate_turtle_body()
        # dependencies = cls.get_dependencies()
        # if dependencies != []:
        #     template[template_name]['dependencies'] = dependencies

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
    def to_yaml(cls, template_name=None, file_path: Path = None,):
        """Convert to YAML string"""
        if template_name == None:
            template_name = cls.__name__
        template = cls.generate_yaml_template(template_name)
        # return yaml.dump(template, default_flow_style=False, sort_keys=False)
        template[template_name]['body'] = FoldedString(template[template_name]['body'])
        if file_path is not None:
            with open(file_path, 'a') as f:
                yaml.dump(template, f, explicit_end=False)
        return yaml.dump(template, explicit_end=False)

    @classmethod
    def _infer_relation_for_field(cls, field_name, field_obj):
        """
        Infer the relation for a field based on class type hierarchies.
        
        Looks up the relation by checking (source_class, target_class) pairs
        in _valid_relations declarations, walking up both hierarchies.
        
        Args:
            field_name: Name of the field
            field_obj: The dataclass field object
            
        Returns:
            The inferred relation object
            
        Raises:
            ValueError: If no relation can be found
        """
        # If relation is explicitly provided, use it
        if field_obj.metadata.get('relation') is not None:
            return field_obj.metadata['relation']
        
        # Get the target type from field annotation
        target_type = field_obj.type
        
        # TODO: Look back into handling lists/optional, like looking in Optional, List, etc. - extract the actual type
        origin = get_origin(target_type)
        if origin is not None:
            # For Optional[X], List[X], etc., get X
            args = get_args(target_type)
            if args:
                target_type = args[0]
        
        # Handle Self reference
        if target_type == cls or str(target_type) == 'Self':
            target_type = cls
        
        # Try to find a matching relation by walking up both class hierarchies
        for source_class in cls.__mro__:
            if not hasattr(source_class, '_valid_relations'):
                continue
            # Walk up target class hierarchy
            target_mro = target_type.__mro__ if hasattr(target_type, '__mro__') else [target_type]
            for target_class in target_mro:
                # Check each relation in _valid_relations
                for relation, valid_target in source_class._valid_relations:
                    # Handle Self reference in _valid_relations
                    if valid_target is Self or str(valid_target) == 'Self':
                        valid_target = source_class
                    # Check if target class matches
                    if valid_target == target_class or (hasattr(valid_target, '__name__') and hasattr(target_class, '__name__') and valid_target.__name__ == target_class.__name__):
                        return relation
        raise ValueError(f"No relation found for field '{field_name}' with type '{target_type}' on {cls}, set it manually")
                    
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
                    relation = cls._infer_relation_for_field(field_name, field_obj)
                    
                    relation_key = (relation._name, field_name)
                    if relation_key not in seen_relations:
                        all_relations.append((relation, field_name))
                        seen_relations.add(relation_key)
        
        return all_relations

    @classmethod
    def _create_qualified_value_shape(cls, g, prop_node, field_obj, field_name, class_iri):
        # TODO: THIS IMPLEMENTATION IS UNFINISHED
        """
        Create a qualified value shape for a field, following the pattern from _generate_shapes.
        
        Args:
            g: The RDF graph
            prop_node: The property shape node
            field_obj: The dataclass field object
            field_name: Name of the field
            class_iri: IRI of the class being defined
        """
        # Create qualified value shape node
        qual_val_shape = BNode()
        
        # Determine target type
        target_type = field_obj.type
        origin = get_origin(target_type)
        if origin is not None:
            args = get_args(target_type)
            if args:
                target_type = args[0]
        
        # Handle Self reference
        if target_type == cls or str(target_type) == 'Self':
            target_type = cls
        
        # Add qualified value shape based on field type
        add_qual_val_shape = True
        
        # Check if this is a literal type
        if isinstance(field_obj.default, Literal) if hasattr(field_obj, 'default') else False:
            g.add((qual_val_shape, SH.hasValue, field_obj.default))
        # Check if target is a Resource subclass (entity/class type)
        elif hasattr(target_type, '_get_iri'):
            g.add((qual_val_shape, SH['class'], target_type._get_iri()))
        # For other types, use hasValue if a default is provided
        elif hasattr(field_obj, 'default') and field_obj.default is not None:
            g.add((qual_val_shape, SH.hasValue, field_obj.default))
        else:
            # No qualified value shape needed for parameters without constraints
            add_qual_val_shape = False
        
        if add_qual_val_shape:
            # Add label for the qualified value shape
            label = field_obj.metadata.get('label', field_name)
            g.add((qual_val_shape, RDFS.label, Literal(label)))
            
            # Link qualified value shape to property
            g.add((prop_node, SH.qualifiedMinCount, Literal(1)))
            g.add((prop_node, SH.qualifiedValueShape, qual_val_shape))
            g.add((qual_val_shape, RDF.type, SH.NodeShape))
    


    # TODO: Address hardcoded type Class
    @classmethod
    def generate_rdf_class_definition(cls, include_hierarchy=False):
        """
        Generate RDF class definition with SHACL constraints.
        
        Args:
            include_hierarchy: If True, include relations from parent classes in the hierarchy.
                             If False, only include relations declared directly on this class.
        """
        g = Graph()
        bind_prefixes(g)
        
        # Get class IRI
        class_iri = cls._get_iri()
        g.add((class_iri, RDF.type, cls._ns['Class']))
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
            if (hasattr(base, '_name') and hasattr(base, '_ns') and 
                base != Resource and base._name != cls._name and
                base.__name__ not in ['Node', 'Value', 'Predicate', 'NamedNode']):
                parent_iri = base._ns[base._name]
                g.add((class_iri, RDFS.subClassOf, parent_iri))
                break  # Only add the immediate parent
        
        # Track property shapes and counts (following _generate_shapes pattern)
        shape_path_name_dct = {}  # Maps relation IRI to property shape node
        prop_counts = {}  # Track count of each property
        processed_relations = set()  # Track processed relations to avoid duplicates

        # TODO: This ipmlementation is half finished, and repetitive with semantic_mpc_interface
        if hasattr(cls, '__dataclass_fields__'):
            # Determine which fields to process based on include_hierarchy
            if include_hierarchy:
                # Process all fields including inherited ones
                fields_to_process = cls.__dataclass_fields__.items()
            else:
                # Only process fields declared directly on this class
                # Get fields from parent classes to exclude them
                parent_fields = set()
                for base in cls.__mro__[1:]:  # Skip self
                    if hasattr(base, '__dataclass_fields__'):
                        parent_fields.update(base.__dataclass_fields__.values())
                
                # Filter to only fields declared on this class
                fields_to_process = [
                    (name, field_obj) 
                    for name, field_obj in cls.__dataclass_fields__.items()
                    if field_obj not in parent_fields
                ]
            
            # First pass: count properties and create property shapes
            for field_name, field_obj in fields_to_process:
                # Infer or get the relation
                relation = cls._infer_relation_for_field(field_name, field_obj)
                if relation is None:
                    continue
                
                relation_iri = relation._get_iri()
                
                # Track property counts
                if relation_iri in prop_counts:
                    prop_counts[relation_iri] += 1
                else:
                    prop_counts[relation_iri] = 1
                
                # Only create property shape once per relation
                if relation_iri in shape_path_name_dct:
                    continue
                
                # Create unique key for this relation to avoid duplicates
                relation_key = relation._name
                if relation_key in processed_relations:
                    continue
                processed_relations.add(relation_key)
                
                # Create blank node for property constraint
                prop_node = BNode()
                g.add((class_iri, SH.property, prop_node))
                g.add((prop_node, RDF.type, SH.PropertyShape))
                g.add((prop_node, SH.path, relation_iri))
                
                # Store in dictionary for later reference
                shape_path_name_dct[relation_iri] = prop_node
                
                # Add comment from field metadata or generate one
                field_comment = field_obj.metadata.get('comment')
                target_class_name = None
                
                # handle class or value of annotation 
                if hasattr(field_obj, 'default'):
                    type_str = str(field_obj.default)
                    
                elif hasattr(field_obj, 'type'):
                    type_str = str(field_obj.type)
                
                if type_str:
                    if field_obj.type == cls or type_str == 'Self' or 'Self' in type_str:
                        target_class_name = cls.__name__
                    elif hasattr(field_obj.type, '__name__'):
                        target_class_name = field_obj.type.__name__
                    else:
                        target_class_name = str(field_obj.type)
                
                if not field_comment and target_class_name:
                    field_comment = f"If the relation `{relation._name}` is present it must associate the `{cls.__name__}` with a `{target_class_name}`."
                
                if field_comment:
                    g.add((prop_node, RDFS.comment, Literal(field_comment)))
                
                # Add target class constraint based on field type annotation
                if hasattr(field_obj, 'default'):
                    target_class = field_obj.type._get_iri()
                    g.add((prop_node, SH['value'], target_class))
                elif hasattr(field_obj, 'type'):
                    target_class = field_obj.type._get_iri()
                    g.add((prop_node, SH['class'], target_class))
                    
                    message = f"s223: If the relation `{relation._name}` is present it must associate the `{cls.__name__}` with a `{target_class_name}`."
                    g.add((prop_node, SH.message, Literal(message)))
            
            # Second pass: create qualified value shapes for each field
            for field_name, field_obj in fields_to_process:
                # Infer or get the relation
                relation = cls._infer_relation_for_field(field_name, field_obj)
                if relation is None:
                    continue
                
                relation_iri = relation._get_iri()
                
                # Get the property shape node
                if relation_iri not in shape_path_name_dct:
                    continue
                
                prop_node = shape_path_name_dct[relation_iri]
                
                # Create qualified value shape (following _generate_shapes pattern)
                if field_obj.metadata.get('qualified', True):
                    cls._create_qualified_value_shape(g, prop_node, field_obj, field_name, class_iri)
            
            # Add minCount/maxCount based on property counts and field metadata
            for relation_iri, count in prop_counts.items():
                if relation_iri in shape_path_name_dct:
                    prop_node = shape_path_name_dct[relation_iri]
                    
                    # Use the count as minCount (following _generate_shapes pattern)
                    # This represents the total number of times this relation appears
                    g.add((prop_node, SH.minCount, Literal(count)))
                    
                    # Check if any field specifies a maxCount
                    max_count = None
                    for field_name, field_obj in fields_to_process:
                        relation = cls._infer_relation_for_field(field_name, field_obj)
                        if relation and relation._get_iri() == relation_iri:
                            field_max = field_obj.metadata.get('max')
                            if field_max is not None:
                                max_count = field_max
                                break
                    
                    if max_count is not None:
                        g.add((prop_node, SH.maxCount, Literal(max_count)))
        
        # Add SHACL property constraints from _valid_relations declarations
        # Determine which classes to process based on include_hierarchy
        if include_hierarchy:
            # Process all classes in the hierarchy
            classes_to_process = cls.__mro__
        else:
            # Only process _valid_relations declared directly on this class
            # Check if this specific class (not inherited) has _valid_relations
            classes_to_process = []
            if '_valid_relations' in cls.__dict__:
                classes_to_process = [cls]
        
        for base_class in classes_to_process:
            # Skip base classes that don't have _valid_relations
            if not hasattr(base_class, '_valid_relations'):
                continue
            
            # Process each relation in _valid_relations
            for relation, target_class in base_class._valid_relations:
                # Create unique key for this relation to avoid duplicates
                relation_key = relation._name
                if relation_key in processed_relations:
                    continue
                processed_relations.add(relation_key)
                
                relation_iri = relation._get_iri()
                
                # Create blank node for property constraint
                prop_node = BNode()
                g.add((class_iri, SH.property, prop_node))
                g.add((prop_node, RDF.type, SH.PropertyShape))
                g.add((prop_node, SH.path, relation_iri))
                
                # Determine target class name for comments and messages
                if target_class is None:  # Handle None type
                    target_class_name = "None"
                elif target_class is Self or str(target_class) == 'Self':
                    target_class_name = cls.__name__
                    target_class = cls
                elif hasattr(target_class, '__name__'):
                    target_class_name = target_class.__name__
                else:
                    target_class_name = str(target_class)
                
                # Generate comment
                field_comment = f"If the relation `{relation._name}` is present it must associate the `{cls.__name__}` with a `{target_class_name}`."
                g.add((prop_node, RDFS.comment, Literal(field_comment)))
                
                # Add sh:class constraint if target class has _get_iri
                if hasattr(target_class, '_get_iri'):
                    target_class_iri = target_class._get_iri()
                    g.add((prop_node, SH['class'], target_class_iri))
                    
                    # Generate SHACL message
                    message = f"s223: If the relation `{relation._name}` is present it must associate the `{cls.__name__}` with a `{target_class_name}`."
                    g.add((prop_node, SH.message, Literal(message)))
        
        return g.serialize(format='turtle')
    
class Predicate(Resource):
    # TODO: Predicate is partially implemented
    _subproperty_of = None  # Can be set to another Predicate class
    _domain = None  # Can be set to a Node class
    _range = None  # Can be set to a Node class
    
    @classmethod
    def generate_turtle_body(cls, subject_name="name", target_name = "target"):
        """Generate RDF/Turtle body for template"""
        
        g = Graph()
        bind_prefixes(g)
        
        prop_iri = cls._get_iri()
        
        g.add((PARAM[subject_name], prop_iri, PARAM[target_name]))

        if cls._domain is not None:
            domain_iri = cls._domain._get_iri()
            g.add((prop_iri, RDFS.domain, domain_iri))
        
        # Add range constraint if specified
        if cls._range is not None:
            range_iri = cls._range._get_iri()
            g.add((prop_iri, RDFS.range, range_iri))
        return g.serialize(format = 'ttl')
    
    @classmethod
    def generate_rdf_property_definition(cls):
        """Generate RDF property definition with subproperty and domain/range constraints"""
        g = Graph()
        bind_prefixes(g)
        
        # Get property IRI
        prop_iri = cls._get_iri()
        
        # Add basic property declaration
        g.add((prop_iri, RDF.type, RDF.Property))
        
        # Add label if available
        if hasattr(cls, 'label'):
            g.add((prop_iri, RDFS.label, Literal(cls.label)))
        
        # Add comment if available
        if hasattr(cls, 'comment'):
            g.add((prop_iri, RDFS.comment, Literal(cls.comment)))
        
        # Add subPropertyOf if specified
        if cls._subproperty_of is not None:
            parent_iri = cls._subproperty_of._get_iri()
            g.add((prop_iri, RDFS.subPropertyOf, parent_iri))
        
        # Add domain constraint if specified
        if cls._domain is not None:
            domain_iri = cls._domain._get_iri()
            g.add((prop_iri, RDFS.domain, domain_iri))
        
        # Add range constraint if specified
        if cls._range is not None:
            range_iri = cls._range._get_iri()
            g.add((prop_iri, RDFS.range, range_iri))
        
        return g.serialize(format='turtle')
    
class Node(Resource):
    pass

class NamedNode(Node):
    pass
