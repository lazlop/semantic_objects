"""Test that optional fields can be provided as keyword arguments at instantiation"""

from typing import Optional
from semantic_objects.core import semantic_object, Node
from semantic_objects.fields import required_field, optional_field
from semantic_objects.s223.properties import Power, Area
from semantic_objects.s223.relations import label


@semantic_object
class EnvironmentalStation(Node):
    label = "Environmental Station"
    comment = "A comprehensive environmental monitoring station"
    
    power_consumption: Power = required_field()
    coverage_area: Area = required_field()
    
    # Optional fields
    station_id: Optional[str] = optional_field(relation=label)
    
    def __post_init__(self):
        """Convert raw values to proper property types"""
        super().__post_init__()
        
        if not isinstance(self.power_consumption, Power):
            self.power_consumption = Power(self.power_consumption)
        if not isinstance(self.coverage_area, Area):
            self.coverage_area = Area(self.coverage_area)


def test_optional_field_with_value():
    """Test that optional fields can be provided at instantiation"""
    # Create an environmental station with optional field
    station = EnvironmentalStation(
        power_consumption=2500.0,  # kW (default SI unit)
        coverage_area=100.0,       # m² (default SI unit)
        station_id="ENV001"
    )
    
    # Verify the optional field was set
    assert station.station_id == "ENV001"
    assert isinstance(station.power_consumption, Power)
    assert isinstance(station.coverage_area, Area)
    print(f"✓ Station created with station_id: {station.station_id}")


def test_optional_field_without_value():
    """Test that optional fields default to None when not provided"""
    # Create an environmental station without optional field
    station = EnvironmentalStation(
        power_consumption=2500.0,
        coverage_area=100.0
    )
    
    # Verify the optional field is None
    assert station.station_id is None
    assert isinstance(station.power_consumption, Power)
    assert isinstance(station.coverage_area, Area)
    print(f"✓ Station created without station_id (defaults to None)")


def test_optional_field_set_to_none():
    """Test that optional fields can be explicitly set to None"""
    # Create an environmental station with optional field explicitly set to None
    station = EnvironmentalStation(
        power_consumption=2500.0,
        coverage_area=100.0,
        station_id=None
    )
    
    # Verify the optional field is None
    assert station.station_id is None
    print(f"✓ Station created with station_id explicitly set to None")


if __name__ == "__main__":
    test_optional_field_with_value()
    test_optional_field_without_value()
    test_optional_field_set_to_none()
    print("\n✅ All optional field tests passed!")
