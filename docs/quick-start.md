# Quick Start Guide

Get up and running with Semantic Objects in 5 minutes!

## Installation

```bash
pip install semantic-objects
# or with optional dependencies
pip install semantic-objects[buildingmotif]
```

## Basic Usage

### 1. Use the Ontology-Generated Classes

`semantic_objects.s223` classes are generated from the real ASHRAE 223P ontology's
SHACL shapes (`python -m semantic_objects.ingest.cli --ontology s223`), not
hand-typed. See `tutorial/s223-generated-classes-tutorial.ipynb` for the full walkthrough.

```python
from semantic_objects.s223 import entities, enumerationkinds

# DomainSpace is a real ontology class - `domain` is required (min=1, max=1)
zone = entities.DomainSpace(domain=enumerationkinds.HVAC())

# Pump demonstrates qualified fields: two connection points sharing the same
# `hasConnectionPoint` relation, narrowed to specific subtypes by the ontology
water = enumerationkinds.Water()
connection = entities.Connection(medium=water)
pump = entities.Pump(
    outlet_connection_point=entities.OutletConnectionPoint(medium=water, connection=connection),
    inlet_connection_point=entities.InletConnectionPoint(medium=water, connection=connection),
)

print(f"{zone._name}: domain={zone.domain._name}")
print(f"{pump._name}: outlet medium={pump.outlet_connection_point.medium._name}")
```

### 2. Load Data from RDF Graphs

```python
from semantic_objects.model_loader import ModelLoader
from semantic_objects.s223 import entities
from rdflib import Graph

# Load an RDF graph
graph = Graph()
graph.parse("building_model.ttl")

# Initialize loader and load spaces
loader = ModelLoader(source=graph)
spaces = loader.load_instances(entities.DomainSpace, ontology='s223')

# Work with loaded objects
for space in spaces:
    print(f"Loaded space: {space._name}")
```

### 3. Generate Templates

```python
from semantic_objects.exporters import export_templates
from semantic_objects.s223 import entities

# Export templates for BuildingMOTIF
export_templates(entities.DomainSpace, 'templates/')

# This creates:
# templates/entities.yml
# templates/relations.yml  
# templates/values.yml
```

### 4. Build Models with BuildingMOTIF

```python
from semantic_objects.build_model import BMotifSession
from semantic_objects.s223 import entities, enumerationkinds

# Create session and load templates
session = BMotifSession()
session.load_class_templates(entities.DomainSpace)

# Create and evaluate a space
zone = entities.DomainSpace(domain=enumerationkinds.HVAC())
session.evaluate(zone)

# The RDF model is now in session.model.graph
print(session.model.graph.serialize(format='turtle'))
```

## Key Concepts

### Entities vs Properties

- **Entities**: Physical or logical objects (`DomainSpace`, `Pump`, `Equipment`) - generated from ontology classes into `s223/_generated/entities.py`
- **Properties**: Attributes with values and units (`Area`, `Power`) - the `Property`/`QuantifiableObservableProperty` hierarchy is generated too, but `qk`/`value`/`unit` and concrete quantity-kind leaves like `Area` are hand-written on top (see `s223/properties.py`) since they come from the QUDT namespace, which this pipeline doesn't ingest

```python
from semantic_objects.s223.properties import Area

# Properties have quantity kinds and units
area = Area(100.0)
print(area.qk)     # Area quantity kind
print(area.unit)   # M2 (default unit)
print(area.value)  # 100.0
```

### Field Types

- `required_field()`: Must be provided, creates SHACL constraints
- `optional_field()`: Optional for templates, used in queries
- `exclusive_field()`: Exactly one value (min=1, max=1)

```python
from semantic_objects.core import semantic_object
from semantic_objects.fields import required_field, optional_field
from semantic_objects.s223 import entities
from semantic_objects.s223.properties import Area

@semantic_object
class ZoneWithExtraArea(entities.DomainSpace):
    conditioned_area: Area = required_field()    # Required
    unconditioned_area: Area = optional_field()  # Optional
```

### Automatic Features

The library automatically:
- Generates SPARQL queries from class definitions
- Creates SHACL shapes for validation
- Infers relations between objects
- Sets default units for properties
- Handles type conversion and validation

## Next Steps

1. **Learn More**: Read the [Core Concepts](core-concepts.md) guide
2. **Interactive Tutorial**: Work through the [Working with Generated Classes](../tutorial/s223-generated-classes-tutorial.ipynb)
3. **Advanced Usage**: Explore [Ontology Ingestion](../tutorial/ontology-ingestion-tutorial.ipynb)
4. **Custom Objects**: Learn to [create custom entities](guides/custom-entities.md)

## Common Patterns

### Loading Multiple Entity Types

```python
from semantic_objects.s223 import entities

# Load multiple classes at once
results = loader.load_multiple_classes({
    'zones': entities.DomainSpace,
    'pumps': entities.Pump,
}, ontology='s223')

zones = results['zones']
pumps = results['pumps']
```

### Working with Units

```python
from semantic_objects.s223.properties import Area
from semantic_objects.qudt.units import M2, FT2

# Explicit unit specification
area_metric = Area(100.0, unit=M2)
area_imperial = Area(100.0, unit=FT2)

# Default units are used if not specified
area_default = Area(100.0)  # Uses M2 by default (see qudt/defaults.py)
```

### Query Generation

```python
from semantic_objects.s223 import entities

# Generate SPARQL query for any Resource class
query = entities.DomainSpace.get_sparql_query(ontology='s223')
print(query)

# Execute query manually
from semantic_objects.model_loader import query_to_df
df = query_to_df(query, graph)
```

You're now ready to start using Semantic Objects! Check out the tutorials for more detailed examples.