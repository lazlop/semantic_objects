from typing import List, Dict, Tuple, Type, Union, get_origin
from dataclasses import dataclass, field
from semantic_mpc_interface.namespaces import * 
import yaml

def get_namespace_prefixes():
    """Get standard namespace prefixes for RDF templates"""
    return {
        'p': '<urn:___param___#>',
        'brick': '<https://brickschema.org/schema/Brick#>',
        's223': '<http://data.ashrae.org/standard223#>',
        'qudt': '<http://qudt.org/schema/qudt/>',
        'quantitykind': '<http://qudt.org/vocab/quantitykind/>',
        'unit': '<http://qudt.org/vocab/unit/>',
        'hpf': '<urn:hpflex#>'
    }

def create_turtle_triples(annots, attrs, relations, subject_name="name"):
    """Create RDF/Turtle triples from relations"""
    triples = []
    
    for pred, objs in relations:
        if isinstance(objs, list):
            for obj in objs:
                if obj in annots.keys():
                    triples.append(f"        s223:{pred._iri} p:{obj}")
                elif obj in attrs.keys():
                    # Handle special cases for different attribute types
                    attr_value = attrs[obj]
                    if hasattr(attr_value, '_iri'):
                        triples.append(f"        s223:{pred._iri} {attr_value}")
                    else:
                        triples.append(f"        s223:{pred._iri} {attr_value}")
                else:
                    raise ValueError(f'{obj} not a good value')
        else:
            if objs in annots.keys():
                triples.append(f"        s223:{pred._iri} p:{objs}")
            elif objs in attrs.keys():
                attr_value = attrs[objs]
                if hasattr(attr_value, '_iri'):
                    triples.append(f"        s223:{pred._iri} {attr_value}")
                else:
                    triples.append(f"        s223:{pred._iri} {attr_value}")
            else:
                raise ValueError(f'{objs} not a good value')
    
    return triples

# Legacy function for backward compatibility
def create_triples(annots, attrs, relations):
    triples = []
    for pred, objs in relations:
        if isinstance(objs,list):
            for obj in objs:
                if obj in annots.keys():
                    triples.append((pred._get_iri(), PARAM[obj]))
                elif obj in attrs.keys():
                    triples.append((pred._get_iri(), attrs[obj]._get_iri()))
                else:
                    raise ValueError(f'{obj} not a good value')
        else:
            if objs in annots.keys():
                    triples.append((pred._get_iri(), PARAM[objs]))
            elif objs in attrs.keys():
                triples.append((pred._get_iri(), attrs[objs]._get_iri()))
            else:
                raise ValueError(f'{objs} not a good value')
    return triples

@dataclass
class Resource:

    relations = []

    @classmethod
    def _get_iri(cls):
        return cls._ns[cls._iri]
    
    @classmethod
    def _get_attributes(cls):
        attrs = {k: v for k, v in cls.__dict__.items()
            if not k.startswith('_') and not callable(v)}
        return attrs

    @classmethod
    def template_body_from_anotations(cls):
        # drafing code for class method
        if cls.relations == []:
            raise Exception('No triples to make')
        relations = cls.get_relations()
        triples = []
        triples += create_triples(cls.__annotations__,
                                  cls._get_attributes(),
                                  relations)
        return triples

    @classmethod
    def generate_turtle_body(cls, subject_name="name"):
        """Generate RDF/Turtle body for template"""
        if not hasattr(cls, '_iri'):
            raise Exception('Class must have _iri attribute')
        
        relations = cls.get_relations()
        prefixes = get_namespace_prefixes()
        
        # Generate prefix declarations
        prefix_lines = []
        for prefix, uri in prefixes.items():
            prefix_lines.append(f"    @prefix {prefix}: {uri} .")
        
        # Generate the main subject declaration
        main_line = f"    p:{subject_name} a s223:{cls._iri}"
        
        # Generate property triples
        property_lines = []
        for pred, objs in relations:
            if isinstance(objs, list):
                for obj in objs:
                    if obj in cls.__annotations__.keys():
                        property_lines.append(f"        s223:{pred._iri} p:{obj}")
                    elif obj in cls._get_attributes().keys():
                        attr_value = cls._get_attributes()[obj]
                        if hasattr(attr_value, '__name__'):
                            # Handle namespace references like QK['Area']
                            property_lines.append(f"        qudt:{pred._iri} {attr_value}")
                        else:
                            property_lines.append(f"        s223:{pred._iri} {attr_value}")
            else:
                if objs in cls.__annotations__.keys():
                    property_lines.append(f"        s223:{pred._iri} p:{objs}")
                elif objs in cls._get_attributes().keys():
                    attr_value = cls._get_attributes()[objs]
                    if hasattr(attr_value, '__name__'):
                        property_lines.append(f"        qudt:{pred._iri} {attr_value}")
                    else:
                        property_lines.append(f"        s223:{pred._iri} {attr_value}")
        
        # Combine all lines
        body_lines = prefix_lines + [main_line]
        if property_lines:
            body_lines[-1] += " ;"  # Add semicolon to main line
            body_lines.extend(property_lines[:-1])  # Add all but last property line
            body_lines.append(property_lines[-1] + " .")  # Add period to last line
        else:
            body_lines[-1] += " ."  # Add period to main line
        
        return "\n".join(body_lines)

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
    def generate_yaml_template(cls, template_name=None):
        """Generate complete YAML template"""
        if template_name is None:
            template_name = cls.__name__.lower()
        
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
        template = cls.generate_yaml_template(template_name)
        return yaml.dump(template, default_flow_style=False, sort_keys=False)

    @classmethod
    def validate_relations(cls):
        if not hasattr(cls, 'relations'):
            raise Exception('No relations defined')
        objects = cls.relations[0][1]
                
        if isinstance(objects,str):
            objects = [objects]
        if not isinstance(objects,list):
            raise TypeError(f'{objects=} must be a list or str')
        
        for obj in list(objects):
            non_relation_attributes = [k for k in cls._get_attributes().keys() if k != 'relations']
            if obj not in list(cls.__annotations__.keys()) \
                + non_relation_attributes:
                raise ValueError(f'{obj} must be an existing attribute or annotation')          
            
    @classmethod
    def get_relations(cls):
        """
        Accumulate relations from all bases up the MRO (excluding 'object').
        """
        cls.validate_relations()
        all_relations = []
        for base in reversed(cls.__mro__):
            if hasattr(base, 'relations'):
                relations = getattr(base, 'relations')
                if relations == []:
                    continue
                all_relations += relations  
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
