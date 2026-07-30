import filecmp
import shutil
import tempfile
from pathlib import Path

import pytest

from semantic_objects.ingest.adapters.s223 import S223Adapter
from semantic_objects.ingest.codegen.emitter import Emitter
from semantic_objects.ingest.config import IngestConfig
from semantic_objects.ingest.parser import OntologyParser

REPO_ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_PATH = REPO_ROOT / "src" / "semantic_objects" / "ontologies" / "s223" / "223p.ttl"
GENERATED_DIR = REPO_ROOT / "src" / "semantic_objects" / "s223" / "_generated"


def _generate_into(output_dir: Path):
    config = IngestConfig(ontology_name="s223", source_path=ONTOLOGY_PATH, output_dir=output_dir)
    adapter = S223Adapter()
    ir = OntologyParser(config, adapter).parse()
    Emitter(ir, adapter.scaffold_parent_local_names(), ONTOLOGY_PATH, output_dir, "s223", adapter=adapter).emit()


def test_generation_is_idempotent():
    with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
        out1, out2 = Path(d1), Path(d2)
        _generate_into(out1)
        _generate_into(out2)
        files1 = sorted(p.name for p in out1.glob("*.py"))
        files2 = sorted(p.name for p in out2.glob("*.py"))
        assert files1 == files2
        # _meta.py embeds GENERATED_AT (a timestamp), so compare everything else byte-for-byte.
        for name in files1:
            if name == "_meta.py":
                continue
            assert filecmp.cmp(out1 / name, out2 / name, shallow=False), f"{name} differs between runs"


@pytest.fixture(scope="module")
def generated():
    assert (GENERATED_DIR / "entities.py").exists(), (
        "s223/_generated/ not found - run `python -m semantic_objects.ingest.cli --ontology s223` first"
    )
    import importlib
    entities = importlib.import_module("semantic_objects.s223._generated.entities")
    properties = importlib.import_module("semantic_objects.s223._generated.properties")
    enumerationkinds = importlib.import_module("semantic_objects.s223._generated.enumerationkinds")
    relations = importlib.import_module("semantic_objects.s223._generated.relations")
    return entities, properties, enumerationkinds, relations


def test_domain_space_import_and_fields(generated):
    entities, _, _, relations = generated
    assert "domain" in entities.DomainSpace.__dataclass_fields__
    field = entities.DomainSpace.__dataclass_fields__["domain"]
    assert field.metadata["relation"] is relations.hasDomain
    assert field.metadata["min"] == 1
    assert field.metadata["max"] == 1
    assert entities.DomainSpace.__mro__[1] is entities.Connectable


def test_physical_space_import_and_valid_relations(generated):
    entities, _, _, relations = generated
    assert entities.PhysicalSpace.__dataclass_fields__ == {}
    targets = {r._name if hasattr(r, "_name") else r for r, _ in entities.PhysicalSpace._valid_relations}
    assert relations.contains in [r for r, _ in entities.PhysicalSpace._valid_relations]
    assert relations.encloses in [r for r, _ in entities.PhysicalSpace._valid_relations]


def test_pump_qualified_connection_point_fields(generated):
    entities, _, _, relations = generated
    fields = entities.Pump.__dataclass_fields__
    assert "outlet_connection_point" in fields
    assert "inlet_connection_point" in fields
    outlet = fields["outlet_connection_point"]
    assert outlet.type is entities.OutletConnectionPoint
    assert outlet.metadata["relation"] is relations.hasConnectionPoint
    assert outlet.metadata["qualified"] is True
    assert outlet.metadata["min"] == 1


def test_quantifiable_observable_property_multiple_inheritance(generated):
    _, properties, _, _ = generated
    assert properties.ObservableProperty in properties.QuantifiableObservableProperty.__bases__
    assert properties.QuantifiableProperty in properties.QuantifiableObservableProperty.__bases__


def test_enumerationkinds_disambiguated_names(generated):
    _, _, enumerationkinds, _ = generated
    assert enumerationkinds.Setpoint._name == "Aspect-Setpoint"
    assert enumerationkinds.Threshold._name == "Aspect-Threshold"
    assert enumerationkinds.Setpoint is not enumerationkinds.Threshold


def test_relation_ontology_iri(generated):
    _, _, _, relations = generated
    assert str(relations.hasConnectionPoint._get_iri()) == "http://data.ashrae.org/standard223#hasConnectionPoint"


def test_instantiation_and_sparql_and_shacl_smoke(generated):
    entities, _, enumerationkinds, _ = generated
    water = enumerationkinds.Water()
    connection = entities.Connection(medium=water)
    outlet = entities.OutletConnectionPoint(medium=water, connection=connection)
    inlet = entities.InletConnectionPoint(medium=water, connection=connection)
    pump = entities.Pump(outlet_connection_point=outlet, inlet_connection_point=inlet)
    assert pump._name

    query = entities.DomainSpace.get_sparql_query(ontology="s223")
    assert "s223:hasDomain" in query
    assert "s223:DomainSpace" in query

    shacl = pump.__class__.generate_rdf_class_definition()
    assert "s223:Pump" in shacl
    assert "s223:hasConnectionPoint" in shacl

    yaml_out = entities.DomainSpace.to_yaml()
    assert "DomainSpace" in yaml_out
    assert "hasDomain" in yaml_out
