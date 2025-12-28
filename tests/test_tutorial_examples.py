"""Test that tutorial examples work correctly with optional fields"""

from typing import Optional
from semantic_objects.core import semantic_object, Node
from semantic_objects.fields import required_field, optional_field
from semantic_objects.s223.properties import Power, Area, QuantifiableObservableProperty
from semantic_objects.qudt import quantitykinds


@semantic_object
class PowerMeasurement(QuantifiableObservableProperty):
    qk = quantitykinds.Power
    _semantic_type = QuantifiableObservableProperty


@semantic_object
class PowerMeter(Node):
    label = "Power Meter"
    comment = "A device that measures electrical power"
    
    # Required power reading
    power: PowerMeasurement = required_field()
    
    # Optional location description
    location: Optional[str] = optional_field(relation=None)
    
    def __post_init__(self):
        """Convert raw power values to PowerMeasurement objects"""
        super().__post_init__()
        if not isinstance(self.power, PowerMeasurement):
            self.power = PowerMeasurement(self.power)


def test_tutorial_power_meter():
    """Test the PowerMeter example from the tutorial"""
    # Test with optional field
    meter1 = PowerMeter(power=1500.0, location="Office 101")
    assert meter1.location == "Office 101"
    assert isinstance(meter1.power, PowerMeasurement)
    assert meter1.power.value == 1500.0
    print("✓ PowerMeter with location works")
    
    # Test without optional field
    meter2 = PowerMeter(power=2000.0)
    assert meter2.location is None
    assert isinstance(meter2.power, PowerMeasurement)
    assert meter2.power.value == 2000.0
    print("✓ PowerMeter without location works")


@semantic_object
class EnvironmentalStation(Node):
    label = "Environmental Station"
    comment = "A comprehensive environmental monitoring station"
    
    power_consumption: Power = required_field()
    coverage_area: Area = required_field()
    
    # Optional fields
    station_id: Optional[str] = optional_field(relation=None)
    
    def __post_init__(self):
        """Convert raw values to proper property types"""
        super().__post_init__()
        
        if not isinstance(self.power_consumption, Power):
            self.power_consumption = Power(self.power_consumption)
        if not isinstance(self.coverage_area, Area):
            self.coverage_area = Area(self.coverage_area)


def test_tutorial_environmental_station():
    """Test the EnvironmentalStation example from the tutorial"""
    # Test with optional field
    station1 = EnvironmentalStation(
        power_consumption=2500.0,
        coverage_area=100.0,
        station_id="ENV001"
    )
    assert station1.station_id == "ENV001"
    assert isinstance(station1.power_consumption, Power)
    assert isinstance(station1.coverage_area, Area)
    print("✓ EnvironmentalStation with station_id works")
    
    # Test without optional field
    station2 = EnvironmentalStation(
        power_consumption=3000.0,
        coverage_area=150.0
    )
    assert station2.station_id is None
    assert isinstance(station2.power_consumption, Power)
    assert isinstance(station2.coverage_area, Area)
    print("✓ EnvironmentalStation without station_id works")


if __name__ == "__main__":
    test_tutorial_power_meter()
    test_tutorial_environmental_station()
    print("\n🎉 All tutorial examples work correctly with optional fields!")