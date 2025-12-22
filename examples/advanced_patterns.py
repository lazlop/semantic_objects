#!/usr/bin/env python3
"""
Advanced Patterns and Use Cases for Semantic Objects

This script demonstrates advanced usage patterns, custom entities,
and complex relationships in the semantic_objects library.
"""

from typing import Optional, List
from semantic_objects.s223 import *
from semantic_objects.core import (
    semantic_object, required_field, optional_field, exclusive_field,
    export_templates, get_related_classes
)
from semantic_objects.build_model import BMotifSession
from semantic_objects.model_loader import ModelLoader
from semantic_objects.s223.properties import Temperature, Pressure
from semantic_objects.s223.enumerationkinds import Setpoint
from rdflib import Graph


# Custom entity definitions
@semantic_object
class ConditionedSpace(Space):
    """A space with HVAC conditioning"""
    design_temperature: Temperature = required_field(
        label="Design Temperature",
        comment="Target temperature for HVAC system"
    )
    
    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.design_temperature, Temperature):
            self.design_temperature = Temperature(self.design_temperature)


@semantic_object
class Office(ConditionedSpace):
    """Office space with occupancy and equipment"""
    max_occupancy: int = required_field(
        label="Maximum Occupancy",
        comment="Maximum number of people allowed"
    )
    has_windows: bool = optional_field(
        label="Has Windows",
        comment="Whether the office has exterior windows"
    )


@semantic_object
class ConferenceRoom(ConditionedSpace):
    """Conference room with AV equipment"""
    av_equipment: bool = required_field(
        label="AV Equipment",
        comment="Whether the room has audio/visual equipment"
    )
    seating_capacity: int = required_field(
        label="Seating Capacity",
        comment="Number of seats in the conference room"
    )


@semantic_object
class HVAC_Zone(Node):
    """HVAC zone containing multiple spaces"""
    served_spaces: List[Space] = required_field(
        label="Served Spaces",
        comment="Spaces served by this HVAC zone"
    )
    zone_type: str = exclusive_field(
        label="Zone Type",
        comment="Type of HVAC zone (VAV, CAV, etc.)"
    )


def example_1_custom_entities():
    """Example 1: Creating and using custom entities"""
    print("=" * 60)
    print("Example 1: Custom Entities")
    print("=" * 60)
    
    # Create custom office
    office_101 = Office(
        area=120.0,
        design_temperature=72.0,  # Fahrenheit
        max_occupancy=4,
        has_windows=True
    )
    office_101._name = "Office_101"
    
    # Create conference room
    conf_room_a = ConferenceRoom(
        area=300.0,
        design_temperature=70.0,
        av_equipment=True,
        seating_capacity=12
    )
    conf_room_a._name = "ConferenceRoom_A"
    
    print(f"Created office: {office_101._name}")
    print(f"  Area: {office_101.area.value} {office_101.area.unit}")
    print(f"  Design temp: {office_101.design_temperature.value}°F")
    print(f"  Max occupancy: {office_101.max_occupancy}")
    print(f"  Has windows: {office_101.has_windows}")
    
    print(f"\nCreated conference room: {conf_room_a._name}")
    print(f"  Area: {conf_room_a.area.value} {conf_room_a.area.unit}")
    print(f"  Design temp: {conf_room_a.design_temperature.value}°F")
    print(f"  AV equipment: {conf_room_a.av_equipment}")
    print(f"  Seating: {conf_room_a.seating_capacity}")
    
    return office_101, conf_room_a


