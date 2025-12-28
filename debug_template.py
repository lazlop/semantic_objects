#!/usr/bin/env python3
"""
Debug script to understand template generation
"""

from src.semantic_objects.s223.properties import EnvironmentalStation, PowerConsumption, AirPressure
import yaml

def debug_template_generation():
    print("=" * 60)
    print("Debug Template Generation")
    print("=" * 60)
    
    # Check relations
    relations = EnvironmentalStation.get_relations()
    print(f"EnvironmentalStation relations:")
    for relation, field_name in relations:
        print(f"  {field_name}: {relation._name}")
    
    # Check template parameters
    params = EnvironmentalStation._get_template_parameters()
    print(f"\nTemplate parameters:")
    for field_name, field_obj in params.items():
        print(f"  {field_name}: {field_obj.type}, init={field_obj.init}, default={field_obj.default}")
    
    # Check dependencies
    deps = EnvironmentalStation.get_dependencies()
    print(f"\nDependencies:")
    for dep in deps:
        print(f"  {dep['template'].__name__}: {dep['args']}")
    
    # Generate turtle body
    turtle_body = EnvironmentalStation.generate_turtle_body()
    print(f"\nGenerated turtle body:")
    print(turtle_body)
    
    # Generate full template
    template = EnvironmentalStation.generate_yaml_template()
    print(f"\nFull template:")
    print(yaml.dump(template, default_flow_style=False))

if __name__ == "__main__":
    debug_template_generation()