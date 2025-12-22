#!/usr/bin/env python3
"""
Basic Usage Examples for Semantic Objects

This script demonstrates the core functionality of the semantic_objects library
with simple, practical examples.
"""

from semantic_objects.s223 import Space, Window, Area, Azimuth, Tilt
from semantic_objects.core import export_templates
from semantic_objects.build_model import BMotifSession
from semantic_objects.model_loader import ModelLoader
from rdflib import Graph


def example_1_creating_objects():
    """Example 1: Creating semantic objects"""
    print("=" * 60)
    print("Example 1: Creating Semantic Objects")
    print("=" * 60)
    
    # Create a space with area
    office = Space(area=150.0)  # Area in default units (ft²)
    print(f"Created office: {office._name}")
    print(f"Office area: {office.area.value} {office.area.unit}")
    
    # Create a window with multiple properties
    south_window = Window(
        area=25.0,      # ft²
        azimuth=180.0,  # degrees (south-facing)
        tilt=90.0       # degrees (vertical)
    )
    print(f"\nCreated window: {south_window._name}")
    print(f"Window area: {south_window.area.value} {south_window.area.unit}")
    print(f"Window orientation: {south_window.azimuth.value}° azimuth, {south_window.tilt.value}° tilt")
    
    return office, south_window


def example_2_template_generation():
    """Example 2: Generating BuildingMOTIF templates"""
    print("\n" + "=" * 60)
    print("Example 2: Template Generation")
    print("=" * 60)
    
    # Export templates for Space (includes all related classes)
    export_templates(Space, 'example_templates')
    print("✅ Exported Space templates to 'example_templates/' directory")
    
    # Show generated YAML template
    space_yaml = Space.generate_yaml_template()
    print("\nGenerated Space template:")
    print(space_yaml)
    
    return 'example_templates'


def example_3_model_building():
    """Example 3: Building RDF models with BMotifSession"""
    print("\n" + "=" * 60)
    print("Example 3: Model Building")
    print("=" * 60)
    
    # Create BMotifSession
    session = BMotifSession(ns='example')
    
    # Load templates
    session.load_class_templates(Space)
    session.load_class_templates(Window)
    print(f"Loaded templates: {list(session.templates.keys())}")
    
    # Create objects
    conference_room = Space(area=200.0)
    conference_room._name = "ConferenceRoom_A"
    
    east_window = Window(area=30.0, azimuth=90.0, tilt=90.0)
    east_window._name = "Window_East_A"
    
    # Evaluate objects (generate RDF)
    session.evaluate(conference_room)
    session.evaluate(east_window)
    
    print(f"✅ Generated RDF model with {len(session.graph)} triples")
    
    # Show sample RDF
    rdf_sample = session.graph.serialize(format='turtle')
    lines = rdf_sample.split('\n')
    print("\nSample RDF (first 10 lines):")
    for line in lines[:10]:
        print(f"  {line}")
    
    return session.graph


def example_4_model_loading():
    """Example 4: Loading objects from RDF graphs"""
    print("\n" + "=" * 60)
    print("Example 4: Model Loading")
    print("=" * 60)
    
    # Use the graph from example 3
    graph = example_3_model_building()
    
    # Initialize ModelLoader
    loader = ModelLoader(source=graph)
    
    # Load Space instances
    spaces = loader.load_instances(Space, ontology='s223')
    print(f"Loaded {len(spaces)} Space objects:")
    for space in spaces:
        print(f"  - {space._name}: {space.area.value} {space.area.unit}")
    
    # Load Window instances
    windows = loader.load_instances(Window, ontology='s223')
    print(f"\nLoaded {len(windows)} Window objects:")
    for window in windows:
        direction = {90.0: "East", 180.0: "South", 270.0: "West", 0.0: "North"}
        dir_name = direction.get(window.azimuth.value, f"{window.azimuth.value}°")
        print(f"  - {window._name}: {window.area.value} ft², {dir_name}-facing")
    
    return spaces, windows


def example_5_query_generation():
    """Example 5: Automatic SPARQL query generation"""
    print("\n" + "=" * 60)
    print("Example 5: Query Generation")
    print("=" * 60)
    
    # Generate SPARQL query for Space
    space_query = Space.get_sparql_query(ontology='s223')
    print("Generated SPARQL query for Space:")
    print(space_query)
    
    # Generate query for Window (more complex)
    print("\n" + "-" * 40)
    window_query = Window.get_sparql_query(ontology='s223')
    print("Generated SPARQL query for Window:")
    print(window_query)


def example_6_validation():
    """Example 6: SHACL validation shape generation"""
    print("\n" + "=" * 60)
    print("Example 6: Validation Shapes")
    print("=" * 60)
    
    # Generate SHACL shape for Space
    shacl_shape = Space.generate_rdf_class_definition(include_hierarchy=False)
    print("Generated SHACL shape for Space:")
    print(shacl_shape)


def example_7_units_and_properties():
    """Example 7: Working with different units and properties"""
    print("\n" + "=" * 60)
    print("Example 7: Units and Properties")
    print("=" * 60)
    
    # Import specific units
    from semantic_objects.qudt.units import M2, FT2, DEG_C, DEG_F
    
    # Create areas with different units
    metric_area = Area(50.0, unit=M2)
    imperial_area = Area(50.0, unit=FT2)
    
    print(f"Metric area: {metric_area.value} {metric_area.unit}")
    print(f"Imperial area: {imperial_area.value} {imperial_area.unit}")
    
    # Create spaces with different units
    metric_space = Space(area=metric_area)
    imperial_space = Space(area=imperial_area)
    
    print(f"\nMetric space: {metric_space.area.value} {metric_space.area.unit}")
    print(f"Imperial space: {imperial_space.area.value} {imperial_space.area.unit}")
    
    # Show quantity kinds
    print(f"\nArea quantity kind: {Area.qk}")
    print(f"Azimuth quantity kind: {Azimuth.qk}")


def main():
    """Run all examples"""
    print("Semantic Objects - Basic Usage Examples")
    print("=" * 60)
    
    try:
        # Run examples
        office, window = example_1_creating_objects()
        template_dir = example_2_template_generation()
        graph = example_3_model_building()
        spaces, windows = example_4_model_loading()
        example_5_query_generation()
        example_6_validation()
        example_7_units_and_properties()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        
        print(f"\nGenerated files:")
        print(f"  - Templates: {template_dir}/")
        print(f"  - Objects created: {len(spaces)} spaces, {len(windows)} windows")
        print(f"  - RDF triples: {len(graph)}")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()