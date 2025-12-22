# Quick Start Guide

Get up and running with Semantic Objects in 5 minutes!

## Installation

```bash
pip install semantic-objects
# or with optional dependencies
pip install semantic-objects[buildingmotif]
```

## Basic Usage

### 1. Define Semantic Objects

```python
from semantic_objects.s223 import Space, Window, Area, Azimuth, Tilt

# Create a space with area
space = Space(area=100.0)  # Area in default units (ft²)

# Create a window with multiple properties
window = Window(
    area=10.0,      # ft²
    azimuth=180.0,  # degrees (south-facing)
    tilt=90.0       # degrees (vertical)
)

print(f"Space area: {space.area.value} {space.area.unit}")
print(f"Window facing: {window.azimuth.value}° azimuth")
```

### 2. Load Data from RDF Graphs

```python
from semantic_objects.model_loader import ModelLoader
from rdflib import Graph

# Load an RDF graph
graph = Graph()
graph.parse("building_model.ttl")

# Initialize loader and load spaces
loader = ModelLoader(source=graph)
spaces = loader.load_instances(Space, ontology='s223')

# Work with loaded objects
for space in spaces:
    print(f"Loaded space: {space._name}")
    if space.area:
        print(f"  Area: {space.area.value} {space.area.unit}")
```

### 3. Generate Templates

```python
from semantic_objects.core import export_templates

# Export templates for BuildingMOTIF
export_templates(Space, 'templates/')

# This creates:
# templates/entities.yml
# templates/relations.yml  
# templates/values.yml
```

### 4. Build Models with BuildingMOTIF

```python
from semantic_objects.build_model import BMotifSession

# Create session and load templates
session = BMotifSession()
session.load_class_templates(Space)

# Create and evaluate a space
space = Space(area=150.0)
session.evaluate(space)

# The RDF model is now in session.graph
print(session.graph.serialize(format='turtle'))
```

## Key Concepts

### Entities vs Properties

- **Entities**: Physical or logical objects (Space, Window, Equipment)
- **Properties**: Attributes with values and units (Area, Temperature, Pressure)

```python
# Entity with properties
space = Space(area=Area(100.0))  # Space is entity, Area is property

# Properties have quantity kinds and units
print(space.area.qk)    # Area quantity kind
print(space.area.unit)  # Square feet (default)
print(space.area.value) # 100.0
```

### Field Types

- `required_field()`: Must be provided, creates SHACL constraints
- `optional_field()`: Optional for templates, used in queries
- `exclusive_field()`: Exactly one value (min=1, max=1)

```python
@semantic_object
class MySpace(Space):
    area: Area = required_field()           # Required
    volume: Volume = optional_field()       # Optional
    zone_type: ZoneType = exclusive_field() # Exactly one
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
2. **Interactive Tutorial**: Work through the [Basic Tutorial](../tutorial/basic-tutorial.ipynb)
3. **Advanced Usage**: Explore [Model Loading](../tutorial/model-loading-tutorial.ipynb)
4. **Custom Objects**: Learn to [create custom entities](guides/custom-entities.md)

## Common Patterns

### Loading Multiple Entity Types

```python
# Load multiple classes at once
results = loader.load_multiple_classes({
    'spaces': Space,
    'windows': Window,
}, ontology='s223')

spaces = results['spaces']
windows = results['windows']
```

### Working with Units

```python
from semantic_objects.qudt.units import M2, FT2

# Explicit unit specification
area_metric = Area(100.0, unit=M2)
area_imperial = Area(100.0, unit=FT2)

# Default units are used if not specified
area_default = Area(100.0)  # Uses FT2 by default
```

### Query Generation

```python
# Generate SPARQL query for any Resource class
query = Space.get_sparql_query(ontology='s223')
print(query)

# Execute query manually
from semantic_objects.model_loader import query_to_df
df = query_to_df(query, graph)
```

You're now ready to start using Semantic Objects! Check out the tutorials for more detailed examples.