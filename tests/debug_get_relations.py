#!/usr/bin/env python3
"""Debug script to trace get_relations execution"""
import os 
import sys
sys.path.append('..')
from src.semantic_objects.s223.entities import Space
from semantic_objects.s223.properties import Area

print("=" * 60)
print("DEBUG: Tracing get_relations() for Space")
print("=" * 60)

print(f"\nArea class MRO: {Area.__mro__}")
print(f"Area class name: {Area.__name__}")

# Manually trace through get_relations logic
print("\n" + "=" * 60)
print("Manual trace of get_relations logic:")
print("=" * 60)

all_relations = []
seen_relations = set()

for base in reversed(Space.__mro__):
    print(f"\nChecking base: {base.__name__}")
    if hasattr(base, '__dataclass_fields__'):
        print(f"  Has __dataclass_fields__")
        for field_name, field_obj in base.__dataclass_fields__.items():
            print(f"  Field: {field_name}")
            print(f"    init: {field_obj.init}")
            print(f"    templatize: {field_obj.metadata.get('templatize', True)}")
            
            # Skip fields with init=False and templatize=False
            if (field_obj.init == False and 
                field_obj.metadata.get('templatize', True) == False):
                print(f"    -> SKIPPED (init=False and templatize=False)")
                continue
            
            print(f"    -> Processing field")
            
            # Try to infer relation
            try:
                relation = Space._infer_relation_for_field(field_name, field_obj)
                print(f"    -> Inferred relation: {relation._local_name if relation else None}")
                
                if relation:
                    relation_key = (relation._local_name, field_name)
                    if relation_key not in seen_relations:
                        all_relations.append((relation, field_name))
                        seen_relations.add(relation_key)
                        print(f"    -> ADDED to relations")
                    else:
                        print(f"    -> Already seen, skipped")
            except ValueError as e:
                print(f"    -> ERROR: {e}")
                continue

print("\n" + "=" * 60)
print(f"Final relations: {all_relations}")
print("=" * 60)

print("\n" + "=" * 60)
print("Calling Space.get_relations():")
print("=" * 60)
relations = Space.get_relations()
print(f"Result: {relations}")
