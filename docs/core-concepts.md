# Core Concepts

Understanding the fundamental concepts behind Semantic Objects will help you use the library effectively.

## Architecture Overview

Semantic Objects provides three main capabilities:

1. **Model Creation**: Define semantic objects as Python dataclasses
2. **Model Loading**: Query RDF graphs and instantiate Python objects  
3. **Template Generation**: Create BuildingMOTIF templates and SHACL shapes

## Resource Hierarchy

All semantic objects inherit from the `Resource` base class:

```python
Resource                    # Base class for all semantic objects
├── Node                   # Concrete entities with auto-generated names
│   ├── Space             # Domain-specific entities
│   ├── Window
│   └── Equipment
├── NamedNode             # Fixed-value nodes (units, enums)
│   ├── Unit              # FT2, M2, DEG, etc.
│   └── EnumerationKind   # Setpoint, Deadband, etc.
└── Predicate             # Relations between entities
    ├── hasProperty
    ├── connectedTo
    └── contains
```

### Resource Base Class

The `Resource` class provides core functionality:

```python
@semantic_object
class MyEntity(Resource):
    _name = 'MyEntity'           # RDF type name
    _ns = S223                   # Namespace
    templatize = True            # Include in templates
    abstract = False             # Can be instantiated
```

### Node Classes

`Node` represents concrete entities that can be instantiated:

```python
@semantic_object
class Space(Node):
    area: Area = required_field()
    
    def __post_init__(self):
        # Custom initialization logic
        super().__post_init__()
        if not isinstance(self.area, Area):
            self.area = Area(self.area)
```

### NamedNode Classes

`NamedNode` represents fixed-value concepts like units:

```python
@semantic_object
class FT2(NamedNode):
    _name = 'FT2'
    label = "square foot"
    symbol = "ft²"
```

## Field Definition System

Fields define the structure and constraints of semantic objects:

### Field Types

```python
# Required field - must be provided, creates SHACL sh:minCount 1
area: Area = required_field()

# Optional field - for templates and queries, not required
volume: Volume = optional_field()

# Exclusive field - exactly one value (min=1, max=1)  
zone_type: ZoneType = exclusive_field()

# Custom constraints
temperature: Temperature = required_field(min=1, max=3)
```

### Field Metadata

Fields carry metadata for template generation and validation:

```python
area: Area = required_field(
    relation=hasProperty,     # Custom relation (auto-inferred if None)
    min=1,                   # Minimum cardinality
    max=None,                # Maximum cardinality (None = unlimited)
    qualified=True,          # Use qualified value shapes in SHACL
    label="Floor Area",      # Human-readable label
    comment="Total floor area of the space"  # Description
)
```

## Property System

Properties represent quantifiable attributes with values and units:

### Property Hierarchy

```python
Property                           # Base property class
└── QuantifiableObservableProperty # Properties with values and units
    ├── Area                      # Specific property types
    ├── Temperature
    ├── Pressure
    └── Flow
```

### Property Definition

```python
@semantic_object
class Area(QuantifiableObservableProperty):
    qk = quantitykinds.Area        # Quantity kind (what it measures)
    # Inherits: value, unit fields from parent
```

### Property Usage

```python
# Create with value only (uses default unit)
area1 = Area(100.0)  # 100.0 ft² (default)

# Create with explicit unit
from semantic_objects.qudt.units import M2
area2 = Area(100.0, unit=M2)  # 100.0 m²

# Access components
print(area1.value)  # 100.0
print(area1.unit)   # FT2 
print(area1.qk)     # Area quantity kind
```

## Relation System

Relations define how entities connect to each other:

### Relation Types

```python
@semantic_object
class hasProperty(Predicate):
    """Relates an entity to its properties"""
    pass

@semantic_object  
class connectedTo(Predicate):
    """Physical or logical connection between entities"""
    pass

@semantic_object
class contains(Predicate):
    """Containment relationship"""
    pass
```

### Automatic Relation Inference

The library automatically infers relations from field types:

