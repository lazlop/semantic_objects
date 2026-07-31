"""Prove `shacl_bridge.py` (hand-rolled, no BuildingMOTIF) against three
representative classes, per the success criteria in
`.claude/plans/i-d-like-to-push-shimmying-lecun.md`:

  - s223.entities.Pump: severity-Warning qualified shapes (sh:node wrapping a
    nested sh:or) must surface but stay OPTIONAL - a warning-severity shape
    means "should have", not "must have".
  - s223.entities.WaterToAirHeatPump: four separate qualifiedValueShapes all
    on hasConnectionPoint (in-scope, no-severity-override, so genuinely
    mandatory) - the hard multi-shape-per-path disambiguation case that
    started this investigation (originally prototyped against g36:Fan, which
    isn't available in this checkout - this is a real equivalent already
    present in the vendored s223 ontology).
  - s223.properties.QuantifiableObservableProperty: reproduces, then fixes,
    the confirmed exporters.py crash (`field_obj.type._get_iri()` called on a
    bare `float` - AttributeError).
"""
import pytest
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

from semantic_objects.namespaces import bind_prefixes
from semantic_objects.s223 import entities, properties
from semantic_objects import shacl_bridge as sb


def _shacl_graph(cls, **kwargs) -> Graph:
    g = Graph()
    bind_prefixes(g)
    g.parse(data=sb.shacl_definition_for(cls, **kwargs), format="turtle")
    return g


# -- Pump: qualified fields + severity-Warning nested sh:or -------------------

def test_pump_query_parses_and_binds_both_connection_points():
    query = sb.sparql_query_for(entities.Pump)
    prepareQuery(query)  # raises on invalid SPARQL
    assert "OutletConnectionPoint" in query
    assert "InletConnectionPoint" in query


def test_pump_warning_severity_shapes_stay_optional():
    """qualifiedMinCount 1 + sh:severity sh:Warning means "should have", not
    "must have" - the query must not filter out Pumps lacking it. (This is
    the correctly-scoped version of the confirmed BuildingMOTIF ShapeCollection
    bug of *always* wrapping qualified shapes in OPTIONAL regardless of what
    the ontology says - here it's OPTIONAL because of severity, not by default.)"""
    query = sb.sparql_query_for(entities.Pump)
    assert "OPTIONAL { ?name s223:hasConnectionPoint ?hasConnectionPoint_OutletConnectionPoint" in query
    assert "OPTIONAL { ?name s223:hasConnectionPoint ?hasConnectionPoint_InletConnectionPoint" in query


def test_pump_shacl_definition_qualified_fields_roundtrip():
    """Same assertion tests/ingest/test_shacl_roundtrip_parity.py makes against
    the existing exporters.py output, now sourced from the live graph."""
    g = _shacl_graph(entities.Pump)
    result = g.query("""
        SELECT ?target WHERE {
            ?shape sh:path s223:hasConnectionPoint .
            ?shape sh:qualifiedValueShape/sh:class ?target .
        }
    """)
    targets = {str(row.target) for row in result}
    assert any("OutletConnectionPoint" in t for t in targets)
    assert any("InletConnectionPoint" in t for t in targets)


def test_pump_shacl_definition_preserves_nested_sparql_constraint():
    """The sh:sparql constraint on Pump's shared hasConnectionPoint path is not
    representable as a field/triple pattern - shacl_definition_for must still
    preserve it verbatim (it's just serializing the live graph, not
    re-deriving), unlike the dataclass-field pipeline which drops it into an
    inert RAW_SHAPES sidecar."""
    definition = sb.shacl_definition_for(entities.Pump)
    assert "sh:sparql" in definition
    assert "SPARQLConstraint" in definition


# -- WaterToAirHeatPump: 4 qualified shapes sharing one path ------------------

def test_water_to_air_heat_pump_disambiguates_four_qualified_shapes():
    query = sb.sparql_query_for(entities.WaterToAirHeatPump)
    prepareQuery(query)
    for var in [
        "?hasConnectionPoint_OutletConnectionPoint ",
        "?hasConnectionPoint_InletConnectionPoint ",
        "?hasConnectionPoint_OutletConnectionPoint_2 ",
        "?hasConnectionPoint_InletConnectionPoint_2 ",
    ]:
        assert var in query


def test_water_to_air_heat_pump_qualified_shapes_are_mandatory_not_optional():
    """Unlike Pump, these four shapes have no sh:severity override, so their
    qualifiedMinCount >= 1 must translate to a plain (non-OPTIONAL) triple
    pattern - the confirmed BuildingMOTIF ShapeCollection bug wraps this in
    OPTIONAL unconditionally, which shacl_bridge deliberately does not."""
    query = sb.sparql_query_for(entities.WaterToAirHeatPump)
    assert "OPTIONAL { ?name s223:hasConnectionPoint ?hasConnectionPoint_OutletConnectionPoint " not in query
    assert "OPTIONAL { ?name s223:hasConnectionPoint ?hasConnectionPoint_InletConnectionPoint " not in query


def test_water_to_air_heat_pump_shacl_definition_include_hierarchy():
    g = _shacl_graph(entities.WaterToAirHeatPump, include_hierarchy=True)
    # Own constraint: qualified hasConnectionPoint shapes targeting both
    # connection point kinds.
    own = bool(g.query("""
        ASK { ?shape sh:path s223:hasConnectionPoint ;
                     sh:qualifiedValueShape [ sh:class s223:OutletConnectionPoint ] . }
    """))
    # Inherited (from an ancestor, e.g. Equipment/Connectable): some
    # constraint not declared directly on WaterToAirHeatPump.
    inherited = bool(g.query("ASK { ?shape sh:path s223:hasProperty . }"))
    assert own
    assert inherited


# -- QuantifiableObservableProperty: regression for the confirmed crash ------

def test_quantifiable_observable_property_crashes_via_existing_exporter():
    """Documents the bug this investigation started from: a dataclass field
    whose type unwraps to a bare Python primitive (`value: float`) makes
    exporters.py call `._get_iri()` on `float` itself. Left unmodified, since
    exporters.py is out of scope for this prototype."""
    with pytest.raises(AttributeError):
        properties.QuantifiableObservableProperty.generate_rdf_class_definition()


def test_quantifiable_observable_property_works_via_shacl_bridge():
    """shacl_bridge never touches a dataclass field, so it can't hit the crash
    above - it just serializes/queries the live graph."""
    definition = sb.shacl_definition_for(properties.QuantifiableObservableProperty, include_hierarchy=True)
    assert "QuantifiableObservableProperty" in definition

    query = sb.sparql_query_for(properties.QuantifiableObservableProperty)
    prepareQuery(query)
    assert "qudt:hasQuantityKind" in query
