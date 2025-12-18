#!/usr/bin/env python3

# Test the qualified value shapes in RDF generation
from src.semantic_objects.s223.entities import Space, Window

def test_space_rdf():
    print("Testing RDF class definition generation for Space (with Area field):")
    print("=" * 80)
    
    try:
        rdf_output = Space.generate_rdf_class_definition(include_hierarchy=True)
        print(rdf_output)
        print("\n")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_window_rdf():
    print("Testing RDF class definition generation for Window (with multiple fields):")
    print("=" * 80)
    
    try:
        rdf_output = Window.generate_rdf_class_definition()
        print(rdf_output)
        print("\n")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_space_rdf()
    test_window_rdf()
