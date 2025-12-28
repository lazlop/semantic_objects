# Inference Module

The inference module provides functionality to generate SHACL annotation rules from semantic object classes and run inference on RDF graphs to automatically add type annotations based on structural patterns.

## Overview

The inference module consists of two main components:

1. **AnnotationRuleGenerator**: Generates SHACL annotation rules from semantic object classes
2. **InferenceEngine**: Runs SHACL inference on RDF graphs using the generated rules

## Quick Start

### Generating Annotation Rules

```python
from semantic_objects.s223 import entities, properties
from semantic_objects.inference import generate_annotation_rules

# Generate rules from modules
rules = generate_annotation_rules([entities, properties])

# Save rules to file
rules.serialize('annotation_rules.ttl', format='turtle')
```

### Running Inference

```python
from rdflib import Graph
from semantic_objects.inference import infer_types
from semantic_objects.s223 import entities, properties

# Load your data
data = Graph()
data.parse('building_data.ttl', format='turtle')

# Run inference to add type annotations
inferred_data = infer_types(data, classes=[entities, properties])

# Save the enriched data
inferred_data.serialize('building_data_inferred.ttl', format='turtle')
```

## Detailed Usage

### AnnotationRuleGenerator Class

The `AnnotationRuleGenerator` class creates SHACL annotation rules that use TripleRule to infer RDF types based on the structure of instances in a data graph.

```python
from semantic_objects.inference import AnnotationRuleGenerator
from semantic_objects.s223.entities import Space, Window

# Create generator
generator = AnnotationRuleGenerator()

# Generate rules for specific classes
rules = generator.generate_annotation_rules([Space, Window])

# Access the shapes graph
print(f"Generated {len(rules)} triples")

# Save to file
generator.save_shapes('my_rules.ttl', format='turtle')
```

### InferenceEngine Class

The `InferenceEngine` class runs SHACL inference on RDF graphs using annotation rules.

```python
from rdflib import Graph
from semantic_objects.inference import InferenceEngine, generate_annotation_rules
from semantic_objects.s223 import entities, properties

# Generate or load annotation rules
rules = generate_annotation_rules([entities, properties])

# Create inference engine
engine = InferenceEngine(annotation_rules=rules)

# Load data
data = Graph()
data.parse('building_data.ttl', format='turtle')

# Run inference
inferred_data = engine.infer(data, use_tq_shacl=True)
```

### Convenience Functions

#### generate_annotation_rules()

Generate SHACL annotation rules from classes or modules.

```python
from semantic_objects.inference import generate_annotation_rules
from semantic_objects.s223 import entities, properties
from semantic_objects.s223.entities import Space

# From modules
rules = generate_annotation_rules([entities, properties])

# From specific classes
rules = generate_annotation_rules([Space])

# From a single class
rules = generate_annotation_rules(Space)
```

#### infer_types()

Run type inference on a data graph in one step.

```python
from rdflib import Graph
from semantic_objects.inference import infer_types
from semantic_objects.s223 import entities, properties

data = Graph()
data.parse('building_data.ttl', format='turtle')

# Infer types based on classes
inferred_data = infer_types(data, classes=[entities, properties])

# Or use pre-generated rules
from semantic_objects.inference import generate_annotation_rules
rules = generate_annotation_rules([entities, properties])
inferred_data = infer_types(data, annotation_rules=rules)
```

## How It Works

### Annotation Rules

The annotation rule generator creates SHACL shapes that define structural patterns for each semantic object class. For example, for a `Space` class with an `area` property:

1. An annotation shape is created: `hpfs:SpaceAnnotation`
2. A SHACL TripleRule is defined: `hpfs:SpaceAnnotationRule`
3. The rule targets instances of `s223:DomainSpace` (the base RDF type)
4. When an instance matches the Space pattern (has required properties), the rule adds: `?instance rdf:type hpfs:Space`

### Inference Process

The inference engine:

1. Takes a data graph with instances
2. Applies SHACL annotation rules
3. Adds type triples for instances that match class patterns
4. Returns the enriched graph

## SHACL Engines

