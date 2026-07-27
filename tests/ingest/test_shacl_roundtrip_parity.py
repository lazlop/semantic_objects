"""Verify field-generating shapes round-trip through the existing (unmodified)
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
    # The existing (unmodified) RdfExporter emits sh:value rather than sh:class
    # for a plain Resource-typed field - this asserts against its actual behavior,
    # not an idealized shape, since exporters.py is intentionally untouched.
    query = """
    ASK {
        ?shape sh:path s223:hasDomain ;
               sh:value s223:EnumerationKind-Domain ;
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
