# Core Concepts

Understanding the fundamental concepts behind Semantic Objects will help you use the library effectively.

## Architecture Overview

Semantic Objects provides four main capabilities:

1. **Ontology Ingestion**: Parse an ontology's SHACL shapes into typed Python classes (`src/semantic_objects/ingest/`) - this is how `semantic_objects.s223` gets its ~576 entity/property/enumeration classes and ~60 relations, not hand-typing
2. **Generated + Override Classes**: Generated base classes live in `s223/_generated/`; the sibling `s223/entities.py`, `s223/properties.py`, etc. add hand-written customization that isn't derivable from SHACL, then re-export everything - see `tutorial/ontology-ingestion-tutorial.ipynb`
3. **Model Loading**: Query RDF graphs and instantiate Python objects
4. **Template Generation**: Create BuildingMOTIF templates and SHACL shapes

## Resource Hierarchy

All semantic objects inherit from the `Resource` base class:

```python
Resource                    # Base class for all semantic objects
├── Node                   # Concrete entities with auto-generated names
│   ├── DomainSpace        # Ontology-generated entities (s223/_generated/entities.py)
│   ├── Pump
│   └── Equipment
├── NamedNode             # Fixed-value nodes (units, enums)
│   ├── Unit              # FT2, M2, DEG, etc.
│   └── EnumerationKind   # Setpoint, Threshold, HVAC, etc.
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

`Node` represents concrete entities that can be instantiated. This is a hand-written
example (`examples/s223_framework_demo.py`); real ontology-generated `Node`
subclasses live in `s223/_generated/entities.py`:

```python
@semantic_object
class Room(Node):
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

Properties represent quantifiable attributes with values and units. The
`Property`/`ObservableProperty`/`QuantifiableProperty`/`QuantifiableObservableProperty`/
`EnumerableProperty` hierarchy is ontology-generated (`s223/_generated/properties.py`).
`qk`/`value`/`unit` are hand-added on top in `s223/properties.py` - the ontology
models those via QUDT-namespace relations (`qudt:hasQuantityKind`, `qudt:hasUnit`),
which this pipeline doesn't ingest. Concrete quantity-kind leaves are hand-written
the same way:

### Property Hierarchy

```python
Property (generated)
└── QuantifiableObservableProperty (generated, extended by hand with qk/value/unit)
    ├── Area      # hand-written leaf, s223/properties.py
    ├── Azimuth
    ├── Tilt
    └── Power
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
area1 = Area(100.0)  # 100.0 m² (default - see qudt/defaults.py)

# Create with explicit unit
from semantic_objects.qudt.units import M2, FT2
area2 = Area(100.0, unit=FT2)  # 100.0 ft²

# Access components
print(area1.value)  # 100.0
print(area1.unit)   # M2
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

The library automatically infers relations from field types. This is (simplified)
how the real, generated `DomainSpace` is defined:

```python
@semantic_object
class DomainSpace(Connectable):
    domain: Domain = required_field()  # Automatically uses hasDomain relation

# Equivalent to:
@semantic_object
class DomainSpace(Connectable):
    domain: Domain = required_field(relation=hasDomain)
```

## Template Generation

Semantic objects automatically generate BuildingMOTIF templates. This is the real
output for `entities.DomainSpace.to_yaml()`:

```yaml
DomainSpace:
  body: >+
    @prefix P: <urn:___param___#> .

    @prefix s223: <http://data.ashrae.org/standard223#> .


    P:name a s223:DomainSpace ;
        s223:hasDomain P:domain .

  dependencies:
  - args:
      name: domain
    template: Domain
```

### Template Parameters

Templates use parameters for flexible instantiation:

```python
# Get template parameters for a class
params = entities.DomainSpace._get_template_parameters()
# Returns: {'domain': Field(type=Domain, ...)}

# Generate template body
body = entities.DomainSpace.generate_turtle_body()
# Returns RDF/Turtle with param: placeholders
```

## SHACL Generation

Generate SHACL shapes for validation:

```python
# Generate SHACL shape with full hierarchy
shacl_full = entities.DomainSpace.generate_rdf_class_definition(include_hierarchy=True)

