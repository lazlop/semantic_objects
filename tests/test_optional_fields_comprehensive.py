"""Comprehensive test for optional fields functionality"""

from typing import Optional, List
from semantic_objects.core import semantic_object, Node
from semantic_objects.fields import required_field, optional_field
from semantic_objects.s223.properties import Power, Area
from semantic_objects.s223.relations import label, contains


@semantic_object
class SimpleDevice(Node):
    """Simple device with optional fields"""
    label = "Simple Device"
    
    # Required field
    power: Power = required_field()
    
    # Optional fields of different types
    device_id: Optional[str] = optional_field(relation=label)
    description: Optional[str] = optional_field(relation=None)
    is_active: Optional[bool] = optional_field(relation=None)
    priority: Optional[int] = optional_field(relation=None)
    
    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.power, Power):
            self.power = Power(self.power)


@semantic_object
class ComplexDevice(Node):
    """Device with optional list fields"""
    label = "Complex Device"
    
    # Required field
    main_area: Area = required_field()
    
    # Optional simple fields (avoid complex generic types for now)
    device_name: Optional[str] = optional_field(relation=None)
    max_capacity: Optional[float] = optional_field(relation=None)
    
    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.main_area, Area):
            self.main_area = Area(self.main_area)


def test_simple_optional_fields():
    """Test simple optional fields with different types"""
    print("Testing simple optional fields...")
    
    # Test with all optional fields provided
    device1 = SimpleDevice(
        power=1000.0,
        device_id="DEV001",
        description="Test device",
        is_active=True,
        priority=1
    )
    
    assert device1.device_id == "DEV001"
    assert device1.description == "Test device"
    assert device1.is_active is True
    assert device1.priority == 1
    print("✓ All optional fields set correctly")
    
    # Test with no optional fields
    device2 = SimpleDevice(power=1000.0)
    
    assert device2.device_id is None
    assert device2.description is None
    assert device2.is_active is None
    assert device2.priority is None
    print("✓ Optional fields default to None correctly")
    
    # Test with some optional fields
    device3 = SimpleDevice(
        power=1000.0,
        device_id="DEV003",
        is_active=False
    )
    
    assert device3.device_id == "DEV003"
    assert device3.description is None
    assert device3.is_active is False
    assert device3.priority is None
    print("✓ Partial optional fields work correctly")


def test_optional_list_fields():
    """Test optional fields with different types"""
    print("\nTesting optional fields with different types...")
    
    # Test with optional fields provided
    device1 = ComplexDevice(
        main_area=100.0,
        device_name="Complex Device 1",
        max_capacity=500.0
    )
    
    assert device1.device_name == "Complex Device 1"
    assert device1.max_capacity == 500.0
    print("✓ Optional fields with different types set correctly")
    
    # Test with no optional fields
    device2 = ComplexDevice(main_area=100.0)
    
    assert device2.device_name is None
    assert device2.max_capacity is None
    print("✓ Optional fields default to None correctly")


def test_optional_field_metadata():
    """Test that optional field metadata is set correctly"""
    print("\nTesting optional field metadata...")
    
    # Check that optional fields have correct metadata
    device_fields = SimpleDevice.__dataclass_fields__
    
    # Required field should not have optional=True
    power_field = device_fields['power']
    assert power_field.metadata.get('optional') != True
    print("✓ Required field does not have optional=True")
    
    # Optional fields should have optional=True
    device_id_field = device_fields['device_id']
    assert device_id_field.metadata.get('optional') == True
    assert device_id_field.default is None
    assert device_id_field.init is True
    print("✓ Optional field has correct metadata")
    
    description_field = device_fields['description']
    assert description_field.metadata.get('optional') == True
    assert description_field.metadata.get('relation') is None
    print("✓ Optional field with relation=None has correct metadata")


def test_optional_field_inheritance():
    """Test that optional fields work with inheritance"""
    print("\nTesting optional field inheritance...")
    
    @semantic_object
    class ExtendedDevice(SimpleDevice):
        """Extended device with additional optional field"""
        
        # Additional optional field
        location: Optional[str] = optional_field(relation=None)
    
    device = ExtendedDevice(
        power=1500.0,
        device_id="EXT001",
        location="Building A"
    )
    
    # Check inherited optional fields
    assert device.device_id == "EXT001"
    assert device.description is None  # Not provided
    
    # Check new optional field
    assert device.location == "Building A"
    
    print("✓ Optional fields work correctly with inheritance")


if __name__ == "__main__":
    test_simple_optional_fields()
    test_optional_list_fields()
    test_optional_field_metadata()
    test_optional_field_inheritance()
    print("\n🎉 All comprehensive optional field tests passed!")