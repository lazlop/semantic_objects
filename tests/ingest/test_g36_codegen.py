import filecmp
import tempfile
from pathlib import Path

import pytest

from semantic_objects.ingest.adapters.g36 import G36Adapter
from semantic_objects.ingest.codegen.emitter import Emitter
from semantic_objects.ingest.config import IngestConfig
from semantic_objects.ingest.parser import OntologyParser

REPO_ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_PATH = REPO_ROOT / "src" / "semantic_objects" / "ontologies" / "s223" / "223p.ttl"
GENERATED_DIR = REPO_ROOT / "src" / "semantic_objects" / "g36" / "_generated"
EXTERNAL_RELATIONS_MODULE = "semantic_objects.s223.relations"


def _generate_into(output_dir: Path):
    config = IngestConfig(ontology_name="g36", source_path=ONTOLOGY_PATH, output_dir=output_dir)
    adapter = G36Adapter()
    ir = OntologyParser(config, adapter).parse()
    Emitter(ir, adapter.scaffold_parent_local_names(), ONTOLOGY_PATH, output_dir, "g36",
            external_relations_module=EXTERNAL_RELATIONS_MODULE).emit()


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
        "g36/_generated/ not found - run `python -m semantic_objects.ingest.cli --ontology g36` first"
    )
    import importlib
    from semantic_objects.s223 import entities as s223_entities, relations as s223_relations
    entities = importlib.import_module("semantic_objects.g36._generated.entities")
    relations = importlib.import_module("semantic_objects.g36._generated.relations")
    return entities, relations, s223_entities, s223_relations


def test_all_eleven_g36_classes_generated(generated):
    entities, _, _, _ = generated
    expected = {
        'ChilledWaterCoil', 'ChilledWaterValve', 'Damper', 'ElectricHeatingCoil', 'Fan',
        'FanWithVFD', 'HotWaterCoil', 'HotWaterValve', 'TwoPositionDamper', 'Zone', 'ZoneGroup',
    }
    assert expected <= set(entities.__all__)


def test_g36_classes_subclass_real_s223_classes(generated):
    entities, _, s223_entities, _ = generated
    assert issubclass(entities.Zone, s223_entities.Zone)
    assert issubclass(entities.Fan, s223_entities.Fan)
    assert issubclass(entities.FanWithVFD, entities.Fan)
    assert issubclass(entities.FanWithVFD, s223_entities.Fan)
    assert issubclass(entities.ChilledWaterCoil, s223_entities.CoolingCoil)
    assert issubclass(entities.ZoneGroup, s223_entities.Zone)


def test_asserted_type_is_the_real_s223_ancestor_not_the_g36_name(generated):
    # g36 classes are never asserted as their own RDF type - see g36:XAnnotation's
    # SHACL inference rule (tutorial/g36-extension-tutorial.ipynb section 2.3).
    # A class whose Python name doesn't coincide with its s223 parent's name (e.g.
    # FanWithVFD, ChilledWaterCoil, ZoneGroup) must not leak its own name into `_name`.
    entities, _, _, _ = generated
    assert entities.FanWithVFD._name == 'Fan'
    assert entities.ChilledWaterCoil._name == 'CoolingCoil'
    assert entities.ZoneGroup._name == 'Zone'
    assert entities.ElectricHeatingCoil._name == 'ElectricResistanceElement'
    # coincidentally-same-named classes still resolve correctly
    assert entities.Zone._name == 'Zone'
    assert entities.Fan._name == 'Fan'


def test_g36_fields_reuse_the_real_s223_relation_objects(generated):
    entities, relations, _, s223_relations = generated
    assert relations.hasProperty is s223_relations.hasProperty
    fan_field = entities.Fan.__dataclass_fields__['enumerated_actuatable_property']
    assert fan_field.metadata['relation'] is s223_relations.hasProperty
    coil_field = entities.ChilledWaterCoil.__dataclass_fields__['chilled_water_valve']
    assert coil_field.metadata['relation'] is s223_relations.connectedTo


def test_instantiation_and_sparql_smoke(generated):
    entities, _, s223_entities, _ = generated
    from semantic_objects.s223 import properties as s223_properties, enumerationkinds

    air = enumerationkinds.Air()
    connection = s223_entities.Connection(medium=air)
    outlet = s223_entities.OutletConnectionPoint(medium=air, connection=connection)
    inlet = s223_entities.InletConnectionPoint(medium=air, connection=connection)
    start_stop = s223_properties.EnumeratedActuatableProperty(enumeration_kind=enumerationkinds.OnOff())

    fan = entities.Fan(outlet_connection_point=outlet, inlet_connection_point=inlet,
                        enumerated_actuatable_property=start_stop)
    assert type(fan)._name == 'Fan'

    query = entities.FanWithVFD.get_sparql_query()
    assert "s223:Fan" in query
    assert "s223:FanWithVFD" not in query