# Generate only local constraints
shacl_local = entities.DomainSpace.generate_rdf_class_definition(include_hierarchy=False)
```

### SHACL Features

- **Cardinality constraints**: From field min/max values
- **Type constraints**: From field type annotations
- **Qualified shapes**: For complex property constraints
- **Inheritance**: Includes parent class constraints

## Query Generation

Automatically generate SPARQL queries from class definitions:

```python
# Generate query for DomainSpace class
query = entities.DomainSpace.get_sparql_query(ontology='s223')

# Query includes:
# - Class type constraints (a s223:DomainSpace)
# - Property patterns (s223:hasDomain ?domain)
# - Property type constraints (?domain a s223:EnumerationKind-Domain)
```

## Ontology Support

### S223 (ASHRAE Standard 223P)

Classes are generated from the real ontology's SHACL shapes - see
`tutorial/ontology-ingestion-tutorial.ipynb` for how, and
`tutorial/s223-generated-classes-tutorial.ipynb` for a full usage walkthrough:

```python
from semantic_objects.s223 import entities, properties, enumerationkinds

# Entities (ontology-generated)
zone = entities.DomainSpace(domain=enumerationkinds.HVAC())

water = enumerationkinds.Water()
connection = entities.Connection(medium=water)
pump = entities.Pump(
    outlet_connection_point=entities.OutletConnectionPoint(medium=water, connection=connection),
    inlet_connection_point=entities.InletConnectionPoint(medium=water, connection=connection),
)

# Properties with quantity kinds (qk/value/unit hand-added on generated base - see s223/properties.py)
area = properties.Area(100.0)        # Area quantity kind
power = properties.Power(500.0)      # Power quantity kind
```

### QUDT (Quantities, Units, Dimensions, Types)

Comprehensive unit and quantity kind support:

```python
from semantic_objects.qudt import quantitykinds, units

# Quantity kinds
area_qk = quantitykinds.Area
temp_qk = quantitykinds.Temperature  # a QuantityKind marker exists, but there's
                                      # no hand-written Temperature *property* leaf
                                      # yet in s223/properties.py - add one the same
                                      # way Area/Power are defined, if you need it

# Units
ft2 = units.FT2
m2 = units.M2
psi = units.PSI
pa = units.PA
```

## Best Practices

These examples subclass `entities.DomainSpace` (real, ontology-generated) to show
customization patterns - the same patterns apply whether you're extending a
generated class or a hand-written one.

### 1. Use Type Hints

```python
from typing import Optional, List
from semantic_objects.s223 import entities

@semantic_object
class MyZone(entities.DomainSpace):
    extra_area: Area = required_field()
    notes: Optional[Area] = optional_field()
```

### 2. Implement __post_init__ for Validation

```python
@semantic_object
class MyZone(entities.DomainSpace):
    extra_area: Area = required_field()

    def __post_init__(self):
        super().__post_init__()
        # Convert raw values to proper types
        if not isinstance(self.extra_area, Area):
            self.extra_area = Area(self.extra_area)
        # Add validation logic
        if self.extra_area.value <= 0:
            raise ValueError("Area must be positive")
```

### 3. Use Descriptive Metadata

```python
@semantic_object
class MyZone(entities.DomainSpace):
    extra_area: Area = required_field(
        label="Extra Area",
        comment="Additional floor area associated with this zone"
    )
```

### 4. Leverage Inheritance

```python
@semantic_object
class ConditionedZone(entities.DomainSpace):
    """Zone with HVAC conditioning"""
    design_power: Power = required_field()

@semantic_object
class Office(ConditionedZone):
    """Office zone with occupancy"""
    occupancy: Domain = required_field()
```

## Next Steps

- **Hands-on Practice**: Work through the [Working with Generated Classes](../tutorial/s223-generated-classes-tutorial.ipynb)
- **Model Loading**: Learn about [the ontology ingestion pipeline](../tutorial/ontology-ingestion-tutorial.ipynb)
- **Custom Entities**: Create [custom semantic objects](guides/custom-entities.md)
- **API Reference**: Explore the [detailed API documentation](api/)