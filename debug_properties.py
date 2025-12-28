#!/usr/bin/env python3
"""
Debug script to understand property template generation
"""

from src.semantic_objects.s223.properties import PowerConsumption, AirPressure, QuantifiableObservableProperty
from src.semantic_objects.build_model import BMotifSession
import yaml

def debug_power_consumption_template():
    print("=" * 60)
    print("Debug PowerConsumption Template Generation")
    print("=" * 60)
    
    cls = PowerConsumption
    
    # Check template parameters
    params = cls._get_template_parameters()
    print("Template parameters:")
    for field_name, field_obj in params.items():
        print(f"  {field_name}: {field_obj.type}")
        print(f"    Init: {field_obj.init}")
        print(f"    Default: {field_obj.default}")
        print(f"    Metadata: {field_obj.metadata}")
    
    # Check relations
    relations = cls.get_relations()
    print(f"\nRelations:")
    for relation, field_name in relations:
        print(f"  {field_name}: {relation._name}")
    
    # Check dataclass fields
    fields = cls.__dataclass_fields__
    print(f"\nDataclass fields:")
    for field_name, field_obj in fields.items():
        print(f"  {field_name}: {field_obj.type}")
        print(f"    Init: {field_obj.init}")
        print(f"    Default: {field_obj.default}")
        print(f"    Metadata: {field_obj.metadata}")
    
    # Generate turtle body step by step
    print(f"\nGenerating turtle body step by step:")
    
    from rdflib import Graph
    from src.semantic_objects.namespaces import PARAM, bind_prefixes
    from dataclasses import _MISSING_TYPE
    
    g = Graph()
    bind_prefixes(g)
    
    from src.semantic_objects.namespaces import RDF
    g.add((PARAM['name'], RDF.type, cls._get_iri()))
    
    parameters = cls._get_template_parameters()
    for field_name, field_obj in parameters.items():
        print(f"\n  Processing field: {field_name}")
        
        # Check if this field has a 'value' metadata pointing to another field
        target_field_name = field_obj.metadata.get('value')
        if target_field_name is not None:
            print(f"    -> SKIPPED: inter-field relation")
            continue
        
        # Check if relation is explicitly set to None (skip main entity relation)
        if field_obj.metadata.get('relation') is None and 'relation' in field_obj.metadata:
            print(f"    -> SKIPPED: relation explicitly set to None")
            continue
            
        relation = cls._infer_relation_for_field(field_name, field_obj)
        print(f"    -> Relation: {relation._name}")
        
        if not isinstance(field_obj.default, _MISSING_TYPE) and field_obj.default is not None:
            print(f"    -> Using fixed value: {field_obj.default}")
            if hasattr(field_obj.default, '_get_iri'):
                iri = field_obj.default._get_iri()
                print(f"    -> IRI: {iri}")
                g.add((PARAM['name'], relation._get_iri(), iri))
            else:
                print(f"    -> No _get_iri method on {field_obj.default}")
        else:
            print(f"    -> Using parameter: P:{field_name}")
            g.add((PARAM['name'], relation._get_iri(), PARAM[field_name]))
    
    print(f"\nFinal turtle:")
    print(g.serialize(format='ttl'))

if __name__ == "__main__":
    debug_power_consumption_template()