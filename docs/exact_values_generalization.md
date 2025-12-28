# Exact Values Generalization

## Overview

This document describes the generalization of the aspect handling mechanism in the semantic_objects library. Previously, aspects were handled with hardcoded logic specific to the s223 ontology. This has been replaced with a generalized approach using field metadata that can be applied to any field requiring exact value matching.

## Problem Statement

The original implementation had hardcoded logic in `query.py` that specifically checked for an `aspects` class attribute and generated special SPARQL queries for s223 properties. This approach was:

1. **Not generalizable**: Only worked for aspects in s223 ontology
2. **Hardcoded**: Required modifying query generation code for each new use case
3. **Inflexible**: Couldn't be applied to other fields or ontologies

## Solution

The solution generalizes this pattern using field metadata, making it applicable to any field that requires exact value matching.

### Key Changes

#### 1. Added `exact_values` Parameter to Field Metadata

**File**: `src/semantic_objects/fields.py`

Added a new `exact_values` parameter to the `required_field()` function:

```python
def required_field(relation=None, min=1, max=None, qualified=True, 
                   label=None, comment=None, value=None, exact_values=None):
    """
    The 'exact_values' parameter specifies that the semantic model must have 
    exactly these values (not at least).
    """
    return field(
        metadata={
            'relation': relation,
            'min': min,
            'max': max,
            'qualified': qualified,
            'label': label,
            'comment': comment,
            'value': value,
            'exact_values': exact_values  # New parameter
        }
    )
```

#### 2. Generalized Query Generation

**File**: `src/semantic_objects/query.py`

Removed hardcoded s223 aspect logic and replaced it with a generalized approach:

- **Removed**: Hardcoded checks for s223 ontology and aspect handling
- **Added**: Generic `exact_values` metadata processing
- **Added**: `_add_exact_values_filter()` method to generate SPARQL filters
- **Added**: `_add_exact_values_to_query()` method to inject filters into queries

The query builder now:
1. Detects fields with `exact_values` metadata
2. Generates appropriate SPARQL FILTER clauses
3. Uses `IN` operator for exact matching
4. Handles empty exact_values lists (FILTER NOT EXISTS)

#### 3. Updated s223 Properties

**File**: `src/semantic_objects/s223/properties.py`

Changed from hardcoded class attribute to field metadata:

**Before**:
```python
@semantic_object
class Area_SP(Area):
    aspects = [Setpoint, Deadband, Occupancy]
```

**After**:
```python
@semantic_object
class Area_SP(Area):
    aspects: Optional[list] = field(
        default=None,
        init=False,
        metadata={
            'relation': hasAspect,
            'exact_values': [Setpoint, Deadband, Occupancy],
            'qualified': False
        }
    )
```

## Generated SPARQL Query Example

For `Area_SP`, the system now generates:

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
PREFIX s223: <http://data.ashrae.org/standard223#>

SELECT DISTINCT * WHERE {
    ?name rdf:type s223:Area_SP .
    ?name s223:hasValue ?value .
    ?name s223:hasQuantityKind quantitykind:Area .
    ?name <http://data.ashrae.org/standard223#hasAspect> ?name_exact_values .
    FILTER(?name_exact_values IN (s223:Aspect-Setpoint,s223:Aspect-Threshold,s223:Domain-Occupancy) )
}
```

The FILTER clause ensures that only instances with exactly the specified aspects are matched.

## Benefits

1. **Generalized**: Works for any field, not just aspects
2. **Declarative**: Exact values are specified in field metadata
3. **Maintainable**: No need to modify query generation code for new use cases
4. **Extensible**: Can be applied to other ontologies and use cases
5. **Type-safe**: Uses Python dataclass field metadata system

## Usage

To use exact value matching for any field:

```python
from semantic_objects.core import semantic_object
from semantic_objects.fields import field

@semantic_object
class MyClass(SomeBase):
    my_field: Optional[list] = field(
        default=None,
        init=False,
        metadata={
            'relation': some_relation,
            'exact_values': [Value1, Value2, Value3],
            'qualified': False
        }
    )
```

This will generate SPARQL queries that match only instances with exactly `Value1`, `Value2`, and `Value3` for `my_field`.

## Testing

A comprehensive test suite has been added in `tests/test_exact_values.py` that verifies:

1. Field metadata is correctly set
2. Relations are properly configured
3. SPARQL queries are generated with correct FILTER clauses
4. All exact values are referenced in the query

## Migration Notes

For existing code using the old `aspects = [...]` pattern:

1. Convert to a field with `init=False` and `default=None`
2. Add type annotation (e.g., `Optional[list]`)
3. Move the list to `exact_values` in metadata
4. Specify the `relation` in metadata

The old pattern will no longer work as the hardcoded s223 logic has been removed.
