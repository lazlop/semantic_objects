# Semantic Objects Documentation

Welcome to the **Semantic Objects** library documentation! This library provides a simplified Pythonic interface to several ontologies for the modeling of cyberphysical systems in the built environment (specifically those based on Brick, ASHRAE 223P, and WATR).

The goal of this package is to simplify:
- Creating SHACL/Ontology statements for validation of existing semantic models or use in other tools
- Creation of templates to enable use of BuildingMOTIF or other resources for creating building models
- Loading of semantic models into python objects to simplify querying and metadata usage


## 📚 Documentation Structure

### Getting Started
- [Quick Start Guide](quick-start.md) - Get up and running in 5 minutes
- [Installation Guide](installation.md) - Installation and setup instructions
- [Core Concepts](core-concepts.md) - Understanding the library architecture

### Tutorials
- [Basic Tutorial](../tutorial/basic-tutorial.ipynb) - Interactive Jupyter notebook tutorial
- [Model Loading Tutorial](../tutorial/model-loading-tutorial.ipynb) - Loading RDF data into Python objects
- [Template Generation Tutorial](../tutorial/template-generation-tutorial.ipynb) - Creating BuildingMOTIF templates
- [Advanced Examples](../tutorial/advanced-examples.ipynb) - Complex use cases and patterns

### API Reference
- [Core Classes](api/core.md) - Resource, Node, Predicate classes
- [Model Loader](api/model-loader.md) - Loading semantic data from RDF graphs
- [S223 Entities](api/s223-entities.md) - ASHRAE 223P implementation
- [QUDT Support](api/qudt.md) - Quantity kinds and units

### How-To Guides
- [Creating Custom Entities](guides/custom-entities.md) - Define your own semantic objects
- [Working with Properties](guides/properties.md) - Handling quantifiable properties
- [Validation and SHACL](guides/validation.md) - Generating validation rules
- [BuildingMOTIF Integration](guides/buildingmotif.md) - Template generation and evaluation

### Migration
- [Migration Guide](MIGRATION_SUMMARY.md) - Migrating from old LoadModel class

## 🎯 Key Features

### 1. **Pythonic Ontology Interface**
Define semantic objects as simple Python dataclasses:

```python
@semantic_object
class Space(DomainSpace):
    area: Area = required_field()
```

### 2. **Automatic Query Generation**
Generate SPARQL queries automatically from class definitions:

```python
query = Space.get_sparql_query(ontology='s223')
```

### 3. **Type-Safe Model Loading**
Load RDF data into typed Python objects:

```python
loader = ModelLoader(source="building.ttl")
spaces = loader.load_instances(Space, ontology='s223')
```

### 4. **Template Generation**
Create BuildingMOTIF templates automatically:

```python
export_templates(Space, 'templates/')
```

### 5. **SHACL Validation**
Generate SHACL shapes for validation:

```python
shacl_shape = Space.generate_rdf_class_definition()
```

## 🚀 Quick Example

```python
from semantic_objects.s223 import Space, Area
from semantic_objects.model_loader import ModelLoader

# Define a space with area
space = Space(area=Area(100.0))

# Load spaces from RDF graph
loader = ModelLoader(source="building.ttl")
spaces = loader.load_instances(Space, ontology='s223')

# Generate templates
from semantic_objects.core import export_templates
export_templates(Space, 'templates/')
```

## 🏗️ Architecture Overview

The library is built around three core concepts:

1. **Resource Classes**: Python dataclasses that represent ontology concepts
2. **Model Loader**: Query RDF graphs and instantiate Python objects
3. **Template Generation**: Create BuildingMOTIF templates for model building

## 🔗 Related Projects

- [BuildingMOTIF](https://github.com/NREL/BuildingMOTIF) - Building model generation framework
- [ASHRAE Standard 223P](https://www.ashrae.org/technical-resources/standards-and-guidelines/standards-addenda/standard-223p) - Semantic tagging standard
- [Brick Schema](https://brickschema.org/) - Building metadata schema

## 📖 Next Steps

1. Start with the [Quick Start Guide](quick-start.md)
2. Work through the [Basic Tutorial](../tutorial/basic-tutorial.ipynb)
3. Explore the [API Reference](api/) for detailed documentation
4. Check out [Advanced Examples](../tutorial/advanced-examples.ipynb) for complex use cases
