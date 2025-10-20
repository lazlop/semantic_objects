#!/usr/bin/env python3

from src.semantic_objects.s223.entities import Space, SpaceOptArea, Window
from src.semantic_objects.watr.entities import Tank

def test__space():
    """Test the new -based Space class"""
    print("Testing Space:")
    print("Relations:", Space.get_relations())
    print("Dependencies:", Space.get_dependencies())
    print("Optional s:", Space.get_optional_fields())
    print("YAML template:")
    print(Space.to_yaml("space"))
    print()

def test__space_opt_area():
    """Test the new -based Space with optional area"""
    print("Testing SpaceOptArea:")
    print("Relations:", SpaceOptArea.get_relations())
    print("Dependencies:", SpaceOptArea.get_dependencies())
    print("Optional s:", SpaceOptArea.get_optional_fields())
    print("YAML template:")
    print(SpaceOptArea.to_yaml("space-optarea"))
    print()

def test__window():
    """Test the new -based Window class"""
    print("Testing Window:")
    print("Relations:", Window.get_relations())
    print("Dependencies:", Window.get_dependencies())
    print("Optional s:", Window.get_optional_fields())
    print("YAML template:")
    print(Window.to_yaml("window"))
    print()

def test_tank():
    """Test the new -based Window class"""
    print("Testing Window:")
    print("Relations:", Tank.get_relations())
    print("Dependencies:", Tank.get_dependencies())
    print("Optional s:", Tank.get_optional_fields())
    print("YAML template:")
    print(Tank.to_yaml("window"))
    print()

if __name__ == "__main__":
    test__space()
    test__space_opt_area()
    test__window()
    test_tank()