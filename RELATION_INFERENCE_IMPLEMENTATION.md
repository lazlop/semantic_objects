# Relation Inference Implementation

## Overview

This document describes the implementation of automatic relation inference for the semantic objects template builder. Instead of explicitly providing relations in field definitions, the system now infers default relations based on the class type and field type annotation.

## Implementation Details

### 1. Relation Metadata with `_applies_to`

Relations now define their applicability directly in the relation class using the `_applies_to` attribute. This attribute contains a list of `(source_class_name, target_class_name)` tuples that specify which class pairs the relation applies to.

**Example from `src/semantic_objects/s223/relations.py`:**
```python
class hasProperty(Predicate):
    _local_name = 'hasProperty'
    _applies_to = [
        ('Node', 'QuantifiableObervableProperty'),
    ]

class contains(Predicate):
    _local_name = 'contains'
    _applies_to = [
        ('PhysicalSpace', 'PhysicalSpace'),
    ]

class hasConnectionPoint(Predicate):
    _local_name = 'hasConnectionPoint'
    _applies_to = [
        ('Node', 'ConnectionPoint'),
        ('Equipment', 'FluidInlet'),
        ('Equipment', 'FluidOutlet'),
        ('Equipment', 'InletConnectionPoint'),
        ('Equipment', 'OutletConnectionPoint'),
    ]
```

**Example from `src/semantic_objects/watr/relations.py`:**
```python
class hasProcess(Predicate):
    _local_name = 'hasProcess'
    _applies_to = [
        ('UnitProcess', 'Process'),
    ]
```

### 2. Registry Builder Function

The `build_relations_registry()` function in `src/semantic_objects/core.py` automatically builds the `DEFAULT_RELATIONS` dictionary by scanning relation classes:

```python
def build_relations_registry(relations_module):
    """
    Build a DEFAULT_RELATIONS registry from relation classes with _applies_to metadata.
    
    Scans all Predicate subclasses in the provided module and builds a dictionary
    mapping (source_class, target_class) tuples to relation classes based on their
    _applies_to attribute.
    """
    registry = {}
    
    for name in dir(relations_module):
        obj = getattr(relations_module, name)
        
        if (isinstance(obj, type) and 
            issubclass(obj, Predicate) and 
            obj is not Predicate and
            hasattr(obj, '_applies_to')):
            
            for source_class, target_class in obj._applies_to:
                registry[(source_class, target_class)] = obj
    
    return registry
```

### 3. Automatic Registry Building

Each ontology module now builds its `DEFAULT_RELATIONS` automatically:

**In `src/semantic_objects/s223/core.py`:**
```python
from .. import core 
from . import relations

# Build DEFAULT_RELATIONS from relation class metadata
DEFAULT_RELATIONS = core.build_relations_registry(relations)
```

**In `src/semantic_objects/watr/core.py`:**
```python
from .. import core 
from ..s223 import relations as s223_relations
from . import relations

# Build DEFAULT_RELATIONS from relation class metadata
# This includes both watr-specific relations and s223 relations used by watr
DEFAULT_RELATIONS = {}
DEFAULT_RELATIONS.update(core.build_relations_registry(s223_relations))
DEFAULT_RELATIONS.update(core.build_relations_registry(relations))
```

### 2. Relation Inference Method

Added `_infer_relation_for_field()` method to the `Resource` class in `src/semantic_objects/core.py`:

- **Explicit relations take precedence**: If a relation is explicitly provided in the field metadata, it is used
- **Hierarchical lookup**: Walks up both the source class and target class hierarchies to find a matching relation
- **Per-ontology scope**: Finds the appropriate DEFAULT_RELATIONS registry by walking up the class MRO
- **Error handling**: Raises a clear error if no relation can be inferred and none is provided

### 3. Updated Methods

Modified the following methods to use relation inference:

- `get_relations()`: Now calls `_infer_relation_for_field()` for each field
- `generate_rdf_class_definition()`: Uses inference when generating SHACL constraints

### 4. Field Helper Functions

Updated `required_field()` to include `default=None` so that fields work properly with dataclasses inheritance.

## Usage

### Before (Explicit Relations)

```python
@dataclass
class Space(PhysicalSpace):
    area: Area = required_field(hasProperty)
```

### After (Inferred Relations)

```python
@dataclass
class Space(PhysicalSpace):
    area: Area = required_field()  # relation inferred as hasProperty
```

The relation is automatically inferred based on:
- Source class: `Space` (inherits from `PhysicalSpace` → `Node`)
- Target class: `Area` (inherits from `QuantifiableObervableProperty` → `Node`)
- Registry lookup finds: `('Node', 'QuantifiableObervableProperty')` → `hasProperty`

## Benefits

1. **Less Boilerplate**: No need to import and specify relations for common patterns
2. **Type Safety**: Relations are determined by the type system
3. **Maintainability**: Centralized relation mappings in DEFAULT_RELATIONS
4. **Flexibility**: Can still explicitly specify relations when needed
5. **Clear Errors**: Helpful error messages when relations cannot be inferred

## Adding New Relation Mappings

To add support for new class/relation combinations, add the `_applies_to` attribute to the relation class:

1. Identify the source and target class names
2. Add or update the `_applies_to` attribute in the relation class definition
3. Use the most general classes that make sense (e.g., use `Node` instead of specific subclasses when the relation applies broadly)
4. The registry will be automatically rebuilt when the module is imported

**Example - Adding a new relation:**
```python
class hasSensor(Predicate):
    _local_name = 'hasSensor'
    _applies_to = [
        ('Equipment', 'Sensor'),
    ]
```

**Example - Adding more applicability to an existing relation:**
```python
class hasConnectionPoint(Predicate):
    _local_name = 'hasConnectionPoint'
    _applies_to = [
        ('Node', 'ConnectionPoint'),
        ('Equipment', 'FluidInlet'),
        ('Equipment', 'FluidOutlet'),
        # Add new mapping:
        ('Equipment', 'Sensor'),
    ]
```

## Testing

Run the test suite to verify relation inference:

```bash
python3 test_relation_inference.py
```

The test suite verifies:
- Relation inference for simple fields
- Relation inference for multiple fields
- Relation inference across different ontologies (s223, watr)
- YAML template generation with inferred relations
- RDF class definition generation with inferred relations

## Notes

- The system uses hierarchical lookup, so you can define relations at parent class levels and they will apply to subclasses
- Explicit relations always take precedence over inferred relations
- The registry is per-ontology (s223 vs watr), allowing different ontologies to have different default relations