The module supports two SHACL engines:

### TopQuadrant SHACL (Recommended)

Provides full support for SHACL rules including TripleRule.

```python
# Install
pip install brick-tq-shacl

# Use (default)
inferred_data = infer_types(data, classes=[entities], use_tq_shacl=True)
```

### PySHACL (Limited Support)

Fallback option with limited SHACL rule support.

```python
# Install
pip install pyshacl

# Use
inferred_data = infer_types(data, classes=[entities], use_tq_shacl=False)
```

## Examples

### Example 1: Basic Inference

```python
from rdflib import Graph, Literal, URIRef
from semantic_objects.s223 import entities, properties
from semantic_objects.inference import generate_annotation_rules, infer_types
from semantic_objects.namespaces import S223, QUDT, UNIT, bind_prefixes

# Create sample data
data = Graph()
bind_prefixes(data)

space = URIRef("http://example.org/Space1")
area = URIRef("http://example.org/Area1")

# Add triples matching Space pattern
data.add((space, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), S223.DomainSpace))
data.add((space, S223.hasProperty, area))
data.add((area, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), S223.QuantifiableObservableProperty))
data.add((area, QUDT.hasQuantityKind, URIRef("http://qudt.org/vocab/quantitykind/Area")))
data.add((area, S223.hasValue, Literal(100.0)))

# Run inference
inferred = infer_types(data, classes=[entities, properties])

# Check for inferred types
print(f"Original triples: {len(data)}")
print(f"After inference: {len(inferred)}")
```

### Example 2: Saving and Reusing Rules

```python
from semantic_objects.s223 import entities, properties
from semantic_objects.inference import generate_annotation_rules, infer_types
from rdflib import Graph

# Generate rules once
rules = generate_annotation_rules([entities, properties])
rules.serialize('annotation_rules.ttl', format='turtle')

# Later, load and reuse rules
loaded_rules = Graph()
loaded_rules.parse('annotation_rules.ttl', format='turtle')

# Use with multiple data graphs
for data_file in ['building1.ttl', 'building2.ttl']:
    data = Graph()
    data.parse(data_file, format='turtle')
    inferred = infer_types(data, annotation_rules=loaded_rules)
    inferred.serialize(f'inferred_{data_file}', format='turtle')
```

### Example 3: Inspecting Generated Rules

```python
from semantic_objects.s223.entities import Space
from semantic_objects.inference import AnnotationRuleGenerator
from semantic_objects.namespaces import HPFS, RDF, SH

generator = AnnotationRuleGenerator()
rules = generator.generate_annotation_rules(Space)

# Query the rules graph
annotation_shape = HPFS["SpaceAnnotation"]
rule_iri = HPFS["SpaceAnnotationRule"]

print("Annotation Shape:")
for s, p, o in rules.triples((annotation_shape, None, None)):
    print(f"  {p} -> {o}")

print("\nAnnotation Rule:")
for s, p, o in rules.triples((rule_iri, None, None)):
    print(f"  {p} -> {o}")
```

## API Reference

### AnnotationRuleGenerator

- `__init__()`: Initialize the generator
- `generate_annotation_rules(classes)`: Generate rules for given classes/modules
- `save_shapes(filename, format='turtle')`: Save rules to file

### InferenceEngine

- `__init__(annotation_rules=None)`: Initialize with optional rules
- `infer(data_graph, annotation_rules=None, use_tq_shacl=True)`: Run inference

### Convenience Functions

- `generate_annotation_rules(classes)`: Generate rules from classes/modules
- `infer_types(data_graph, classes=None, annotation_rules=None, use_tq_shacl=True)`: Run inference in one step

## Notes

- Only `Node` subclasses (entities) generate annotation rules
- Abstract classes are automatically skipped
- Classes without a `_ns` attribute are skipped
- The module gracefully handles classes that can't generate IRIs
- Generated rules use the `hpfs:` namespace (urn:hpflex/shapes#)

## Related Documentation

- [Core Concepts](core-concepts.md)
- [Quick Start](quick-start.md)
- [Installation](installation.md)
