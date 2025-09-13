from typing import List, Dict, Tuple, Type, Union, get_origin
from dataclasses import dataclass, field
from semantic_mpc_interface.namespaces import * 
import yaml
from rdflib import Graph

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
    def _get_attributes(cls):
        attrs = {k: v for k, v in cls.__dict__.items()
            if not k.startswith('_') and not callable(v)}
        return attrs


    # # Legacy function 
    # def create_triples(annots, attrs, relations):
    #     triples = []
    #     for pred, objs in relations:
    #         if isinstance(objs,list):
    #             for obj in objs:
    #                 if obj in annots.keys():
    #                     triples.append((pred._get_iri(), PARAM[obj]))
    #                 elif obj in attrs.keys():
    #                     triples.append((pred._get_iri(), attrs[obj]._get_iri()))
    #                 else:
    #                     raise ValueError(f'{obj} not a good value')
    #         else:
    #             if objs in annots.keys():
    #                     triples.append((pred._get_iri(), PARAM[objs]))
    #             elif objs in attrs.keys():
    #                 triples.append((pred._get_iri(), attrs[objs]._get_iri()))
    #             else:
    #                 raise ValueError(f'{objs} not a good value')
    #     return triples

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
        """Get template dependencies based on annotations"""
        dependencies = []
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
    def generate_yaml_template(cls, template_name):
        """Generate complete YAML template"""
        template = {
            template_name: {
                'body': cls.generate_turtle_body(),
                'dependencies': cls.get_dependencies()
            }
        }
        
        # Add optional fields if they exist
        if hasattr(cls, '_optional'):
            template[template_name]['optional'] = cls._optional
        
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
    def validate_relations(cls):
        if not hasattr(cls, 'relations'):
            raise Exception('No relations defined')
        
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
        """
        cls.validate_relations()
        all_relations = []
        seen_relations = set()
        
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

class NamedNode(Resource):
    # A Named Node 
    pass
