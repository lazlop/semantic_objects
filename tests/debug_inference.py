#!/usr/bin/env python3
"""Debug script to trace relation inference"""
import os 
import sys
sys.path.append('..')
from src.semantic_objects.s223.entities import Space
from semantic_objects.s223.properties import Area
import sys

print("=" * 60)
print("DEBUG: Tracing _infer_relation_for_field")
print("=" * 60)

# Get the field
field_obj = Space.__dataclass_fields__['area']
print(f"\nField: area")
print(f"Type: {field_obj.type}")
print(f"Type name: {field_obj.type.__name__}")

# Find DEFAULT_RELATIONS
default_relations = None
for base in Space.__mro__:
    if hasattr(base, '__module__'):
        module = sys.modules.get(base.__module__)
        if module and hasattr(module, 'DEFAULT_RELATIONS'):
            default_relations = module.DEFAULT_RELATIONS
            print(f"\nFound DEFAULT_RELATIONS in module: {base.__module__}")
            print(f"Registry: {default_relations}")
            break

print("\n" + "=" * 60)
print("Walking class hierarchies:")
print("=" * 60)

# Walk source hierarchy
print("\nSource class hierarchy (Space):")
for source_class in Space.__mro__:
    if hasattr(source_class, '__name__'):
        print(f"  {source_class.__name__}")

# Walk target hierarchy
print("\nTarget class hierarchy (Area):")
target_type = field_obj.type
for target_class in target_type.__mro__:
    if hasattr(target_class, '__name__'):
        print(f"  {target_class.__name__}")

print("\n" + "=" * 60)
print("Checking all combinations:")
print("=" * 60)

for source_class in Space.__mro__:
    if not hasattr(source_class, '__name__'):
        continue
    source_name = source_class.__name__
    
    for target_class in target_type.__mro__:
        if not hasattr(target_class, '__name__'):
            continue
        target_name = target_class.__name__
        
        key = (source_name, target_name)
        in_registry = key in default_relations
        print(f"  ({source_name}, {target_name}): {'✓ FOUND' if in_registry else '✗'}")
        
        if in_registry:
            print(f"    -> Relation: {default_relations[key]._local_name}")
