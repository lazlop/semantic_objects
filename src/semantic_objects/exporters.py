from typing import get_origin, get_args, List, Type
from dataclasses import _MISSING_TYPE
from .namespaces import PARAM, RDF, RDFS, SH, bind_prefixes
import yaml
from pathlib import Path
from rdflib import Graph, Literal, BNode, URIRef
from .discovery import get_related_classes


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

class FoldedString(str):
    """Custom string class for YAML folded scalar representation"""
    pass


def folded_string_representer(dumper, data):
    """Custom YAML representer for folded strings"""
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='>')


# Register the custom representer
yaml.add_representer(FoldedString, folded_string_representer)


class YamlExporter:
    """Handles all YAML export functionality for Resource classes"""
    
    @staticmethod
    def generate_turtle_body(cls, subject_name="name"):
        """Generate RDF/Turtle body for template"""
        g = Graph()
        bind_prefixes(g)
        
        g.add((PARAM['name'], RDF.type, cls._get_iri()))
        
        parameters = cls._get_template_parameters()
        for field_name, field_obj in parameters.items():
            # Check if this field has a 'value' metadata pointing to another field
            target_field_name = field_obj.metadata.get('value')
            if target_field_name is not None:
                # This is an inter-field relation - skip it here, handle separately
                continue
            
            # Check if relation is explicitly set to None (skip main entity relation)
            if field_obj.metadata.get('relation') is None and 'relation' in field_obj.metadata:
                # Relation explicitly set to None - skip creating main entity relation
                continue
                
            relation = cls._infer_relation_for_field(field_name, field_obj)
            if not isinstance(field_obj.default, _MISSING_TYPE) and field_obj.default is not None:
                g.add((PARAM['name'], relation._get_iri(), field_obj.default._get_iri()))
            else:
                g.add((PARAM['name'], relation._get_iri(), PARAM[field_name]))
        
        # Handle inter-field relations
        inter_field_rels = cls._get_inter_field_relations()
        for rel in inter_field_rels:
            source_field = rel['source_field']
            target_field = rel['target_field']
            relation = rel['relation']
            
            g.add((PARAM[source_field], relation._get_iri(), PARAM[target_field]))
            
        return g.serialize(format='ttl')
    
    @staticmethod
    def generate_predicate_turtle_body(cls, subject_name="name", target_name="target"):
        """Generate RDF/Turtle body for Predicate template"""
        g = Graph()
        bind_prefixes(g)
        
        prop_iri = cls._get_iri()
        
        g.add((PARAM[subject_name], prop_iri, PARAM[target_name]))

        if cls._domain is not None:
            domain_iri = cls._domain._get_iri()
            g.add((prop_iri, RDFS.domain, domain_iri))
        
        if cls._range is not None:
            range_iri = cls._range._get_iri()
            g.add((prop_iri, RDFS.range, range_iri))
        
        return g.serialize(format='ttl')
    
    @staticmethod
    def generate_yaml_template(cls, template_name=None):
        """Generate complete YAML template"""
        if template_name is None:
            template_name = cls.__name__
            
        bmotif_format_dependencies = [
            {'template': v['template'].__name__,
             'args': v['args']}
            for v in cls.get_dependencies()
        ]
        
        template = {
            template_name: {
                'body': YamlExporter.generate_turtle_body(cls),
                'dependencies': bmotif_format_dependencies
            }
        }

        # Add optional fields if they exist
        optional_fields = cls.get_optional_fields()
        if optional_fields:
            if len(optional_fields) == 1:
                template[template_name]['optional'] = optional_fields[0]
            else:
                template[template_name]['optional'] = optional_fields
        
        return template
    
    @staticmethod
    def to_yaml(cls, template_name=None, file_path: Path = None):
        """Convert to YAML string"""
        if template_name is None:
            template_name = cls.__name__
        
        template = YamlExporter.generate_yaml_template(cls, template_name)
        template[template_name]['body'] = FoldedString(template[template_name]['body'])
        
        if file_path is not None:
            with open(file_path, 'a') as f:
                yaml.dump(template, f, explicit_end=False)
        
        return yaml.dump(template, explicit_end=False)