def example_2_inheritance_hierarchy():
    """Example 2: Working with inheritance hierarchies"""
    print("\n" + "=" * 60)
    print("Example 2: Inheritance Hierarchy")
    print("=" * 60)
    
    # Show class hierarchy
    print("Class hierarchy:")
    print("  Space")
    print("    └── ConditionedSpace")
    print("        ├── Office")
    print("        └── ConferenceRoom")
    
    # Create instances of different types
    spaces = [
        Space(area=80.0),  # Basic space
        ConditionedSpace(area=100.0, design_temperature=68.0),
        Office(area=120.0, design_temperature=72.0, max_occupancy=2, has_windows=False),
        ConferenceRoom(area=250.0, design_temperature=70.0, av_equipment=True, seating_capacity=8)
    ]
    
    # Set names
    names = ["Storage", "ConditionedSpace_1", "Office_Small", "ConferenceRoom_B"]
    for space, name in zip(spaces, names):
        space._name = name
    
    # Show polymorphic behavior
    print("\nCreated spaces (polymorphic):")
    for space in spaces:
        print(f"  {space._name} ({type(space).__name__})")
        print(f"    Area: {space.area.value} {space.area.unit}")
        
        # Check for conditioning
        if hasattr(space, 'design_temperature'):
            print(f"    Design temp: {space.design_temperature.value}°F")
        
        # Check for office-specific attributes
        if isinstance(space, Office):
            print(f"    Max occupancy: {space.max_occupancy}")
            print(f"    Has windows: {space.has_windows}")
        
        # Check for conference room attributes
        if isinstance(space, ConferenceRoom):
            print(f"    AV equipment: {space.av_equipment}")
            print(f"    Seating: {space.seating_capacity}")
    
    return spaces


def example_3_template_generation_advanced():
    """Example 3: Advanced template generation patterns"""
    print("\n" + "=" * 60)
    print("Example 3: Advanced Template Generation")
    print("=" * 60)
    
    # Export templates for custom entities
    export_templates([Office, ConferenceRoom], 'advanced_templates')
    print("✅ Exported advanced templates")
    
    # Show template dependencies
    office_deps = Office.get_dependencies()
    conf_deps = ConferenceRoom.get_dependencies()
    
    print(f"\nOffice template dependencies:")
    for dep in office_deps:
        print(f"  - {dep['template'].__name__}: {dep['args']}")
    
    print(f"\nConferenceRoom template dependencies:")
    for dep in conf_deps:
        print(f"  - {dep['template'].__name__}: {dep['args']}")
    
    # Show related classes
    office_related = get_related_classes(Office)
    predicates, entities, values = office_related
    
    print(f"\nOffice related classes:")
    print(f"  Predicates: {len(predicates)}")
    print(f"  Entities: {len(entities)}")
    print(f"  Values: {len(values)}")
    
    print("  Entity classes:")
    for entity in entities:
        print(f"    - {entity.__name__}")


def example_4_complex_model_building():
    """Example 4: Building complex models with relationships"""
    print("\n" + "=" * 60)
    print("Example 4: Complex Model Building")
    print("=" * 60)
    
    # Create BMotifSession
    session = BMotifSession(ns='advanced_building')
    
    # Load templates for all custom classes
    for cls in [Office, ConferenceRoom, HVAC_Zone]:
        session.load_class_templates(cls)
    
    print(f"Loaded templates: {list(session.templates.keys())}")
    
    # Create a floor with multiple spaces
    floor_spaces = [
        Office(area=120.0, design_temperature=72.0, max_occupancy=4, has_windows=True),
        Office(area=100.0, design_temperature=72.0, max_occupancy=2, has_windows=False),
        ConferenceRoom(area=200.0, design_temperature=70.0, av_equipment=True, seating_capacity=8),
        ConferenceRoom(area=300.0, design_temperature=70.0, av_equipment=True, seating_capacity=12),
    ]
    
    # Set names
    space_names = ["Office_201", "Office_202", "ConferenceRoom_Small", "ConferenceRoom_Large"]
    for space, name in zip(floor_spaces, space_names):
        space._name = name
    
    # Evaluate all spaces
    for space in floor_spaces:
        session.evaluate(space)
        print(f"✅ Evaluated {space._name}")
    
    print(f"\nGenerated model with {len(session.graph)} triples")
    
    return session.graph, floor_spaces


