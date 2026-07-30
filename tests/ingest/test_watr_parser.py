from pathlib import Path

import pytest

from semantic_objects.ingest.adapters.watr import WatrAdapter
from semantic_objects.ingest.config import IngestConfig
from semantic_objects.ingest.parser import OntologyParser

ONTOLOGY_PATH = (
    Path(__file__).resolve().parents[2]
    / "src" / "semantic_objects" / "ontologies" / "watr" / "water.ttl"
)


@pytest.fixture(scope="module")
def ontology_ir():
    config = IngestConfig(
        ontology_name="watr",
        source_path=ONTOLOGY_PATH,
        output_dir=Path("unused"),
    )
    return OntologyParser(config, WatrAdapter()).parse()


def test_meta_class_excluded(ontology_ir):
    assert "Class" not in ontology_ir.classes


def test_class_and_relation_counts(ontology_ir):
    assert len(ontology_ir.classes) > 300
    assert len(ontology_ir.relations) == 15


def test_relations_are_watr_native_only(ontology_ir):
    # WATR reuses s223 relations (hasRole, hasConnectionPoint) directly rather than
    # redefining them - only WATR's own new relations should appear in its own IR.
    assert "hasProcess" in ontology_ir.relations
    assert "hasAccuracy" in ontology_ir.relations
    assert "hasRole" not in ontology_ir.relations
    assert "hasConnectionPoint" not in ontology_ir.relations
    for rel in ontology_ir.relations.values():
        assert rel.kind == "Relation"
        assert rel.inverse_of_local is None


def test_unit_process_is_abstract_organizational_category(ontology_ir):
    # watr:UnitProcess is typed only rdfs:Class (no sh:NodeShape of its own) - a
    # pure organizational category that several equipment classes mix in.
    unit_process = ontology_ir.classes["UnitProcess"]
    assert unit_process.is_abstract is True
    assert unit_process.parent_local_names == ["Equipment"]


def test_boiler_subclasses_s223_and_watr_parent(ontology_ir):
    boiler = ontology_ir.classes["Boiler"]
    assert set(boiler.parent_local_names) == {"Boiler", "UnitProcess"}
    assert boiler.is_abstract is False


def test_thickener_redundant_multi_parent_survives(ontology_ir):
    # Thickener declares both s223:Equipment and watr:UnitProcess directly, even
    # though UnitProcess already subclasses Equipment - redundant but valid RDFS,
    # and the parser should keep both (the emitter is responsible for ordering
    # them so Python's MRO doesn't choke on it).
    thickener = ontology_ir.classes["Thickener"]
    assert set(thickener.parent_local_names) == {"Equipment", "UnitProcess"}


def test_enum_value_bucketed_via_s223_ancestor(ontology_ir):
    # watr:Role-Feed's only parent is s223:EnumerationKind-Role - water.ttl never
    # restates that class's own ancestry back to the literal s223:EnumerationKind
    # root, so bucket resolution has to consult the already-ingested s223 IR.
    role_feed = ontology_ir.classes["Role-Feed"]
    assert role_feed.bucket == "enumerationkinds"
    assert role_feed.class_name == "Feed"


def test_process_taxonomy_bucketed_as_entities(ontology_ir):
    # The Process-* taxonomy (85 punned class/value nodes under ProcessType) has
    # no s223 or EnumerationKind ancestry - it's WATR's own novel hierarchy.
    aeration = ontology_ir.classes["Process-Aeration"]
    assert aeration.bucket == "entities"
    process_type = ontology_ir.classes["ProcessType"]
    assert process_type.parent_local_names == []


def test_aeration_basin_hasvalue_constraint_preserved_not_a_field(ontology_ir):
    # sh:hasValue/sh:in constraints aren't representable as required_field()/
    # _valid_relations entries - they should show up as complex constraints
    # (preserved for fidelity in _raw_shapes), not silently dropped.
    basin = ontology_ir.classes["AerationBasin"]
    field_paths = {s.path_local for s in basin.property_shapes}
    assert "hasProcess" not in field_paths
    assert any(c.path_local == "hasProcess" for c in basin.complex_constraints)
    assert any(c.path_local == "hasRole" for c in basin.complex_constraints)
