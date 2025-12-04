#!/usr/bin/env python3

# Test the new RDF generation method
from src.semantic_objects.s223 import PhysicalSpace, Area_FT2, Window, Area

def test_rdf_generation(for_class = PhysicalSpace):
    print(f"Testing RDF class definition generation for {for_class.__name__}")
    print("=" * 60)
    rdf_output = for_class.generate_rdf_class_definition()
    print(rdf_output)

if __name__ == "__main__":
    test_rdf_generation()
    test_rdf_generation(Area_FT2)
    test_rdf_generation(Area)
    test_rdf_generation(Window)
