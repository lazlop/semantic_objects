#!/usr/bin/env python3

import yaml
from src.template_builder.s223.entities import FieldSpace, FieldSpaceOptArea, FieldWindow

def load_original_templates():
    """Load the original templates from templates/entities.yml"""
    with open('templates/entities.yml', 'r') as f:
        return yaml.safe_load(f)

def compare_templates():
    """Compare generated templates with original ones"""
    original = load_original_templates()
    
    print("=== COMPARISON: Space Template ===")
    print("Original space template:")
    print(yaml.dump({'space': original['space']}, default_flow_style=False))
    print("Generated space template:")
    print(FieldSpace.to_yaml("space"))
    
    print("\n=== COMPARISON: Space-OptArea Template ===")
    print("Original space-optarea template:")
    print(yaml.dump({'space-optarea': original['space-optarea']}, default_flow_style=False))
    print("Generated space-optarea template:")
    print(FieldSpaceOptArea.to_yaml("space-optarea"))
    
    print("\n=== COMPARISON: Window Template ===")
    print("Original window template:")
    print(yaml.dump({'window': original['window']}, default_flow_style=False))
    print("Generated window template:")
    print(FieldWindow.to_yaml("window"))

if __name__ == "__main__":
    compare_templates()