def example_5_advanced_querying():
    """Example 5: Advanced querying and filtering"""
    print("\n" + "=" * 60)
    print("Example 5: Advanced Querying")
    print("=" * 60)
    
    # Use graph from previous example
    graph, original_spaces = example_4_complex_model_building()
    
    # Load with ModelLoader
    loader = ModelLoader(source=graph)
    
    # Load different types of spaces
    offices = loader.load_instances(Office, ontology='s223')
    conf_rooms = loader.load_instances(ConferenceRoom, ontology='s223')
    
    print(f"Loaded {len(offices)} offices and {len(conf_rooms)} conference rooms")
    
    # Advanced filtering and analysis
    print("\nOffice analysis:")
    total_office_area = sum(office.area.value for office in offices)
    total_occupancy = sum(office.max_occupancy for office in offices)
    offices_with_windows = [office for office in offices if office.has_windows]
    
    print(f"  Total office area: {total_office_area} ft²")
    print(f"  Total occupancy: {total_occupancy} people")
    print(f"  Offices with windows: {len(offices_with_windows)}")
    
    print("\nConference room analysis:")
    total_conf_area = sum(room.area.value for room in conf_rooms)
    total_seating = sum(room.seating_capacity for room in conf_rooms)
    rooms_with_av = [room for room in conf_rooms if room.av_equipment]
    
    print(f"  Total conference area: {total_conf_area} ft²")
    print(f"  Total seating capacity: {total_seating} people")
    print(f"  Rooms with AV: {len(rooms_with_av)}")
    
    # Temperature analysis
    all_conditioned = offices + conf_rooms
    avg_temp = sum(space.design_temperature.value for space in all_conditioned) / len(all_conditioned)
    print(f"\nAverage design temperature: {avg_temp:.1f}°F")
    
    return offices, conf_rooms


def example_6_custom_properties():
    """Example 6: Creating custom properties and constraints"""
    print("\n" + "=" * 60)
    print("Example 6: Custom Properties")
    print("=" * 60)
    
    # Create a custom property
    from semantic_objects.s223.properties import QuantifiableObervableProperty
    from semantic_objects.qudt import quantitykinds
    
    @semantic_object
    class Illuminance(QuantifiableObervableProperty):
        """Light level property"""
        qk = quantitykinds.Illuminance  # Assuming this exists
    
    @semantic_object
    class SmartOffice(Office):
        """Office with smart building features"""
        target_illuminance: Illuminance = optional_field(
            label="Target Illuminance",
            comment="Desired light level in lux"
        )
        automated_blinds: bool = optional_field(
            label="Automated Blinds",
            comment="Whether the office has automated window blinds"
        )
    
    # Create smart office
    smart_office = SmartOffice(
        area=150.0,
        design_temperature=71.0,
        max_occupancy=3,
        has_windows=True,
        automated_blinds=True
    )
    smart_office._name = "SmartOffice_301"
    
    print(f"Created smart office: {smart_office._name}")
    print(f"  Standard office features: ✓")
    print(f"  Automated blinds: {smart_office.automated_blinds}")
    
    # Show template generation for custom properties
    smart_yaml = SmartOffice.generate_yaml_template()
    print(f"\nSmart office template preview:")
    lines = smart_yaml.split('\n')
    for line in lines[:10]:
        print(f"  {line}")
    
    return smart_office


def example_7_validation_and_constraints():
    """Example 7: Validation and SHACL constraints"""
    print("\n" + "=" * 60)
    print("Example 7: Validation and Constraints")
    print("=" * 60)
    
    # Generate SHACL shapes for custom classes
    office_shacl = Office.generate_rdf_class_definition(include_hierarchy=True)
    conf_shacl = ConferenceRoom.generate_rdf_class_definition(include_hierarchy=False)
    
    print("Generated SHACL shapes:")
    print(f"  Office (with hierarchy): {len(office_shacl)} characters")
    print(f"  ConferenceRoom (local only): {len(conf_shacl)} characters")
    
    # Show constraint examples
    print("\nOffice SHACL constraints (sample):")
    lines = office_shacl.split('\n')
    for line in lines[:15]:
        if line.strip():
            print(f"  {line}")
    
    # Show field constraints
    office_fields = Office.__dataclass_fields__
    print("\nOffice field constraints:")
    for field_name, field_obj in office_fields.items():
        if hasattr(field_obj, 'metadata') and field_obj.metadata:
            constraints = []
            if 'min' in field_obj.metadata:
                constraints.append(f"min={field_obj.metadata['min']}")
            if 'max' in field_obj.metadata:
                constraints.append(f"max={field_obj.metadata['max']}")
            if 'qualified' in field_obj.metadata:
                constraints.append(f"qualified={field_obj.metadata['qualified']}")
            
            if constraints:
                print(f"  {field_name}: {', '.join(constraints)}")