```python
@semantic_object
class Space(Node):
    area: Area = required_field()  # Automatically uses hasProperty relation
    
# Equivalent to:
@semantic_object  
class Space(Node):
    area: Area = required_field(relation=hasProperty)
```

## Template Generation

Semantic objects automatically generate BuildingMOTIF templates:

### Template Structure

```yaml
Space:
  body: |
    @prefix s223: <http://data.ashrae.org/standard223#> .
    @prefix param: <urn:___param___#> .
    
    param:name a s223:Space ;
        s223:hasProperty param:area .
  dependencies:
    - template: Area
      args: {name: area}
```

### Template Parameters

Templates use parameters for flexible instantiation:

```python
# Get template parameters for a class
params = Space._get_template_parameters()
# Returns: {'area': Field(type=Area, ...)}

# Generate template body
body = Space.generate_turtle_body()
# Returns RDF/Turtle with param: placeholders
```

## SHACL Generation

Generate SHACL shapes for validation:

```python
# Generate SHACL shape with full hierarchy
shacl_full = Space.generate_rdf_class_definition(include_hierarchy=True)

# Generate only local constraints  
shacl_local = Space.generate_rdf_class_definition(include_hierarchy=False)
```

### SHACL Features

- **Cardinality constraints**: From field min/max values
- **Type constraints**: From field type annotations
- **Qualified shapes**: For complex property constraints
- **Inheritance**: Includes parent class constraints

## Query Generation

Automatically generate SPARQL queries from class definitions:

```python
# Generate query for Space class
query = Space.get_sparql_query(ontology='s223')

# Query includes:
# - Class type constraints (a s223:Space)
# - Property patterns (s223:hasProperty ?area)
# - Property type constraints (?area a s223:QuantifiableObservableProperty)
# - Quantity kind filters (for s223 ontology)
```

## Ontology Support

### S223 (ASHRAE Standard 223P)

Complete implementation of ASHRAE 223P concepts:

```python
from semantic_objects.s223 import *

# Entities
space = Space(area=100.0)
window = Window(area=10.0, azimuth=180.0, tilt=90.0)

# Relations  
space.windows = [window]  # Uses hasWindow relation

# Properties with quantity kinds
area = Area(100.0)        # Area quantity kind
temp = Temperature(72.0)  # Temperature quantity kind
```

### QUDT (Quantities, Units, Dimensions, Types)

Comprehensive unit and quantity kind support:

```python
from semantic_objects.qudt import quantitykinds, units

# Quantity kinds
area_qk = quantitykinds.Area
temp_qk = quantitykinds.Temperature

# Units
ft2 = units.FT2
m2 = units.M2
celsius = units.DEG_C
fahrenheit = units.DEG_F
```

## Best Practices

### 1. Use Type Hints

```python
from typing import Optional, List

@semantic_object
class Space(Node):
    area: Area = required_field()
    windows: Optional[List[Window]] = optional_field()
```

### 2. Implement __post_init__ for Validation

```python
@semantic_object
class Space(Node):
    area: Area = required_field()
    
    def __post_init__(self):
        super().__post_init__()
        # Convert raw values to proper types
        if not isinstance(self.area, Area):
            self.area = Area(self.area)
        # Add validation logic
        if self.area.value <= 0:
            raise ValueError("Area must be positive")
```

### 3. Use Descriptive Metadata

```python
@semantic_object
class Space(Node):
    area: Area = required_field(
        label="Floor Area",
        comment="Total conditioned floor area of the space in square feet"
    )
```

### 4. Leverage Inheritance

```python
@semantic_object
class ConditionedSpace(Space):
    """Space with HVAC conditioning"""
    design_temperature: Temperature = required_field()

@semantic_object  
class Office(ConditionedSpace):
    """Office space with occupancy"""
    occupancy: Occupancy = required_field()
```

## Next Steps

- **Hands-on Practice**: Work through the [Basic Tutorial](../tutorial/basic-tutorial.ipynb)
- **Model Loading**: Learn about [loading RDF data](../tutorial/model-loading-tutorial.ipynb)
- **Custom Entities**: Create [custom semantic objects](guides/custom-entities.md)
- **API Reference**: Explore the [detailed API documentation](api/)