class RdfExporter:
    """Handles all RDF export functionality for Resource classes"""
    
    @staticmethod
    def _create_qualified_value_shape(cls, g, prop_node, field_obj, field_name, class_iri):
        """Create a qualified value shape for a field"""
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
        
        add_qual_val_shape = True
        
        # Check if this is a literal type
        if isinstance(field_obj.default, Literal) if hasattr(field_obj, 'default') else False:
            g.add((qual_val_shape, SH.hasValue, field_obj.default))
        # Check if target is a Resource subclass
        elif hasattr(target_type, '_get_iri'):
            g.add((qual_val_shape, SH['class'], target_type._get_iri()))
        # For other types, use hasValue if a default is provided
        elif hasattr(field_obj, 'default') and field_obj.default is not None:
            g.add((qual_val_shape, SH.hasValue, field_obj.default))
        else:
            add_qual_val_shape = False
        
        if add_qual_val_shape:
            label = field_obj.metadata.get('label', field_name)
            g.add((qual_val_shape, RDFS.label, Literal(label)))
            g.add((prop_node, SH.qualifiedMinCount, Literal(1)))
            g.add((prop_node, SH.qualifiedValueShape, qual_val_shape))
            g.add((qual_val_shape, RDF.type, SH.NodeShape))
    
    @staticmethod
    def generate_rdf_class_definition(cls, include_hierarchy=False):
        """Generate RDF class definition with SHACL constraints"""
        from .core import Resource  # Import here to avoid circular dependency
        
        g = Graph()
        bind_prefixes(g)
        
        class_iri = cls._get_iri()
        g.add((class_iri, RDF.type, cls._ns['Class']))
        for type in cls._other_types:
            g.add((class_iri, RDF.type, type))
        
        if hasattr(cls, 'comment'):
            g.add((class_iri, RDFS.comment, Literal(cls.comment)))
        
        if hasattr(cls, 'label'):
            g.add((class_iri, RDFS.label, Literal(cls.label)))
        
        # Add subclass relationship
        for base in cls.__mro__[1:]:
            if (hasattr(base, '_name') and hasattr(base, '_ns') and 
                base != Resource and base._name != cls._name and
                base.__name__ not in ['Node', 'Value', 'Predicate', 'NamedNode']):
                parent_iri = base._ns[base._name]
                g.add((class_iri, RDFS.subClassOf, parent_iri))
                break
        
        shape_path_name_dct = {}
        prop_counts = {}
        processed_relations = set()

        if hasattr(cls, '__dataclass_fields__'):
            if include_hierarchy:
                fields_to_process = cls.__dataclass_fields__.items()
            else:
                parent_fields = set()
                for base in cls.__mro__[1:]:
                    if hasattr(base, '__dataclass_fields__'):
                        parent_fields.update(base.__dataclass_fields__.values())
                
                fields_to_process = [
                    (name, field_obj) 
                    for name, field_obj in cls.__dataclass_fields__.items()
                    if field_obj not in parent_fields
                ]
            
            # First pass: count properties and create property shapes
            for field_name, field_obj in fields_to_process:
                if field_obj.metadata.get('value') is not None:
                    continue
                
                relation = cls._infer_relation_for_field(field_name, field_obj)
                if relation is None:
                    continue
                
                relation_iri = relation._get_iri()
                
                if relation_iri in prop_counts:
                    prop_counts[relation_iri] += 1
                else:
                    prop_counts[relation_iri] = 1
                
                if relation_iri in shape_path_name_dct:
                    continue
                
                relation_key = relation._name
                if relation_key in processed_relations:
                    continue
                processed_relations.add(relation_key)
                
                prop_node = BNode()
                g.add((class_iri, SH.property, prop_node))
                g.add((prop_node, RDF.type, SH.PropertyShape))
                g.add((prop_node, SH.path, relation_iri))
                
                shape_path_name_dct[relation_iri] = prop_node
                
                field_comment = field_obj.metadata.get('comment')
                target_class_name = None
                
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
                
                if hasattr(field_obj, 'default'):
                    target_class = field_obj.type._get_iri()
                    g.add((prop_node, SH['value'], target_class))
                elif hasattr(field_obj, 'type'):
                    target_class = field_obj.type._get_iri()
                    g.add((prop_node, SH['class'], target_class))
                    
                    message = f"s223: If the relation `{relation._name}` is present it must associate the `{cls.__name__}` with a `{target_class_name}`."
                    g.add((prop_node, SH.message, Literal(message)))
            
            # Second pass: create qualified value shapes
            for field_name, field_obj in fields_to_process:
                if field_obj.metadata.get('value') is not None:
                    continue
                
                relation = cls._infer_relation_for_field(field_name, field_obj)
                if relation is None:
                    continue
                
                relation_iri = relation._get_iri()
                
                if relation_iri not in shape_path_name_dct:
                    continue
                
                prop_node = shape_path_name_dct[relation_iri]
                
                if field_obj.metadata.get('qualified', True):
                    RdfExporter._create_qualified_value_shape(cls, g, prop_node, field_obj, field_name, class_iri)
            
            # Add minCount/maxCount
            for relation_iri, count in prop_counts.items():
                if relation_iri in shape_path_name_dct:
                    prop_node = shape_path_name_dct[relation_iri]
                    g.add((prop_node, SH.minCount, Literal(count)))
                    
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
        
        # Add constraints from _valid_relations
        if include_hierarchy:
            classes_to_process = cls.__mro__
        else:
            classes_to_process = []
            if '_valid_relations' in cls.__dict__:
                classes_to_process = [cls]
        
        for base_class in classes_to_process:
            if not hasattr(base_class, '_valid_relations'):
                continue
            
            for relation, target_class in base_class._valid_relations:
                relation_key = relation._name
                if relation_key in processed_relations:
                    continue
                processed_relations.add(relation_key)
                
                relation_iri = relation._get_iri()
                
                prop_node = BNode()
                g.add((class_iri, SH.property, prop_node))
                g.add((prop_node, RDF.type, SH.PropertyShape))
                g.add((prop_node, SH.path, relation_iri))
                
                if target_class is None:
                    target_class_name = "None"
                elif target_class.__name__ == 'Self' or str(target_class) == 'Self':
                    target_class_name = cls.__name__
                    target_class = cls
                elif hasattr(target_class, '__name__'):
                    target_class_name = target_class.__name__
                else:
                    target_class_name = str(target_class)
                
                field_comment = f"If the relation `{relation._name}` is present it must associate the `{cls.__name__}` with a `{target_class_name}`."
                g.add((prop_node, RDFS.comment, Literal(field_comment)))
                
                if hasattr(target_class, '_get_iri'):
                    target_class_iri = target_class._get_iri()
                    g.add((prop_node, SH['class'], target_class_iri))
                    
                    message = f"s223: If the relation `{relation._name}` is present it must associate the `{cls.__name__}` with a `{target_class_name}`."
                    g.add((prop_node, SH.message, Literal(message)))
        
        return g.serialize(format='turtle')
    
    @staticmethod
    def generate_rdf_property_definition(cls):
        """Generate RDF property definition with subproperty and domain/range constraints"""
        g = Graph()
        bind_prefixes(g)
        
        prop_iri = cls._get_iri()
        
        g.add((prop_iri, RDF.type, RDF.Property))
        
        if hasattr(cls, 'label'):
            g.add((prop_iri, RDFS.label, Literal(cls.label)))
        
        if hasattr(cls, 'comment'):
            g.add((prop_iri, RDFS.comment, Literal(cls.comment)))
        
        if cls._subproperty_of is not None:
            parent_iri = cls._subproperty_of._get_iri()
            g.add((prop_iri, RDFS.subPropertyOf, parent_iri))
        
        if cls._domain is not None:
            domain_iri = cls._domain._get_iri()
            g.add((prop_iri, RDFS.domain, domain_iri))
        
        if cls._range is not None:
            range_iri = cls._range._get_iri()
            g.add((prop_iri, RDFS.range, range_iri))
        
        return g.serialize(format='turtle')