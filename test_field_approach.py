#!/usr/bin/env python3

from src.template_builder.s223.entities import FieldSpace, FieldSpaceOptArea, FieldWindow

def test_field_space():
    """Test the new field-based Space class"""
    print("Testing FieldSpace:")
    print("Relations:", FieldSpace.get_relations())
    print("Dependencies:", FieldSpace.get_dependencies())
    print("Optional fields:", FieldSpace.get_optional_fields())
    print("YAML template:")
    print(FieldSpace.to_yaml("space"))
    print()

def test_field_space_opt_area():
    """Test the new field-based Space with optional area"""
    print("Testing FieldSpaceOptArea:")
    print("Relations:", FieldSpaceOptArea.get_relations())
    print("Dependencies:", FieldSpaceOptArea.get_dependencies())
    print("Optional fields:", FieldSpaceOptArea.get_optional_fields())
    print("YAML template:")
    print(FieldSpaceOptArea.to_yaml("space-optarea"))
    print()

def test_field_window():
    """Test the new field-based Window class"""
    print("Testing FieldWindow:")
    print("Relations:", FieldWindow.get_relations())
    print("Dependencies:", FieldWindow.get_dependencies())
    print("Optional fields:", FieldWindow.get_optional_fields())
    print("YAML template:")
    print(FieldWindow.to_yaml("window"))
    print()

if __name__ == "__main__":
    test_field_space()
    test_field_space_opt_area()
    test_field_window()
