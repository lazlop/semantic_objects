#!/usr/bin/env python3
"""
Test script for EnvironmentalStation class template export
"""

from typing import Optional
from src.semantic_objects.s223.properties import EnvironmentalStation, PowerConsumption, AirPressure
from src.semantic_objects.exporters import export_templates
from src.semantic_objects.build_model import BMotifSession
from src.semantic_objects.model_loader import ModelLoader

def test_environmental_station_creation():
    """Test creating an EnvironmentalStation instance"""
    print("=" * 60)
    print("Test 1: Creating EnvironmentalStation Instance")
    print("=" * 60)
    
    # Create an environmental station
    station = EnvironmentalStation(
        power_consumption=PowerConsumption(value=150.0),
        air_pressure=AirPressure(value=1013.25),
        station_id="ENV_001"
    )
    station._name = "Environmental_Station_1"
    
    print(f"Created station: {station._name}")
    print(f"  Power consumption: {station.power_consumption.value} {station.power_consumption.unit}")
    print(f"  Air pressure: {station.air_pressure.value} {station.air_pressure.unit}")
    print(f"  Station ID: {station.station_id}")
    
    return station

def test_template_generation():
    """Test generating YAML template for EnvironmentalStation"""
    print("\n" + "=" * 60)
    print("Test 2: Template Generation")
    print("=" * 60)
    
    try:
        # Generate YAML template
        yaml_template_dict = EnvironmentalStation.generate_yaml_template()
        print("✅ Successfully generated YAML template")
        print("\nTemplate preview:")
        
        # Convert to YAML string for display
        import yaml
        yaml_string = yaml.dump(yaml_template_dict, default_flow_style=False)
        lines = yaml_string.split('\n')
        for i, line in enumerate(lines[:20]):
            print(f"  {i+1:2d}: {line}")
        if len(lines) > 20:
            print(f"  ... ({len(lines) - 20} more lines)")
        
        return yaml_template_dict
    except Exception as e:
        print(f"❌ Error generating template: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_template_dependencies():
    """Test getting template dependencies"""
    print("\n" + "=" * 60)
    print("Test 3: Template Dependencies")
    print("=" * 60)
    
    try:
        deps = EnvironmentalStation.get_dependencies()
        print(f"Found {len(deps)} dependencies:")
        for dep in deps:
            print(f"  - {dep['template'].__name__}: {dep['args']}")
        
        return deps
    except Exception as e:
        print(f"❌ Error getting dependencies: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_optional_fields():
    """Test optional field handling"""
    print("\n" + "=" * 60)
    print("Test 4: Optional Fields")
    print("=" * 60)
    
    try:
        optional_fields = EnvironmentalStation.get_optional_fields()
        print(f"Optional fields: {optional_fields}")
        
        # Test creating station without optional field
        station_no_id = EnvironmentalStation(
            power_consumption=PowerConsumption(value=100.0),
            air_pressure=AirPressure(value=1000.0)
        )
        station_no_id._name = "Station_No_ID"
        
        print(f"Created station without ID: {station_no_id._name}")
        print(f"  Station ID: {station_no_id.station_id}")
        
        return optional_fields
    except Exception as e:
        print(f"❌ Error testing optional fields: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_bmotif_integration():
    """Test integration with BMotif session"""
    print("\n" + "=" * 60)
    print("Test 5: BMotif Integration")
    print("=" * 60)
    
    try:
        # Create BMotif session
        session = BMotifSession(ns='test_env_station')
        
        # Load class templates
        session.load_class_templates(EnvironmentalStation)
        print(f"Loaded templates: {list(session.templates.keys())}")
        
        # Create and evaluate station
        station = EnvironmentalStation(
            power_consumption=PowerConsumption(value=200.0),
            air_pressure=AirPressure(value=1020.0),
            station_id="BMOTIF_001"
        )
        station._name = "BMotif_Station"
        
        session.evaluate(station)
        print(f"✅ Successfully evaluated station in BMotif")
        print(f"Generated {len(session.graph)} triples")
        
        return session.graph
    except Exception as e:
        print(f"❌ Error in BMotif integration: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_round_trip():
    """Test round-trip: create -> serialize -> load"""
    print("\n" + "=" * 60)
    print("Test 6: Round-Trip Test")
    print("=" * 60)
    
    try:
        # Create and serialize
        graph = test_bmotif_integration()
        if graph is None:
            print("❌ Cannot perform round-trip test - BMotif integration failed")
            return
        
        # Save to file
        graph.serialize(destination='test_env_station.ttl', format='turtle')
        print("✅ Saved model to test_env_station.ttl")
        
        # Debug: Check what SPARQL query is generated
        try:
            sparql_query = EnvironmentalStation.get_sparql_query(ontology='s223')
            print(f"\nGenerated SPARQL query:")
            print(sparql_query)
        except Exception as e:
            print(f"Error generating SPARQL query: {e}")
        
        # Load back
        loader = ModelLoader(source='test_env_station.ttl')
        loaded_stations = loader.load_instances(EnvironmentalStation, ontology='s223')
        
        print(f"✅ Loaded {len(loaded_stations)} stations from file")
        
        for station in loaded_stations:
            print(f"  Station: {station._name}")
            print(f"    Power: {station.power_consumption.value} {station.power_consumption.unit}")
            print(f"    Pressure: {station.air_pressure.value} {station.air_pressure.unit}")
            print(f"    ID: {station.station_id}")
        
        return loaded_stations
    except Exception as e:
        print(f"❌ Error in round-trip test: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_export_templates():
    """Test exporting templates to files"""
    print("\n" + "=" * 60)
    print("Test 7: Export Templates")
    print("=" * 60)
    
    try:
        export_templates([EnvironmentalStation], 'environmental_station_templates')
        print("✅ Successfully exported templates to environmental_station_templates/")
        return True
    except Exception as e:
        print(f"❌ Error exporting templates: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Environmental Station Template Export Test")
    print("=" * 60)
    
    results = {}
    
    # Run tests
    results['creation'] = test_environmental_station_creation()
    results['template'] = test_template_generation()
    results['dependencies'] = test_template_dependencies()
    results['optional'] = test_optional_fields()
    results['bmotif'] = test_bmotif_integration()
    results['roundtrip'] = test_round_trip()
    results['export'] = test_export_templates()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    success_count = 0
    total_tests = len(results)
    
    for test_name, result in results.items():
        if result is not None and result != [] and result != False:
            print(f"✅ {test_name}: PASS")
            success_count += 1
        else:
            print(f"❌ {test_name}: FAIL")
    
    print(f"\nOverall: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed - check output above for details")

if __name__ == "__main__":
    main()