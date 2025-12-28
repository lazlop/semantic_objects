#!/usr/bin/env python3
"""
Debug script to understand template generation
"""

from src.semantic_objects.s223.properties import EnvironmentalStation, PowerConsumption, AirPressure
from src.semantic_objects.s223.core import Node
from src.semantic_objects.s223.relations import hasProperty
import yaml

def debug_get_relations():
    print("=" * 60)
    print("Debug get_relations method")
    print("=" * 60)
    
    cls = EnvironmentalStation
    all_relations = []
    seen_relations = set()
    
    print("Processing dataclass fields...")
    
    # Get field-based relations from dataclass fields
    for base in reversed(cls.__mro__):
        if hasattr(base, '__dataclass_fields__'):
            print(f"\nProcessing base class: {base.__name__}")
            for field_name, field_obj in base.__dataclass_fields__.items():
                print(f"  Field: {field_name}")
                print(f"    Type: {field_obj.type}")
                print(f"    Init: {field_obj.init}")
                print(f"    Default: {field_obj.default}")
                print(f"    Metadata: {field_obj.metadata}")
                
                # Skip fields with init=False and templatize=False
                if (field_obj.init == False and 
                    field_obj.metadata.get('templatize', True) == False):
                    print(f"    -> SKIPPED: init=False and templatize=False")
                    continue
                
                # Skip fields that are part of inter-field relations (source fields with 'value' metadata)
                if field_obj.metadata.get('value') is not None:
                    print(f"    -> SKIPPED: has 'value' metadata (inter-field relation)")
                    continue
                
                # Skip fields with relation explicitly set to None
                if field_obj.metadata.get('relation') is None and 'relation' in field_obj.metadata:
                    print(f"    -> SKIPPED: relation explicitly set to None")
                    continue
                
                try:
                    relation = cls._infer_relation_for_field(field_name, field_obj)
                    print(f"    -> Inferred relation: {relation._name}")
                    
                    relation_key = (relation._name, field_name)
                    if relation_key not in seen_relations:
                        all_relations.append((relation, field_name))
                        seen_relations.add(relation_key)
                        print(f"    -> ADDED to relations")
                    else:
                        print(f"    -> SKIPPED: already seen")
                except Exception as e:
                    print(f"    -> ERROR inferring relation: {e}")
    
    print(f"\nFinal relations: {len(all_relations)}")
    for relation, field_name in all_relations:
        print(f"  {field_name}: {relation._name}")
    
    # Compare with actual get_relations result
    actual_relations = cls.get_relations()
    print(f"\nActual get_relations result: {len(actual_relations)}")
    for relation, field_name in actual_relations:
        print(f"  {field_name}: {relation._name}")

if __name__ == "__main__":
    debug_get_relations()