from typing import List, Dict, Tuple, Type, Union, Optional, get_origin, get_args, Self
from dataclasses import dataclass, field, fields, _MISSING_TYPE
from pathlib import Path

from rdflib import Graph, Literal, BNode, URIRef

from .namespaces import PARAM, RDF, RDFS, SH, bind_prefixes
from .query import SparqlQueryBuilder
from .fields import * 


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
    
    # Initialize _inter_field_relations if not present
    if '_inter_field_relations' not in cls.__dict__:
        cls._inter_field_relations = []
    
    return dataclass(cls)

@semantic_object
class Resource:
    templatize = True

    def __post_init__(self):
        """
        Automatically convert field values to their proper types.
        If a field expects a Resource subclass but receives a raw value,
        instantiate the Resource with that value.
        """
        if not hasattr(self.__class__, '__dataclass_fields__'):
            return
            
        for field_name, field_obj in self.__class__.__dataclass_fields__.items():
            # Skip fields that weren't initialized
            if not hasattr(self, field_name):
                continue
                
            current_value = getattr(self, field_name)
            
            # Skip if value is None or already the correct type
            if current_value is None:
                continue
                
            expected_type = field_obj.type
            
            # Handle Optional types
            origin = get_origin(expected_type)
            if origin is not None:
                args = get_args(expected_type)
                if args:
                    expected_type = args[0]
            
            # Skip if already the correct type
            if isinstance(current_value, expected_type):
                continue
            
            # If expected type is a Resource subclass and current value is not,
            # try to instantiate it
            if (isinstance(expected_type, type) and 
                issubclass(expected_type, Resource) and 
                not isinstance(current_value, Resource)):
                try:
                    # Try to instantiate with the current value
                    setattr(self, field_name, expected_type(current_value))
                except Exception:
                    # If instantiation fails, leave the value as-is
                    # This allows for more complex initialization patterns
                    pass

    @classmethod
    def _get_iri(cls):
        if not hasattr(cls, '_name'):
            if cls.abstract:
                raise Exception(f'Class {cls} is abstract, has no iri')
            raise Exception(f'Class {cls} must have _name attribute')
        return cls._ns[cls._name]
    
    @classmethod
    def _get_attributes(cls):
        attrs = {k: v for k, v in cls.__dict__.items()
            if not k.startswith('_')}
        return attrs

    @classmethod
    def _get_template_parameters(cls):
        seen_fields = set()
        parameters = {}

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
                    parameters[field_name] = field_obj

        return parameters

    @classmethod
    def _get_inter_field_relations(cls):
        """
        Get all inter-field relations defined for this class and its parents.
        Returns a list of inter-field relation dictionaries.
        """
        all_relations = []
        seen_relations = set()
        
        for base in reversed(cls.__mro__):
            if hasattr(base, '_inter_field_relations'):
                for rel in base._inter_field_relations:
                    # Create a unique key for this relation
                    rel_key = (rel['source_field'], rel['relation']._name if hasattr(rel['relation'], '_name') else str(rel['relation']), rel['target_field'])
                    if rel_key not in seen_relations:
                        all_relations.append(rel)
                        seen_relations.add(rel_key)
        
        return all_relations

    @classmethod
    def get_dependencies(cls):
        """Get template dependencies based on annotations and field metadata"""
        dependencies = []
        
        # Check if this is a dataclass with fields
        if hasattr(cls, '__dataclass_fields__'):
            for field_name, field_obj in cls.__dataclass_fields__.items():
                # Skip fields that are targets of inter-field relations (they're not separate dependencies)
                target_field_name = field_obj.metadata.get('value')
                if target_field_name is not None:
                    # This field is a source in an inter-field relation, skip it
                    continue
                
                annotation_type = field_obj.type
                
                # Handle Optional types - extract the actual type
                origin = get_origin(annotation_type)
                if origin is not None:
                    args = get_args(annotation_type)
                    if args:
                        annotation_type = args[0]
                
                # Skip if not a class type
                if not isinstance(annotation_type, type):
                    continue

                if not issubclass(annotation_type, Resource):
                    continue

                if annotation_type.templatize == False:
                    continue
                # Skip if field has init=False and templatize=False
                if (field_obj.init == False and 
                    field_obj.metadata.get('templatize', True) == False):
                    continue

                if not isinstance(field_obj.default,_MISSING_TYPE):
                    continue

                dependencies.append({
                    'template': annotation_type,
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
                    
                    # Skip fields that are part of inter-field relations (source fields with 'value' metadata)
                    if field_obj.metadata.get('value') is not None:
                        continue
                    
                    # Skip fields with relation explicitly set to None
                    if field_obj.metadata.get('relation') is None and 'relation' in field_obj.metadata:
                        continue
                    
                    relation = cls._infer_relation_for_field(field_name, field_obj)
                    
                    relation_key = (relation._name, field_name)
                    if relation_key not in seen_relations:
                        all_relations.append((relation, field_name))
                        seen_relations.add(relation_key)
        
        # Add inter-field relations
        inter_field_rels = cls._get_inter_field_relations()
        for rel in inter_field_rels:
            relation = rel['relation']
            source_field = rel['source_field']
            
            relation_key = (relation._name, source_field)
            if relation_key not in seen_relations:
                all_relations.append((relation, source_field))
                seen_relations.add(relation_key)
        
        return all_relations

    @classmethod
    def get_related_classes(cls, get_recursive=True, include_abstract=False):
        """
        Get related classes for this class, categorized by type.
        
        This method works correctly regardless of how the class or this module is imported,
        because it uses the actual class hierarchy (MRO) to determine class types rather
        than comparing against hardcoded class references.
        
        Args:
            get_recursive: If True, recursively find all related classes. If False, only
                          find classes directly referenced by this class.
            include_abstract: If True, include abstract classes in the results.
        
        Returns:
            Tuple of (predicate_list, entity_list, value_list) where each list contains
            classes of that type found in the class hierarchy.
        """
        # Helper function to check if a class is a subclass of a base by name
        def _is_subclass_of_name(klass, base_name):
            """Check if klass is a subclass of a class with the given name."""
            if not isinstance(klass, type):
                return False
            for base in klass.__mro__:
                if base.__name__ == base_name:
                    return True
            return False
        
        # Collect all related classes
        relations = [relation for relation, field_name in cls.get_relations()]
        entities_and_values = [field.type for entity, field in cls.__dataclass_fields__.items()]
        all_classes = [cls] + relations + entities_and_values
        all_classes = list(set(all_classes))

        if get_recursive:
            new_classes = all_classes.copy()
            for i in range(100):
                next_new_classes = []
                for klass in new_classes:
                    # Skip if not a class (e.g., Optional[X], float, etc.)
                    if not isinstance(klass, type):
                        continue
                    # Skip if not a Resource subclass
                    if not _is_subclass_of_name(klass, 'Resource'):
                        continue
                    
                    # Get relations and fields from this class
                    relations = [relation for relation, field_name in klass.get_relations()]
                    entities_and_values = [field.type for entity, field in klass.__dataclass_fields__.items()]
                    next_classes = relations + entities_and_values
                    
                    # Add new classes we haven't seen yet
                    for next_class in next_classes:
                        if next_class not in all_classes:
                            next_new_classes.append(next_class)
                            all_classes.append(next_class)
                
                if not next_new_classes:
                    break
                new_classes = next_new_classes
                
                if i == 99:
                    raise RecursionError("Max depth reached")
        
        # Categorize classes by type using name-based checks
        predicate_lst, entity_lst, value_lst = [], [], []
        
        for klass in all_classes:
            # Skip if not a class type
            if not isinstance(klass, type):
                continue
            
            # Skip if not a Resource subclass
            if not _is_subclass_of_name(klass, 'Resource'):
                continue
            
            # Skip abstract classes if requested
            if not include_abstract and hasattr(klass, 'abstract') and klass.abstract:
                continue
            
            # Categorize by checking class hierarchy
            if _is_subclass_of_name(klass, 'Predicate'):
                predicate_lst.append(klass)
            elif _is_subclass_of_name(klass, 'Node'):
                entity_lst.append(klass)
        
        return predicate_lst, entity_lst

    @classmethod
    def get_sparql_query(cls, ontology=None):
        """
        Convenience method to generate a SPARQL query from the class definition.
        Delegates to SparqlQueryBuilder.
        
        Args:
            ontology: Optional ontology identifier (e.g., 's223') for special handling
            
        Returns:
            A SPARQL query string that can be used to query for instances of this class
        """
        builder = SparqlQueryBuilder(cls)
        return builder.get_sparql_query(ontology)
    
    def _get_evaluation_dict(self):
        parameters = self._get_template_parameters()
        evaluation_dict = {}
        for field_name, field_obj in parameters.items():
            if not isinstance(field_obj.default, _MISSING_TYPE):
                evaluation_dict[field_name] = field_obj.default
            else:
                evaluation_dict[field_name] = None
        return evaluation_dict
        
    def get_field_values(self, recursive=False, _visited=None, _prefix = ""):
        """
        Get field values for this instance. For now doing in buildingmotif template form
        
        Args:
            recursive: If True, recursively get field values for all related Resource objects.
                      If False (default), only get field values for this instance.
            _visited: Internal parameter to track visited objects and prevent infinite recursion.
        
        Returns:
            Dictionary of field names to values. When recursive=True, Resource field values
            are replaced with their nested field value dictionaries.
        """
        # Initialize visited set for tracking circular references
        if _visited is None:
            _visited = set()
        
        # Use object id to track visited instances
        obj_id = id(self)
        if obj_id in _visited:
            # Return a reference marker to indicate circular reference
            return {'_circular_ref': True, '_name': getattr(self, '_name', self.__class__.__name__)}
        
        # Mark this object as visited
        _visited.add(obj_id)

        field_values = {}
        field_values['_name'] = getattr(self, '_name', self.__class__.__name__)
        for field_name, field_obj in self.__class__.__dataclass_fields__.items():
            field_value = getattr(self, field_name)
            if isinstance(field_value, type):
                if issubclass(field_value, NamedNode):
                    field_values[field_name] = field_value._get_iri()
            elif isinstance(field_value, Resource):
                if recursive:
                    # Recursively get field values for Resource instances
                    field_values[field_name] = {
                        '_name': field_value._name,
                        '_type': field_value.__class__.__name__,
                        **field_value.get_field_values(recursive=True, _visited=_visited)
                    }
                else:
                    field_values[field_name] = field_value._name
            else:
                field_values[field_name] = field_value
        
        return field_values

    # Methods that use exporters (import and delegate)
    @classmethod
    def generate_turtle_body(cls, subject_name="name"):
        """Generate RDF/Turtle body for template"""
        from .exporters import YamlExporter
        return YamlExporter.generate_turtle_body(cls, subject_name)
    
    @classmethod
    def generate_yaml_template(cls, template_name=None):
        """Generate complete YAML template"""
        from .exporters import YamlExporter
        return YamlExporter.generate_yaml_template(cls, template_name)
    
    @classmethod
    def to_yaml(cls, template_name=None, file_path: Path = None):
        """Convert to YAML string"""
        from .exporters import YamlExporter
        return YamlExporter.to_yaml(cls, template_name, file_path)
    
    @classmethod
    def _create_qualified_value_shape(cls, g, prop_node, field_obj, field_name, class_iri):
        """Create a qualified value shape for a field"""
        from .exporters import RdfExporter
        return RdfExporter._create_qualified_value_shape(cls, g, prop_node, field_obj, field_name, class_iri)
    
    @classmethod
    def generate_rdf_class_definition(cls, include_hierarchy=False):
        """Generate RDF class definition with SHACL constraints"""
        from .exporters import RdfExporter
        return RdfExporter.generate_rdf_class_definition(cls, include_hierarchy)


class Predicate(Resource):
    _subproperty_of = None
    _domain = None
    _range = None
    
    @classmethod
    def generate_turtle_body(cls, subject_name="name", target_name="target"):
        """Generate RDF/Turtle body for template"""
        from .exporters import YamlExporter
        return YamlExporter.generate_predicate_turtle_body(cls, subject_name, target_name)
    
    @classmethod
    def generate_rdf_property_definition(cls):
        """Generate RDF property definition with subproperty and domain/range constraints"""
        from .exporters import RdfExporter
        return RdfExporter.generate_rdf_property_definition(cls)


class Node(Resource):
    _name: Optional[str] = field(default=None, init=True, metadata={'templatize': False})
    _instance_counter = {}
    
    def __post_init__(self):
        """Auto-generate _name if not provided"""
        super().__post_init__()
        
        if self._name is None or self._name == self.__class__.__name__:
            class_name = self.__class__.__name__
            
            if class_name not in Node._instance_counter:
                Node._instance_counter[class_name] = 0
            
            Node._instance_counter[class_name] += 1
            self._name = f"{class_name}_{Node._instance_counter[class_name]}"


class NamedNode(Node):
    templatize = False