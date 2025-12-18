#!/usr/bin/env python3
"""
Test script to verify the include_hierarchy parameter in generate_rdf_class_definition
"""

from src.semantic_objects.s223.entities import Space, PhysicalSpace, Space_TwoArea, Window

def test_hierarchy_modes():
    """Test both hierarchy modes for RDF class definition generation"""
    
    print("=" * 80)
    print("Testing generate_rdf_class_definition with include_hierarchy parameter")
    print("=" * 80)
    
    # Test with a class that has inheritance (Space inherits from PhysicalSpace)
    print("\n1. Testing Space class WITH hierarchy (include_hierarchy=True)")
    print("-" * 80)
    space_with_hierarchy = Space.generate_rdf_class_definition(include_hierarchy=True)
    print(space_with_hierarchy)
    
    print("\n2. Testing Space class WITHOUT hierarchy (include_hierarchy=False)")
    print("-" * 80)
    space_without_hierarchy = Space.generate_rdf_class_definition(include_hierarchy=False)
    print(space_without_hierarchy)
    
    # Test with Space_TwoArea which inherits from Space (which inherits from PhysicalSpace)
    print("\n3. Testing Space_TwoArea class WITH hierarchy (include_hierarchy=True)")
    print("-" * 80)
    space_two_area_with_hierarchy = Space_TwoArea.generate_rdf_class_definition(include_hierarchy=True)
    print(space_two_area_with_hierarchy)
    
    print("\n4. Testing Space_TwoArea class WITHOUT hierarchy (include_hierarchy=False)")
    print("-" * 80)
    space_two_area_without_hierarchy = Space_TwoArea.generate_rdf_class_definition(include_hierarchy=False)
    print(space_two_area_without_hierarchy)
    
    # Test with Window class (has multiple fields)
    print("\n5. Testing Window class WITH hierarchy (include_hierarchy=True)")
    print("-" * 80)
    window_with_hierarchy = Window.generate_rdf_class_definition(include_hierarchy=True)
    print(window_with_hierarchy)
    
    print("\n6. Testing Window class WITHOUT hierarchy (include_hierarchy=False)")
    print("-" * 80)
    window_without_hierarchy = Window.generate_rdf_class_definition(include_hierarchy=False)
    print(window_without_hierarchy)
    
    
    print("\n" + "=" * 80)
    print("Analysis:")
    print("=" * 80)
    print("- WITH hierarchy: Should include relations from parent classes")
    print("- WITHOUT hierarchy: Should only include relations declared on the specific class")
    print("\nCompare the sh:property statements in each output to verify the difference.")

if __name__ == "__main__":
    test_hierarchy_modes()
