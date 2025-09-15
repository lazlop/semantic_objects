#!/usr/bin/env python3

# Test the new RDF generation method
from src.template_builder.s223.entities import PhysicalSpace

def test_rdf_generation():
    print("Testing RDF class definition generation for PhysicalSpace:")
    print("=" * 60)
    
    try:
        rdf_output = PhysicalSpace.generate_rdf_class_definition()
        print(rdf_output)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rdf_generation()
