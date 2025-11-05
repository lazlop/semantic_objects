#!/usr/bin/env python3
"""
Demo script showing how to generate YAML templates from s223 resource classes.

This demonstrates the enhanced semantic_objects functionality that allows
s223 resources to generate YAML templates similar to the examples in the
templates/ directory.
"""

from src.semantic_objects.s223.entities import Space, Space_OptArea, Window
from semantic_objects.s223.properties import Area, Azimuth, Tilt

def main():
    print("=" * 60)
    print("TEMPLATE BUILDER DEMO")
    print("=" * 60)
    print()
    
    print("This demo shows how s223 resource classes can now generate")
    print("YAML templates that match the format in templates/")
    print()
    
    # Entity templates
    print("🏢 ENTITY TEMPLATES")
    print("-" * 40)
    
    print("\n1. Space (basic):")
    print(Space.to_yaml())
    
    print("\n2. Space with optional area:")
    print(Space_OptArea.to_yaml())
    
    print("\n3. Window (multiple properties):")
    print(Window.to_yaml())
    
    # Value templates  
    print("\n📏 VALUE TEMPLATES")
    print("-" * 40)
    
    print("\n1. Area:")
    print(Area.to_yaml())
    
    print("\n2. Azimuth:")
    print(Azimuth.to_yaml())
    
    print("\n3. Tilt:")
    print(Tilt.to_yaml())

    print('instantiating space')
    a = Space(Area(10))
    print(a)

if __name__ == "__main__":
    main()
