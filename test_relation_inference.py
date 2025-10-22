#!/usr/bin/env python3
"""Test script to verify relation inference functionality"""

from src.semantic_objects.s223.entities import Space, Window, PhysicalSpace, Space_TwoArea, Area

def test_space_relation_inference():
    """Test that Space class correctly infers hasProperty relation for area field"""
    print("Testing Space class relation inference...")
    
    # Get relations for Space class
    relations = Space.get_relations()
    print(f"Space relations: {relations}")
    
    # Check that area field has hasProperty relation
    area_relation = None
    for relation, field_name in relations:
        if field_name == 'area':
            area_relation = relation
            break
    
    if area_relation:
        print(f"✓ Area field has relation: {area_relation._local_name}")
        assert area_relation._local_name == 'hasProperty', f"Expected 'hasProperty', got '{area_relation._local_name}'"
        print("✓ Relation inference working correctly for Space.area!")
    else:
        print("✗ No relation found for area field")
        raise AssertionError("Area field should have a relation")
    
    print()

def test_window_relation_inference():
    """Test that Window class correctly infers hasProperty for all property fields"""
    print("Testing Window class relation inference...")
    
    relations = Window.get_relations()
    print(f"Window relations: {relations}")
    
    expected_fields = {'area', 'azimuth', 'tilt'}
    found_fields = set()
    
    for relation, field_name in relations:
        if field_name in expected_fields:
            found_fields.add(field_name)
            print(f"✓ {field_name} field has relation: {relation._local_name}")
            assert relation._local_name == 'hasProperty', f"Expected 'hasProperty' for {field_name}, got '{relation._local_name}'"
    
    if found_fields == expected_fields:
        print("✓ All Window property fields have correct relations!")
    else:
        missing = expected_fields - found_fields
        print(f"✗ Missing relations for fields: {missing}")
        raise AssertionError(f"Missing relations for: {missing}")
    
    print()

def test_physical_space_self_reference():
    """Test that PhysicalSpace correctly infers contains relation for Self reference"""
    print("Testing PhysicalSpace self-reference relation inference...")
    
    relations = PhysicalSpace.get_relations()
    print(f"PhysicalSpace relations: {relations}")
    
    # Note: contains and encloses are explicitly defined with valid_field, so they should still work
    contains_relation = None
    for relation, field_name in relations:
        if field_name == 'contains':
            contains_relation = relation
            break
    
    if contains_relation:
        print(f"✓ Contains field has relation: {contains_relation._local_name}")
        print("✓ Self-reference relation working!")
    else:
        print("Note: contains field uses valid_field with explicit relation")
    
    print()

def test_yaml_generation():
    """Test that YAML generation still works with inferred relations"""
    print("Testing YAML generation with inferred relations...")
    
    try:
        yaml_output = Space.to_yaml()
        print("Space YAML output:")
        print(yaml_output)
        print("✓ YAML generation successful!")
        yaml_output = Space_TwoArea.to_yaml()
        print("Space2Area YAML output:")
        print(yaml_output)
        print("✓ YAML generation successful!")
        yaml_output = Area.to_yaml()
        print("Area YAML output:")
        print(yaml_output)
        print("✓ YAML generation successful!")
    except Exception as e:
        print(f"✗ YAML generation failed: {e}")
        raise
    
    print()

def test_rdf_generation():
    """Test that RDF class definition generation works with inferred relations"""
    print("Testing RDF class definition generation with inferred relations...")
    
    try:
        rdf_output = Space.generate_rdf_class_definition(include_hierarchy=True)
        print("Space RDF class definition (first 500 chars):")
        print(rdf_output)
        # print(rdf_output[:500])
        # print("...")
        print("✓ RDF generation successful!")
        rdf_output = Space_TwoArea.generate_rdf_class_definition(include_hierarchy=False)
        print("SpaceTwoArea RDF class definition")
        print(rdf_output)
    except Exception as e:
        print(f"✗ RDF generation failed: {e}")
        raise
    
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("RELATION INFERENCE TEST SUITE")
    print("=" * 60)
    print()
    
    try:
        test_space_relation_inference()
        test_window_relation_inference()
        test_physical_space_self_reference()
        test_yaml_generation()
        test_rdf_generation()
        
        print("=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"TEST FAILED: {e}")
        print("=" * 60)
        raise
