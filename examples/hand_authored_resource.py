#!/usr/bin/env python3
"""
Hand-Authoring Resource Classes (No Ontology Ingestion Required)

`semantic_objects.ingest` exists to mirror an *external* ontology (S223, WATR,
CXF) class-for-class, with round-trip parity tests keeping it faithful to the
vendored SHACL. That's the right tool when standards fidelity is the point.

It is not the only way to get a Resource class, and it's overkill when your
classes are meant to match your own data/query shape rather than a published
standard. This example defines a small vocabulary from scratch - a couple of
point types and a thermostat family - directly on `core.Resource`/`Node`, with
no ontology behind it at all, and shows that inheritance, BuildingMOTIF
template generation, and SHACL generation all still work exactly the same way
they do for ingested classes:

- `StagedThermostat(Thermostat)` adds one field via ordinary Python
  subclassing - no template DSL, no separate "extends" resolution step.
- `.to_yaml()` / `.generate_turtle_body()` produce ready-to-load BuildingMOTIF
  templates, because that machinery lives on `Resource`, not on anything
  ontology-specific.
- `.generate_rdf_class_definition()` produces SHACL constraints from the same
  field definitions - inheritance and constraint generation aren't two
  separate systems to keep in sync.

See docs/ or the project's architecture discussion for why this is preferred
over building a YAML template inheritance/conditionals DSL: the class system
already *is* that DSL, with type-checking and no compile step.
"""
from rdflib import Namespace

from semantic_objects.core import Node, Predicate, semantic_object
from semantic_objects.fields import required_field

# A namespace for a vocabulary that isn't ingested from anywhere - it exists
# only because this project needs it.
POINTS = Namespace("urn:example-points#")


@semantic_object
class PointNode(Node):
    """Shared base for this example's vocabulary - just sets the namespace."""
    _ns = POINTS
    abstract = True


@semantic_object
class hasPoint(Predicate):
    _ns = POINTS


# --- A small value family -------------------------------------------------
# Three point types that only differ in what they assert about themselves.
# Compare to hand-writing three near-identical BuildingMOTIF YAML blocks that
# only differ by one triple - here it's one field override each.

@semantic_object
class Deadband(PointNode):
    pass


@semantic_object
class Tolerance(PointNode):
    pass


@semantic_object
class Active(PointNode):
    pass


@semantic_object
class StageCount(PointNode):
    pass


# --- An entity family with a specialization --------------------------------

@semantic_object
class Thermostat(PointNode):
    """A thermostat with the points every thermostat has."""
    deadband: Deadband = required_field(relation=hasPoint)
    tolerance: Tolerance = required_field(relation=hasPoint)
    active: Active = required_field(relation=hasPoint)


@semantic_object
class StagedThermostat(Thermostat):
    """A thermostat that also reports how many heating/cooling stages are
    active. Inherits deadband/tolerance/active from Thermostat for free -
    this is the entire "extension" of the base template."""
    stage_count: StageCount = required_field(relation=hasPoint)


def main():
    print("=" * 60)
    print("Hand-authored Resource classes - no ontology ingestion involved")
    print("=" * 60)

    print("\n--- Thermostat: generated BuildingMOTIF template ---")
    print(Thermostat.to_yaml())

    print("--- StagedThermostat: same template, extended by subclassing ---")
    print(StagedThermostat.to_yaml())

    print("--- StagedThermostat: SHACL constraints, generated from the same fields ---")
    print(StagedThermostat.generate_rdf_class_definition(include_hierarchy=True))

    print("--- Instantiating and inspecting a StagedThermostat ---")
    tstat = StagedThermostat(
        deadband=Deadband(),
        tolerance=Tolerance(),
        active=Active(),
        stage_count=StageCount(),
    )
    print(f"Created: {tstat._name}")
    print(f"Fields: {list(tstat.__class__.__dataclass_fields__.keys())}")


if __name__ == "__main__":
    main()
