from pathlib import Path

import pytest

from semantic_objects.ingest.adapters.s223 import S223Adapter
from semantic_objects.ingest.config import IngestConfig
from semantic_objects.ingest.parser import OntologyParser

ONTOLOGY_PATH = (
    Path(__file__).resolve().parents[2]
    / "src" / "semantic_objects" / "ontologies" / "s223" / "223p.ttl"
)


@pytest.fixture(scope="module")
def ontology_ir():
    config = IngestConfig(
        ontology_name="s223",
        source_path=ONTOLOGY_PATH,
        output_dir=Path("unused"),
    )
    return OntologyParser(config, S223Adapter()).parse()


def test_meta_classes_excluded(ontology_ir):
    for meta in ("Class", "Concept", "AbstractClass", "Relation", "RelationWithInverse", "SymmetricRelation"):
        assert meta not in ontology_ir.classes


def test_class_and_relation_counts_are_substantial(ontology_ir):
    assert len(ontology_ir.classes) > 300
    assert len(ontology_ir.relations) >= 55


def test_abstract_classes_flagged(ontology_ir):
    for name in ("Connectable", "ConnectionPoint", "ExternalReference"):
        assert ontology_ir.classes[name].is_abstract


def test_pump_qualified_connection_points_generate_fields(ontology_ir):
    pump = ontology_ir.classes["Pump"]
    field_names = {s.field_name for s in pump.property_shapes}
    assert "outlet_connection_point" in field_names
    assert "inlet_connection_point" in field_names

    outlet = next(s for s in pump.property_shapes if s.field_name == "outlet_connection_point")
    assert outlet.qualified is True
    assert outlet.target_class_local == "OutletConnectionPoint"
    assert outlet.min_count == 1
    # The nested medium sh:or refinement is preserved, not dropped, and doesn't
    # block field generation.
    assert len(outlet.supplementary_notes) >= 1

    inlet = next(s for s in pump.property_shapes if s.field_name == "inlet_connection_point")
    assert inlet.target_class_local == "InletConnectionPoint"


def test_pump_sparql_constraint_is_complex_not_a_field(ontology_ir):
    pump = ontology_ir.classes["Pump"]
    field_paths = {s.path_local for s in pump.property_shapes}
    # The medium-compatibility sh:sparql constraint shares hasConnectionPoint's path
    # but produces no field of its own (it's attached as a supplementary note to
    # whichever field shares its path, or left standalone if none do).
    sparql_notes = [
        note for shape in pump.property_shapes for note in shape.supplementary_notes
        if note.kind == 'sparql'
    ]
    standalone_sparql = [c for c in pump.complex_constraints if c.kind == 'sparql']
    assert len(sparql_notes) + len(standalone_sparql) >= 1
    assert "hasConnectionPoint" in field_paths  # confirms fields still exist alongside it


def test_window_qualified_connection_points_with_medium_notes(ontology_ir):
    window = ontology_ir.classes["Window"]
    field_names = {s.field_name for s in window.property_shapes}
    assert "inlet_connection_point" in field_names
    assert "outlet_connection_point" in field_names
    for shape in window.property_shapes:
        assert shape.qualified is True
        assert len(shape.supplementary_notes) >= 1  # EM-Light/Fluid-Air sh:or


def test_domain_space_has_domain_is_simple_field(ontology_ir):
    domain_space = ontology_ir.classes["DomainSpace"]
    has_domain = next(s for s in domain_space.property_shapes if s.path_local == "hasDomain")
    assert has_domain.qualified is False
    assert has_domain.target_class_local == "EnumerationKind-Domain"
    assert has_domain.min_count == 1
    assert has_domain.max_count == 1


def test_domain_space_inverse_path_is_complex(ontology_ir):
    domain_space = ontology_ir.classes["DomainSpace"]
    field_paths = {s.path_local for s in domain_space.property_shapes}
    assert "encloses" not in field_paths  # only reachable via sh:inversePath here
    assert any(c.kind == 'inverse-path' for c in domain_space.complex_constraints)


def test_physical_space_contains_encloses_are_simple_fields(ontology_ir):
    physical_space = ontology_ir.classes["PhysicalSpace"]
    field_names = {s.field_name: s for s in physical_space.property_shapes}
    assert "contains" in field_names
    assert "encloses" in field_names
    assert field_names["contains"].target_class_local == "PhysicalSpace"
    assert field_names["encloses"].target_class_local == "DomainSpace"


def test_physical_space_parent_is_dropped_meta_class(ontology_ir):
    # Real ontology: PhysicalSpace rdfs:subClassOf s223:Concept (a meta marker,
    # not a generated class) - so no in-scope parent survives filtering.
    physical_space = ontology_ir.classes["PhysicalSpace"]
    assert physical_space.parent_local_names == []


def test_domain_space_parent_is_connectable(ontology_ir):
    domain_space = ontology_ir.classes["DomainSpace"]
    assert domain_space.parent_local_names == ["Connectable"]


def test_quantifiable_observable_property_multiple_inheritance(ontology_ir):
    qop = ontology_ir.classes["QuantifiableObservableProperty"]
    assert set(qop.parent_local_names) == {"ObservableProperty", "QuantifiableProperty"}


def test_enumeration_values_flagged_and_bucketed(ontology_ir):
    setpoint = ontology_ir.classes["Aspect-Setpoint"]
    assert setpoint.is_enumeration_value is True
    assert setpoint.bucket == "enumerationkinds"
    assert setpoint.class_name == "Setpoint"

    threshold = ontology_ir.classes["Aspect-Threshold"]
    assert threshold.class_name == "Threshold"


def test_properties_bucketed_correctly(ontology_ir):
    assert ontology_ir.classes["Property"].bucket == "properties"
    assert ontology_ir.classes["QuantifiableObservableProperty"].bucket == "properties"


def test_entities_bucketed_correctly(ontology_ir):
    assert ontology_ir.classes["Pump"].bucket == "entities"
    assert ontology_ir.classes["DomainSpace"].bucket == "entities"


def test_relation_kinds_and_inverse(ontology_ir):
    has_cp = ontology_ir.relations["hasConnectionPoint"]
    assert has_cp.kind == "RelationWithInverse"
    assert has_cp.inverse_of_local == "isConnectionPointOf"

    has_medium = ontology_ir.relations["hasMedium"]
    assert has_medium.kind == "Relation"
    assert has_medium.inverse_of_local is None


def test_quantitykinds_referenced_recorded(ontology_ir):
    assert "Pressure" in ontology_ir.quantitykinds_referenced
    assert "Temperature" in ontology_ir.quantitykinds_referenced
    assert len(ontology_ir.quantitykinds_referenced) >= 10
