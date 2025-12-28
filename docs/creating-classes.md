# Creating Custom Semantic Object Classes

This guide explains how to create your own semantic object classes using the patterns established in the library.

## Overview

The Semantic Objects library uses a decorator-based approach to define semantic classes. All classes use the `@semantic_object` decorator and follow specific inheritance patterns.

## Basic Patterns

### Entity Classes

Entity classes represent physical or logical objects and inherit from `Node`:

```python
from semantic_objects.core import semantic_object, Node, required_field
from semantic_objects.fields import optional_field
from typing import Optional

@semantic_object
class TemperatureSensor(Node):
    label = "Temperature Sensor"
    comment = "A sensor that measures temperature"
    
    # Required properties
    temperature: Temperature = required_field()
    
    # Optional properties
    location: Optional[str] = optional_field(relation=None)
    
    def __post_init__(self):
        """Convert raw values to proper types"""
        super().__post_init__()
        if not isinstance(self.temperature, Temperature):
            self.temperature = Temperature(self.temperature)
```

### Property Classes

Property classes represent measurable attributes and inherit from `QuantifiableObservableProperty`:

```python
from semantic_objects.s223.properties import QuantifiableObservableProperty
from semantic_objects.qudt import quantitykinds

@semantic_object
class Temperature(QuantifiableObservableProperty):
    qk = quantitykinds.Temperature
    _semantic_type = QuantifiableObservableProperty
```

### Property Classes with Fixed Units

```python
from semantic_objects.qudt import units

@semantic_object
class Temperature_Celsius(Temperature):
    unit = units.DEG_C
    _semantic_type = QuantifiableObservableProperty
```

## Inheritance Hierarchies

Create hierarchies by inheriting from existing classes:

```python
@semantic_object
class Equipment(Node):
    label = "Equipment"
    abstract = True  # Base class, not instantiated directly
    
    power: Power = required_field()

@semantic_object
class HVACEquipment(Equipment):
    label = "HVAC Equipment"
    abstract = True

@semantic_object
class AirHandlingUnit(HVACEquipment):
    label = "Air Handling Unit"
    
    supply_temperature: Temperature = required_field()
    return_temperature: Temperature = required_field()
```

## Relationships Between Classes

### Simple Relations

```python
@semantic_object
class MechanicalRoom(Space):
    equipment: List[Equipment] = optional_field(relation=contains)
```

### Inter-Field Relations

```python
from semantic_objects.fields import inter_field_relation

@semantic_object
class ZoneWithSensor(Space):
    zone: Space = required_field(relation=hasDomainSpace)
    sensor: TemperatureSensor = required_field(relation=hasPoint)
    
    # Define relationship between fields
    _inter_field_relations = [
        inter_field_relation(
            source_field='zone',
            relation=contains,
            target_field='sensor',
            min=1,
            max=1
        )
    ]
```

## Advanced Patterns

### Mixins for Common Functionality

```python
@semantic_object
class OperationalMixin(Node):
    abstract = True
    
    is_operational: Optional[bool] = optional_field(relation=None)
    last_maintenance: Optional[str] = optional_field(relation=None)

@semantic_object
class SmartThermostat(OperationalMixin, Node):
    current_temperature: Temperature = required_field()
    setpoint_temperature: Temperature = required_field()
```

### Factory Methods

```python
@semantic_object
class BuildingFloor(Node):
    floor_number: int = field(metadata={'relation': None})
    spaces: List[Space] = field(default_factory=list, metadata={'relation': contains})
    
    @classmethod
    def create_office_floor(cls, floor_number: int, num_offices: int, office_area: float):
        spaces = []
        for i in range(num_offices):
            office = Space(area=office_area)
            office._name = f"Office_{floor_number}{i+1:02d}"
            spaces.append(office)
        
        floor = cls(floor_number=floor_number, spaces=spaces)
        floor._name = f"Floor_{floor_number}"
        return floor
```

## Key Decorator Features

The `@semantic_object` decorator:

1. **Converts to dataclass**: Automatically applies `@dataclass`
2. **Handles inheritance**: Merges fields from parent classes
3. **Sets defaults**: Provides `_name` and `abstract` attributes
4. **Manages metadata**: Preserves field metadata for relations

## Working with Optional Fields

Use the `optional_field()` function for optional properties:

```python
from semantic_objects.fields import optional_field

@semantic_object
class MyEntity(Node):
    # Required field
    required_prop: SomeProperty = required_field()
    
    # Optional fields
    optional_string: Optional[str] = optional_field(relation=None)
    optional_with_relation: Optional[OtherEntity] = optional_field(relation=someRelation)
```

**Key benefits of `optional_field()`:**
- Automatically sets `default=None` and `init=True`
- Properly marks the field as optional in metadata
- Accepts keyword arguments at instantiation
- Works correctly with inheritance

## Best Practices

### ✅ Do's

1. Always use `@semantic_object` decorator
2. Inherit from appropriate base classes (`Node`, `QuantifiableObservableProperty`, etc.)
3. Define clear `label` and `comment` attributes
4. Use `required_field()` for mandatory properties
5. Implement `__post_init__` for type conversion
6. Set `abstract = True` for base classes

### ❌ Don'ts

1. Don't forget the decorator
2. Don't create circular dependencies
3. Don't ignore type hints
4. Don't mix relation patterns inconsistently

## Complete Example

```python
from semantic_objects.core import *
from semantic_objects.s223 import *
from semantic_objects.qudt import quantitykinds, units

# Custom property using supported quantity kind
@semantic_object
class PowerConsumption(QuantifiableObservableProperty):
    qk = quantitykinds.Power
    _semantic_type = QuantifiableObservableProperty

# Custom entity
@semantic_object
class EnergyMonitor(Node):
    label = "Energy Monitor"
    comment = "A comprehensive energy monitoring device"
    
    power_consumption: PowerConsumption = required_field()
    air_pressure: AirPressure = required_field()
    device_id: Optional[str] = field(default=None, metadata={'relation': None})
    
    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.power_consumption, PowerConsumption):
            self.power_consumption = PowerConsumption(self.power_consumption)
        if not isinstance(self.air_pressure, AirPressure):
            self.air_pressure = AirPressure(self.air_pressure)

# Usage
monitor = EnergyMonitor(
    power_consumption=2500.0,
    air_pressure=101325.0,
    device_id="EM001"
)
```

## Next Steps

- See the [Class Creation Tutorial](../tutorial/class-creation-tutorial.ipynb) for interactive examples
- Check the [Basic Tutorial](../tutorial/basic-tutorial.ipynb) for foundational concepts
- Explore existing classes in `src/semantic_objects/s223/` for more patterns