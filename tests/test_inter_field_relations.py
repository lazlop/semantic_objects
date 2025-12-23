"""Test inter-field relations functionality"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from semantic_objects.s223.entities import SpaceWithWindow, SpaceWithWindowNoMainRelation, Space, Window
from semantic_objects.s223.properties import Area, Azimuth, Tilt
from semantic_objects.s223.relations import connectedTo
from semantic_objects import units

def test_space_with_window_template():
    """Test that SpaceWithWindow generates correct template with inter-field relations"""
    
    # Generate YAML template
    yaml_output = SpaceWithWindow.to_yaml()
    print("Generated YAML template:")
    print(yaml_output)
    print("\n" + "="*80 + "\n")
    
    # Check that the template includes the inter-field relation
    assert 'connectedTo' in yaml_output, "Template should include connectedTo relation"
    assert 'P:space' in yaml_output, "Template should reference space field"
    assert 'P:window' in yaml_output, "Template should reference window field"
    
    # Generate Turtle body to see the RDF structure
    turtle_body = SpaceWithWindow.generate_turtle_body()
    print("Generated Turtle body:")
    print(turtle_body)
    print("\n" + "="*80 + "\n")
    
    # Check that the turtle includes the inter-field relation triple
    assert 'P:space' in turtle_body, "Turtle should include space parameter"
    assert 'P:window' in turtle_body, "Turtle should include window parameter"
    assert 's223:connectedTo' in turtle_body, "Turtle should include connectedTo relation"
    
    print("✓ Template generation test passed!")

def test_space_with_window_relations():
    """Test that get_relations includes inter-field relations"""
    
    relations = SpaceWithWindow.get_relations()
    print("Relations found:")
    for relation, field_name in relations:
        print(f"  - {relation._name} (field: {field_name})")
    print("\n" + "="*80 + "\n")
    
    # Check that connectedTo relation is included
    relation_names = [rel._name for rel, _ in relations]
    assert 'connectedTo' in relation_names, "Relations should include connectedTo"
    
    print("✓ Relations test passed!")

def test_space_with_window_dependencies():
    """Test that dependencies are correctly identified"""
    
    dependencies = SpaceWithWindow.get_dependencies()
    print("Dependencies found:")
    for dep in dependencies:
        print(f"  - {dep['template'].__name__} (args: {dep['args']})")
    print("\n" + "="*80 + "\n")
    
    # Should have dependencies for space, window, and area (from parent Space class)
    dep_templates = [dep['template'].__name__ for dep in dependencies]
    assert 'Space' in dep_templates, "Should have Space dependency"
    assert 'Window' in dep_templates, "Should have Window dependency"
    assert 'Area' in dep_templates, "Should have Area dependency (from parent)"
    
    print("✓ Dependencies test passed!")

def test_inter_field_relations_retrieval():
    """Test that _get_inter_field_relations works correctly"""
    
    inter_field_rels = SpaceWithWindow._get_inter_field_relations()
    print("Inter-field relations found:")
    for rel in inter_field_rels:
        print(f"  - {rel['source_field']} --{rel['relation']._name}--> {rel['target_field']}")
    print("\n" + "="*80 + "\n")
    
    assert len(inter_field_rels) == 1, "Should have exactly one inter-field relation"
    assert inter_field_rels[0]['source_field'] == 'space', "Source should be 'space'"
    assert inter_field_rels[0]['target_field'] == 'window', "Target should be 'window'"
    assert inter_field_rels[0]['relation']._name == 'connectedTo', "Relation should be connectedTo"
    
    print("✓ Inter-field relations retrieval test passed!")

def test_instance_creation():
    """Test that we can create instances with inter-field relations"""
    
    # Create instances
    my_space = Space(area=Area(100, units.FT_2))
    my_window = Window(
        area=Area(10, units.FT_2),
        azimuth=Azimuth(180),
        tilt=Tilt(90)
    )
    
    space_with_window = SpaceWithWindow(
        area=Area(100, units.FT_2),
        space=my_space,
        window=my_window
    )
    
    print(f"Created SpaceWithWindow instance: {space_with_window._name}")
    print(f"  - space: {space_with_window.space._name}")
    print(f"  - window: {space_with_window.window._name}")
    print("\n" + "="*80 + "\n")
    
    assert space_with_window.space == my_space, "Space field should match"
    assert space_with_window.window == my_window, "Window field should match"
    
    print("✓ Instance creation test passed!")

def test_no_main_relation():
    """Test that relation=None skips creating main entity relation"""
    
    # Generate YAML template
    yaml_output = SpaceWithWindowNoMainRelation.to_yaml()
    print("Generated YAML template (with relation=None):")
    print(yaml_output)
    print("\n" + "="*80 + "\n")
    
    # Generate Turtle body to see the RDF structure
    turtle_body = SpaceWithWindowNoMainRelation.generate_turtle_body()
    print("Generated Turtle body (with relation=None):")
    print(turtle_body)
    print("\n" + "="*80 + "\n")
    
    # Check that window is NOT directly related to the main entity
    # Count occurrences of "P:name" followed by any relation to "P:window"
    lines = turtle_body.split('\n')
    main_to_window_relations = [line for line in lines if 'P:name' in line and 'P:window' in line]
    assert len(main_to_window_relations) == 0, "Main entity should NOT have direct relation to window"
    
    # Check that space->window relation still exists
    assert 'P:space s223:connectedTo P:window' in turtle_body, "Inter-field relation should still exist"
    
    # Check that space is still related to main entity
    assert 'P:name' in turtle_body and 's223:hasDomainSpace P:space' in turtle_body, "Main entity should still relate to space"
    
    # Check relations list
    relations = SpaceWithWindowNoMainRelation.get_relations()
    relation_names = [rel._name for rel, _ in relations]
    print("Relations found (with relation=None):")
    for relation, field_name in relations:
        print(f"  - {relation._name} (field: {field_name})")
    print()
    
    # hasWindow should NOT be in relations since window has relation=None
    assert 'hasWindow' not in relation_names, "hasWindow should not be in relations when relation=None"
    # connectedTo should still be there from inter-field relation
    assert 'connectedTo' in relation_names, "connectedTo should still be in relations"
    
    print("✓ No main relation test passed!")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("Testing Inter-Field Relations Functionality")
    print("="*80 + "\n")
    
    test_space_with_window_template()
    test_space_with_window_relations()
    test_space_with_window_dependencies()
    test_inter_field_relations_retrieval()
    test_instance_creation()
    test_no_main_relation()
    
    print("\n" + "="*80)
    print("All tests passed! ✓")
    print("="*80 + "\n")
