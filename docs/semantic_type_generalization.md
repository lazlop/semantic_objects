# Semantic Type Generalization

## Overview

This document describes the generalization of the `QuantifiableObservableProperty` interpretation mechanism to work with any class hierarchy using the `_semantic_type` attribute.

## Problem

Previously, the code had hardcoded checks for `QuantifiableObservableProperty` in two places:

1. **`query.py`**: When generating SPARQL queries, it checked if a class had `QuantifiableObservableProperty` in its MRO and handled the `qk` field specially
2. **`model_loader.py`**: When loading instances from RDF, it checked for `QuantifiableObservableProperty` and handled `value` and `unit` fields specially

This hardcoding made the system inflexible and tied to a specific class hierarchy.

## Solution

We introduced a `_semantic_type` class attribute that allows any class to specify which parent type should be used in the semantic model (RDF representation).

### Key Concepts

1. **`_semantic_type` attribute**: Classes can set this to specify their semantic type in the RDF model
2. **Class-level fields**: Fields with `init=False` and a default value are treated as class-level constraints
3. **Instance-level fields**: Fields with `init=True` are treated as instance-level data

### Example

```python
@semantic_object
class QuantifiableObservableProperty(Property):
    qk: quantitykinds.QuantityKind = required_field(qualified=False)
    value: float = required_field()
    unit: Optional[Unit] = field(default=None, ...)

@semantic_object
class Area(QuantifiableObservableProperty):
    qk = quantitykinds.Area  # Class-level field (init=False)
    _semantic_type = QuantifiableObservableProperty  # Use parent type in RDF
```

In this example:
- `Area` instances will be typed as `QuantifiableObservableProperty` in RDF
- The `qk` field is set at the class level and becomes a constraint in SPARQL queries
- The `value` and `unit` fields are instance-level and passed to `__init__`

## Implementation Details

### In `query.py` (SparqlQueryBuilder)

When generating SPARQL queries:

1. Check if a field type has `_semantic_type` attribute
2. If yes, use `_semantic_type` for the RDF type triple
3. For each class-level field (init=False with default):
   - Infer the relation for that field
   - Add a triple constraining that field to its class-level value

```python
if hasattr(field_type, '_semantic_type') and field_type._semantic_type is not None:
    semantic_type = field_type._semantic_type
    self.graph.add((PARAM[field_name], RDF.type, semantic_type._get_iri()))
    
    # Add triples for class-level fields
    for class_field_name, class_field_obj in field_type.__dataclass_fields__.items():
        if not class_field_obj.init and not isinstance(class_field_obj.default, _MISSING_TYPE):
            # Add constraint triple
```

### In `model_loader.py` (ModelLoader)

When loading instances from RDF:

1. Check if a field type has `_semantic_type` attribute
2. If yes, only pass instance-level fields (init=True) to `__init__`
3. Class-level fields are already set on the class and don't need to be passed

```python
if has_semantic_type:
    # Only pass instance-level fields
    for inst_field_name, inst_field_obj in field_type.__dataclass_fields__.items():
        if inst_field_obj.init:
            # Add to kwargs
```

## Benefits

1. **Generalization**: Works with any class hierarchy, not just `QuantifiableObservableProperty`
2. **Flexibility**: Classes can specify their semantic type explicitly
3. **Maintainability**: No hardcoded class name checks
4. **Extensibility**: Easy to add new class hierarchies with similar patterns

## Usage

To use this pattern with your own classes:

1. Define a parent class with some fields that will be set at the class level
2. Create subclasses that set those fields as class attributes (using `field(init=False, default=...)`)
3. Add `_semantic_type = ParentClass` to the subclasses
4. The system will automatically:
   - Use the parent type in RDF/SPARQL
   - Add constraints for class-level fields in queries
   - Only pass instance-level fields when loading from RDF

## Example: Creating a New Hierarchy

```python
@semantic_object
class MeasurementType(Property):
    measurement_kind: MeasurementKind = required_field(qualified=False)
    value: float = required_field()
    
@semantic_object
class Temperature(MeasurementType):
    measurement_kind = MeasurementKinds.Temperature
    _semantic_type = MeasurementType

@semantic_object
class Pressure(MeasurementType):
    measurement_kind = MeasurementKinds.Pressure
    _semantic_type = MeasurementType
```

Now `Temperature` and `Pressure` instances will be typed as `MeasurementType` in RDF, with `measurement_kind` constraints in SPARQL queries.

## Testing

See `tests/test_semantic_type.py` for comprehensive tests of this functionality.
