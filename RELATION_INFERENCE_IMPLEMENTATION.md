# Relation Inference Implementation

## Overview

This document describes the implementation of automatic relation inference for the semantic objects template builder. Instead of explicitly providing relations in field definitions, the system now infers default relations based on the class type and field type annotation.

## Implementation Details

### 1. DEFAULT_RELATIONS Registry

Each ontology module (s223, watr) now has a `DEFAULT_RELATIONS` dictionary that maps `(source_class_name, target_class_name)` tuples to relation objects.

**Example from `src/semantic_objects/s223/core.py`:**
```python
DEFAULT_RELATIONS = {
    # Node -> QuantifiableObervableProperty uses hasProperty
    ('Node', 'QuantifiableObervableProperty'): relations.hasProperty,
    # PhysicalSpace -> PhysicalSpace uses contains
    ('PhysicalSpace', 'PhysicalSpace'): relations.contains,
    # PhysicalSpace -> DomainSpace uses encloses
    ('PhysicalSpace', 'DomainSpace'): relations.encloses,
    # Node -> ConnectionPoint types use hasConnectionPoint
    ('Node', 'InletConnectionPoint'): relations.hasConnectionPoint,
    ('Node', 'OutletConnectionPoint'): relations.hasConnectionPoint,
    ('Node', 'ConnectionPoint'): relations.hasConnectionPoint,
}
```

**Example from `src/semantic_objects/watr/core.py`:**
```python
DEFAULT_RELATIONS = {
    # Equipment -> ConnectionPoint types use hasConnectionPoint
    ('Equipment', 'FluidInlet'): s223_relations.hasConnectionPoint,
    ('Equipment', 'FluidOutlet'): s223_relations.hasConnectionPoint,
    # ConnectionPoint -> Fluid uses hasMedium
    ('InletConnectionPoint', 'Fluid'): s223_relations.hasMedium,
    ('OutletConnectionPoint', 'Fluid'): s223_relations.hasMedium,
    # UnitProcess -> Process uses hasProcess
    ('UnitProcess', 'Process'): hasProcess,
}
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

To add support for new class/relation combinations:

1. Identify the source and target class names
2. Add an entry to the appropriate DEFAULT_RELATIONS dictionary
3. Use the most general classes that make sense (e.g., use `Node` instead of specific subclasses when the relation applies broadly)

Example:
```python
DEFAULT_RELATIONS = {
    # ... existing mappings ...
    ('Equipment', 'Sensor'): relations.hasSensor,
}
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