def example_8_round_trip_workflow():
    """Example 8: Complete round-trip workflow"""
    print("\n" + "=" * 60)
    print("Example 8: Round-Trip Workflow")
    print("=" * 60)
    
    # Step 1: Create complex objects
    building_spaces = [
        Office(area=110.0, design_temperature=72.0, max_occupancy=3, has_windows=True),
        Office(area=95.0, design_temperature=71.0, max_occupancy=2, has_windows=False),
        ConferenceRoom(area=180.0, design_temperature=69.0, av_equipment=True, seating_capacity=6),
    ]
    
    names = ["Office_RT1", "Office_RT2", "ConferenceRoom_RT1"]
    for space, name in zip(building_spaces, names):
        space._name = name
    
    print(f"Step 1: Created {len(building_spaces)} objects")
    
    # Step 2: Generate RDF model
    session = BMotifSession(ns='roundtrip')
    for cls in [Office, ConferenceRoom]:
        session.load_class_templates(cls)
    
    for space in building_spaces:
        session.evaluate(space)
    
    print(f"Step 2: Generated RDF with {len(session.graph)} triples")
    
    # Step 3: Save to file
    session.graph.serialize(destination='roundtrip_model.ttl', format='turtle')
    print("Step 3: Saved model to 'roundtrip_model.ttl'")
    
    # Step 4: Load from file
    loader = ModelLoader(source='roundtrip_model.ttl')
    loaded_offices = loader.load_instances(Office, ontology='s223')
    loaded_conf_rooms = loader.load_instances(ConferenceRoom, ontology='s223')
    
    print(f"Step 4: Loaded {len(loaded_offices)} offices, {len(loaded_conf_rooms)} conference rooms")
    
    # Step 5: Verify data integrity
    print("\nStep 5: Data integrity check:")
    original_total_area = sum(space.area.value for space in building_spaces)
    loaded_total_area = sum(space.area.value for space in loaded_offices + loaded_conf_rooms)
    
    print(f"  Original total area: {original_total_area} ft²")
    print(f"  Loaded total area: {loaded_total_area} ft²")
    print(f"  Data integrity: {'✅ PASS' if abs(original_total_area - loaded_total_area) < 0.01 else '❌ FAIL'}")
    
    return building_spaces, loaded_offices + loaded_conf_rooms


def main():
    """Run all advanced examples"""
    print("Semantic Objects - Advanced Patterns and Use Cases")
    print("=" * 60)
    
    try:
        # Run examples
        office, conf_room = example_1_custom_entities()
        spaces = example_2_inheritance_hierarchy()
        example_3_template_generation_advanced()
        graph, floor_spaces = example_4_complex_model_building()
        offices, conf_rooms = example_5_advanced_querying()
        smart_office = example_6_custom_properties()
        example_7_validation_and_constraints()
        original, loaded = example_8_round_trip_workflow()
        
        print("\n" + "=" * 60)
        print("✅ All advanced examples completed successfully!")
        print("=" * 60)
        
        print(f"\nSummary:")
        print(f"  Custom entities created: {len([office, conf_room, smart_office])}")
        print(f"  Spaces in complex model: {len(floor_spaces)}")
        print(f"  Round-trip objects: {len(original)} → {len(loaded)}")
        print(f"  Template files generated: advanced_templates/")
        print(f"  RDF model saved: roundtrip_model.ttl")
        
    except Exception as e:
        print(f"\n❌ Error running advanced examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()