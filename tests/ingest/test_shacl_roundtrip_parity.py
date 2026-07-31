"""Verify field-generating shapes round-trip through
RdfExporter.generate_rdf_class_definition() with fidelity matching the vendored
ontology. Full round-trip of non-field constraints (sh:sparql, sh:or) is out of
scope - see _generated/_raw_shapes.py for those.
"""
from rdflib import Graph

from semantic_objects.namespaces import bind_prefixes
from semantic_objects.s223._generated import entities, properties


def _shacl_graph(cls) -> Graph:
    g = Graph()
    bind_prefixes(g)
    g.parse(data=cls.generate_rdf_class_definition(), format='turtle')
    return g


def test_domain_space_roundtrip():
    g = _shacl_graph(entities.DomainSpace)
    # DomainSpace.domain is a plain (unpinned) Resource-typed field - it should
    # constrain to the *type* (sh:class), not one specific fixed individual
    # (sh:value, reserved for fields actually pinned to a fixed value/instance).
    query = """
    ASK {
        ?shape sh:path s223:hasDomain ;
               sh:class s223:EnumerationKind-Domain ;
               sh:minCount 1 .
    }
    """
    assert bool(g.query(query))


def test_physical_space_roundtrip():
    g = _shacl_graph(entities.PhysicalSpace)
    assert bool(g.query("ASK { ?s sh:path s223:contains ; sh:class s223:PhysicalSpace . }"))
    assert bool(g.query("ASK { ?s sh:path s223:encloses ; sh:class s223:DomainSpace . }"))


def test_pump_qualified_fields_roundtrip():
    g = _shacl_graph(entities.Pump)
    # Both qualified connection-point fields should surface as sh:class targets
    # reachable from a hasConnectionPoint property shape (directly or via a
    # qualifiedValueShape, matching how the exporter already renders qualified=True).
    result = g.query("""
        SELECT ?target WHERE {
            ?shape sh:path s223:hasConnectionPoint .
            { ?shape sh:class ?target } UNION { ?shape sh:qualifiedValueShape/sh:class ?target }
        }
    """)
    targets = {str(row.target) for row in result}
    assert any('OutletConnectionPoint' in t for t in targets)
    assert any('InletConnectionPoint' in t for t in targets)


def test_qualifiable_observable_property_subclassof_roundtrip():
    g = _shacl_graph(properties.QuantifiableObservableProperty)
    assert bool(g.query("""
        ASK { s223:QuantifiableObservableProperty rdfs:subClassOf ?p .
              FILTER(?p = s223:ObservableProperty || ?p = s223:QuantifiableProperty) }
    """))


def test_hand_written_qualifiable_observable_property_roundtrip():
    # s223.properties.QuantifiableObservableProperty (hand-written, adds
    # qk/value/unit) used to crash generate_rdf_class_definition() outright:
    # `value: float`'s bare builtin type has no `_get_iri()`, which the exporter
    # called unconditionally. Plain-datatype fields should emit sh:datatype.
    from semantic_objects.s223 import properties as hand_properties
    g = Graph()
    bind_prefixes(g)
    g.parse(data=hand_properties.QuantifiableObservableProperty.generate_rdf_class_definition(),
            format='turtle')
    assert bool(g.query("""
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        ASK { ?shape sh:path s223:hasValue ; sh:datatype xsd:decimal . }
    """))


def test_pinned_field_emits_the_actual_value_not_its_type():
    # Area.qk is pinned to `quantitykinds.Area` - the exporter used to read
    # `field_obj.type._get_iri()` (the *type annotation*, QuantityKind) instead of
    # the actually-pinned value, silently emitting the wrong sh:value.
    from semantic_objects.s223 import properties as hand_properties
    g = Graph()
    bind_prefixes(g)
    g.parse(data=hand_properties.Area.generate_rdf_class_definition(), format='turtle')
    assert bool(g.query("""
        PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
        ASK { ?shape sh:path s223:hasQuantityKind ; sh:value quantitykind:Area . }
    """))
    assert not bool(g.query("""
        PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
        ASK { ?shape sh:path s223:hasQuantityKind ; sh:value quantitykind:QuantityKind . }
    """))


def test_exact_values_field_roundtrip():
    # ThresholdAlarm-style `exact_values` fields (e.g. Area_SP.aspects) used to
    # crash outright (Optional[list] has no _get_iri()). Each value should surface
    # as its own sh:hasValue property shape sharing the field's relation path.
    from semantic_objects.s223 import properties as hand_properties
    g = Graph()
    bind_prefixes(g)
    g.parse(data=hand_properties.Area_SP.generate_rdf_class_definition(), format='turtle')
    for value in ('Aspect-Setpoint', 'Aspect-Threshold', 'Domain-Occupancy'):
        assert bool(g.query(f"""
            ASK {{ ?shape sh:path s223:hasAspect ; sh:hasValue s223:{value} . }}
        """)), f"missing sh:hasValue for {value}"
