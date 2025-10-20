#!/usr/bin/env python3
"""Debug script to understand Space class structure"""

from src.semantic_objects.s223.entities import Space, PhysicalSpace
import sys

print("=" * 60)
print("DEBUG: Space class structure")
print("=" * 60)

print(f"\nSpace class: {Space}")
print(f"Space.__mro__: {Space.__mro__}")
print(f"\nHas __dataclass_fields__: {hasattr(Space, '__dataclass_fields__')}")

if hasattr(Space, '__dataclass_fields__'):
    print(f"\nSpace.__dataclass_fields__:")
    for field_name, field_obj in Space.__dataclass_fields__.items():
        print(f"  {field_name}: {field_obj}")
        print(f"    type: {field_obj.type}")
        print(f"    default: {field_obj.default}")
        print(f"    init: {field_obj.init}")
        print(f"    metadata: {field_obj.metadata}")

print(f"\n\nPhysicalSpace class: {PhysicalSpace}")
print(f"Has __dataclass_fields__: {hasattr(PhysicalSpace, '__dataclass_fields__')}")

if hasattr(PhysicalSpace, '__dataclass_fields__'):
    print(f"\nPhysicalSpace.__dataclass_fields__:")
    for field_name, field_obj in PhysicalSpace.__dataclass_fields__.items():
        print(f"  {field_name}: {field_obj}")
        print(f"    type: {field_obj.type}")
        print(f"    default: {field_obj.default}")
        print(f"    init: {field_obj.init}")
        print(f"    metadata: {field_obj.metadata}")

print("\n" + "=" * 60)
print("Checking module for DEFAULT_RELATIONS")
print("=" * 60)

for base in Space.__mro__:
    if hasattr(base, '__module__'):
        module = sys.modules.get(base.__module__)
        print(f"\nBase: {base.__name__}, Module: {base.__module__}")
        if module and hasattr(module, 'DEFAULT_RELATIONS'):
            print(f"  ✓ Has DEFAULT_RELATIONS: {module.DEFAULT_RELATIONS}")
        else:
            print(f"  ✗ No DEFAULT_RELATIONS")
