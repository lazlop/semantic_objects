#!/usr/bin/env python3
"""
Basic Usage Examples for Semantic Objects

This script demonstrates the core functionality of the semantic_objects library
using the real, ontology-generated s223 classes (see
tutorial/s223-generated-classes-tutorial.ipynb for a more detailed walkthrough).
"""

from semantic_objects.s223 import entities, enumerationkinds
from semantic_objects.exporters import export_templates
from semantic_objects.build_model import BMotifSession
from semantic_objects.model_loader import ModelLoader


def example_1_creating_objects():
    """Example 1: Creating semantic objects"""
    print("=" * 60)
    print("Example 1: Creating Semantic Objects")
    print("=" * 60)

    # DomainSpace is a real ontology class - `domain` is required
    zone = entities.DomainSpace(domain=enumerationkinds.HVAC())
    print(f"Created zone: {zone._name}")
    print(f"Zone domain: {zone.domain._name}")

    # Pump demonstrates qualified fields: two connection points sharing the
    # `hasConnectionPoint` relation, narrowed to specific subtypes by the ontology
    water = enumerationkinds.Water()
    connection = entities.Connection(medium=water)
    pump = entities.Pump(
        outlet_connection_point=entities.OutletConnectionPoint(medium=water, connection=connection),
        inlet_connection_point=entities.InletConnectionPoint(medium=water, connection=connection),
    )
    print(f"\nCreated pump: {pump._name}")
    print(f"Pump outlet medium: {pump.outlet_connection_point.medium._name}")

    return zone, pump


def example_2_template_generation():
    """Example 2: Generating BuildingMOTIF templates"""
    print("\n" + "=" * 60)
    print("Example 2: Template Generation")
    print("=" * 60)

    # Export templates for DomainSpace (includes all related classes)
    export_templates([entities.DomainSpace], 'example_templates')
    print("✅ Exported DomainSpace templates to 'example_templates/' directory")

    # Show generated YAML template
    zone_yaml = entities.DomainSpace.generate_yaml_template()
    print("\nGenerated DomainSpace template:")
    print(zone_yaml)

    return 'example_templates'


def example_3_model_building():
    """Example 3: Building RDF models with BMotifSession"""
    print("\n" + "=" * 60)
    print("Example 3: Model Building")
    print("=" * 60)

    # Create BMotifSession
    session = BMotifSession(ns='example')

    # Load templates
    session.load_class_templates(entities.DomainSpace)
    print(f"Loaded templates: {list(session.templates.keys())}")

    # Create objects
    conference_room = entities.DomainSpace(domain=enumerationkinds.HVAC())
    conference_room._name = "ConferenceRoom_A"

    # Evaluate objects (generate RDF)
    session.evaluate(conference_room)

    print(f"✅ Generated RDF model with {len(session.model.graph)} triples")

    # Show sample RDF
    rdf_sample = session.model.graph.serialize(format='turtle')
    lines = rdf_sample.split('\n')
    print("\nSample RDF (first 10 lines):")
    for line in lines[:10]:
        print(f"  {line}")

    return session.model.graph


def example_4_model_loading():
    """Example 4: Loading objects from RDF graphs"""
    print("\n" + "=" * 60)
    print("Example 4: Model Loading")
    print("=" * 60)

    # Use the graph from example 3
    graph = example_3_model_building()

    # Initialize ModelLoader
    loader = ModelLoader(source=graph)

    # Load DomainSpace instances
    zones = loader.load_instances(entities.DomainSpace, ontology='s223')
    print(f"Loaded {len(zones)} DomainSpace objects:")
    for zone in zones:
        print(f"  - {zone._name}")

    return zones


def example_5_query_generation():
    """Example 5: Automatic SPARQL query generation"""
    print("\n" + "=" * 60)
    print("Example 5: Query Generation")
    print("=" * 60)

    # Generate SPARQL query for DomainSpace
    zone_query = entities.DomainSpace.get_sparql_query(ontology='s223')
    print("Generated SPARQL query for DomainSpace:")
    print(zone_query)

    # Generate query for Pump (more complex - qualified connection-point fields)
    print("\n" + "-" * 40)
    pump_query = entities.Pump.get_sparql_query(ontology='s223')
    print("Generated SPARQL query for Pump:")
    print(pump_query)


def example_6_validation():
    """Example 6: SHACL validation shape generation"""
    print("\n" + "=" * 60)
    print("Example 6: Validation Shapes")
    print("=" * 60)

    # Generate SHACL shape for DomainSpace
    shacl_shape = entities.DomainSpace.generate_rdf_class_definition(include_hierarchy=False)
    print("Generated SHACL shape for DomainSpace:")
    print(shacl_shape)


def example_7_units_and_properties():
    """Example 7: Working with different units and properties"""
    print("\n" + "=" * 60)
    print("Example 7: Units and Properties")
    print("=" * 60)

    from semantic_objects.s223.properties import Area
    from semantic_objects.qudt.units import M2, FT2

    # Create areas with different units
    metric_area = Area(50.0, unit=M2)
    imperial_area = Area(50.0, unit=FT2)

    print(f"Metric area: {metric_area.value} {metric_area.unit._name}")
    print(f"Imperial area: {imperial_area.value} {imperial_area.unit._name}")

    # Show quantity kinds
    print(f"\nArea quantity kind: {Area.qk}")


def main():
    """Run all examples"""
    print("Semantic Objects - Basic Usage Examples")
    print("=" * 60)

    try:
        # Run examples
        zone, pump = example_1_creating_objects()
        template_dir = example_2_template_generation()
        graph = example_3_model_building()
        zones = example_4_model_loading()
        example_5_query_generation()
        example_6_validation()
        example_7_units_and_properties()

        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)

        print(f"\nGenerated files:")
        print(f"  - Templates: {template_dir}/")
        print(f"  - Objects created: {len(zones)} zones")
        print(f"  - RDF triples: {len(graph)}")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
