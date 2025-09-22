#!/usr/bin/env python3

import sys
sys.path.append('src')

from template_builder.watr.entities import Tank, MyCoolAnaerobicPFR

def test_triple_fields():
    print("Testing Tank RDF generation with triple_fields:")
    print("=" * 50)
    
    # Generate RDF for Tank class
    tank_rdf = Tank.generate_rdf_class_definition()
    print("Tank RDF:")
    print(tank_rdf)
    print("\n" + "=" * 50)
    
    # Generate RDF for MyCoolAnaerobicPFR class
    pfr_rdf = MyCoolAnaerobicPFR.generate_rdf_class_definition()
    print("MyCoolAnaerobicPFR RDF:")
    print(pfr_rdf)

if __name__ == "__main__":
    test_triple_fields()
