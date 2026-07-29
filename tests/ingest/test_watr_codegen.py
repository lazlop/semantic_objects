import filecmp
import tempfile
from pathlib import Path

import pytest

from semantic_objects.ingest.adapters.watr import WatrAdapter
from semantic_objects.ingest.codegen.emitter import Emitter
from semantic_objects.ingest.config import IngestConfig
from semantic_objects.ingest.parser import OntologyParser

REPO_ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_PATH = REPO_ROOT / "src" / "semantic_objects" / "ontologies" / "watr" / "water.ttl"
GENERATED_DIR = REPO_ROOT / "src" / "semantic_objects" / "watr" / "_generated"


def _generate_into(output_dir: Path):
    config = IngestConfig(ontology_name="watr", source_path=ONTOLOGY_PATH, output_dir=output_dir)
    adapter = WatrAdapter()
    ir = OntologyParser(config, adapter).parse()
    Emitter(ir, adapter.scaffold_parent_local_names(), ONTOLOGY_PATH, output_dir, "watr", adapter=adapter).emit()


def test_generation_is_idempotent():
    with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
        out1, out2 = Path(d1), Path(d2)
        _generate_into(out1)
        _generate_into(out2)
        files1 = sorted(p.name for p in out1.glob("*.py"))
        files2 = sorted(p.name for p in out2.glob("*.py"))
        assert files1 == files2
        for name in files1:
            if name == "_meta.py":
                continue
            assert filecmp.cmp(out1 / name, out2 / name, shallow=False), f"{name} differs between runs"


@pytest.fixture(scope="module")
def generated():
    assert (GENERATED_DIR / "entities.py").exists(), (
        "watr/_generated/ not found - run `python -m semantic_objects.ingest.cli --ontology watr` first"
    )
    import importlib
    entities = importlib.import_module("semantic_objects.watr._generated.entities")
    properties = importlib.import_module("semantic_objects.watr._generated.properties")
    enumerationkinds = importlib.import_module("semantic_objects.watr._generated.enumerationkinds")
    relations = importlib.import_module("semantic_objects.watr._generated.relations")
    return entities, properties, enumerationkinds, relations


@pytest.fixture(scope="module")
def s223_generated():
    import importlib
    return importlib.import_module("semantic_objects.s223")


def test_boiler_subclasses_s223_boiler_and_watr_unit_process(generated, s223_generated):
    entities, _, _, _ = generated
    assert issubclass(entities.Boiler, s223_generated.Boiler)
    assert any(c.__name__ == "UnitProcess" for c in entities.Boiler.__mro__)


def test_thickener_mro_resolves_redundant_multi_parent(generated, s223_generated):
    # Thickener(s223:Equipment, watr:UnitProcess) is a redundant multi-parent
    # declaration (UnitProcess already subclasses Equipment) - Python's C3
    # linearization requires the more-derived parent (UnitProcess) first, which
    # the emitter must arrange for on its own since RDF doesn't order this for us.
    entities, _, _, _ = generated
    assert issubclass(entities.Thickener, entities.UnitProcess)
    assert issubclass(entities.Thickener, s223_generated.Equipment)


def test_valve_same_named_external_parent_not_self_referential(generated, s223_generated):
    # watr:ButterflyValve/Valve reuses the local name "Valve" while also
    # subclassing s223:Valve - a same-name collision the emitter has to resolve
    # to the external class, not back to itself.
    entities, _, _, _ = generated
    assert issubclass(entities.Valve, s223_generated.Valve)
    assert entities.Valve is not s223_generated.Valve


def test_enumeration_kind_reuses_s223_role_not_a_duplicate(generated, s223_generated):
    enumerationkinds = generated[2]
    assert issubclass(enumerationkinds.Feed, s223_generated.enumerationkinds.Role)


def test_watr_relations_use_watr_namespace(generated):
    _, _, _, relations = generated
    assert relations.hasProcess._ns == relations.Predicate._ns
    from semantic_objects.namespaces import WATR
    assert relations.Predicate._ns == WATR


def test_aeration_basin_valid_relations_reuse_s223_predicate_objects(generated, s223_generated):
    # AerationBasin's hasRole entry (surfaced via _valid_relations on its Reactor/
    # Tank ancestry, not a field of its own) must be the *same* Predicate object
    # s223 already generated, not a second watr-namespaced duplicate - otherwise
    # code elsewhere comparing `relation is relations.hasRole` would silently
    # never match a WATR-authored instance.
    entities, _, _, _ = generated
    valid_relation_predicates = {r for r, _ in entities.AerationBasin._valid_relations}
    assert s223_generated.hasRole in valid_relation_predicates


def test_unresolved_shapes_recorded_not_silently_dropped(generated):
    from semantic_objects.watr._generated import _meta
    assert "UnitProcess" in _meta.UNRESOLVED_NOTES
