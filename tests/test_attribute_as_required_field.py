"""
Test that class attributes are interpreted as required_field with default values.
This tests the fix for the semantic_object decorator.
"""
import os 
import sys
sys.path.append('..')

from src.semantic_objects.s223.properties import Area, QuantifiableObervableProperty
from src.semantic_objects.qudt import quantitykinds
from dataclasses import fields

def test_area_qk_field():
    """Test that Area.qk is converted to a required_field with quantitykinds.Area as default"""
    
    # Get the dataclass fields for Area
    area_fields = {f.name: f for f in fields(Area)}
    
    # Check that qk field exists
    assert 'qk' in area_fields, "qk field should exist in Area"
    
    qk_field = area_fields['qk']
    
    # Check that it has a default value
    print(f"qk field default: {qk_field.default}")
    print(f"qk field default_factory: {qk_field.default_factory}")
    print(f"qk field metadata: {qk_field.metadata}")
    
    # The default should be quantitykinds.Area
    assert qk_field.default == quantitykinds.Area, \
        f"Expected default to be quantitykinds.Area, got {qk_field.default}"
    
    # Check that metadata indicates it's a required field
    assert 'min' in qk_field.metadata, "Field should have 'min' in metadata (from required_field)"
    assert qk_field.metadata.get('min') == 1, "Field should have min=1"
    
    # Check that qualified is set correctly
    assert 'qualified' in qk_field.metadata, "Field should have 'qualified' in metadata"
    assert qk_field.metadata.get('qualified') == False, \
        f"Field should have qualified=False (inherited from parent), got {qk_field.metadata.get('qualified')}"
    
    print("✓ Area.qk is correctly interpreted as a required_field with quantitykinds.Area as default")
    print(f"  - Default value: {qk_field.default}")
    print(f"  - Metadata: {qk_field.metadata}")

def test_parent_field_metadata_preserved():
    """Test that parent field metadata is preserved when overriding with a value"""
    
    # Get the parent class field
    parent_fields = {f.name: f for f in fields(QuantifiableObervableProperty)}
    parent_qk_field = parent_fields['qk']
    
    print(f"\nParent qk field metadata: {parent_qk_field.metadata}")
    print(f"Parent qk field qualified: {parent_qk_field.metadata.get('qualified')}")
    
    # Get the child class field
    area_fields = {f.name: f for f in fields(Area)}
    area_qk_field = area_fields['qk']
    
    print(f"Area qk field metadata: {area_qk_field.metadata}")
    print(f"Area qk field qualified: {area_qk_field.metadata.get('qualified')}")
    
    # The qualified metadata should be preserved from parent
    assert area_qk_field.metadata.get('qualified') == parent_qk_field.metadata.get('qualified'), \
        "Metadata from parent field should be preserved"
    
    print("✓ Parent field metadata is correctly preserved")

if __name__ == "__main__":
    test_area_qk_field()
    test_parent_field_metadata_preserved()
    print("\n✅ All tests passed!")
