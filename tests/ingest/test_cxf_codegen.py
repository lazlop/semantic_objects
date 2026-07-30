import filecmp
import tempfile
from pathlib import Path

import pytest

from semantic_objects.ingest.cxf.emitter import CxfEmitter
from semantic_objects.ingest.cxf.parser import CxfParser

REPO_ROOT = Path(__file__).resolve().parents[2]
CXF_SOURCE_DIR = (REPO_ROOT / "src" / "semantic_objects" / "ontologies" / "cxf"
                  / "Buildings" / "Controls" / "OBC" / "ASHRAE" / "G36")
GENERATED_DIR = REPO_ROOT / "src" / "semantic_objects" / "cxf" / "_generated"


def _generate_into(output_dir: Path):
    ir = CxfParser(CXF_SOURCE_DIR).parse()
    CxfEmitter(ir, CXF_SOURCE_DIR, output_dir).emit()


def _all_py_files(root: Path):
    return sorted(p.relative_to(root) for p in root.rglob("*.py"))


def test_generation_is_idempotent():
    with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
        out1, out2 = Path(d1), Path(d2)
        _generate_into(out1)
        _generate_into(out2)
        files1, files2 = _all_py_files(out1), _all_py_files(out2)
        assert files1 == files2
        for rel in files1:
            if rel.name == "_meta.py":
                continue
            assert filecmp.cmp(out1 / rel, out2 / rel, shallow=False), f"{rel} differs between runs"


@pytest.fixture(scope="module")
def cxf():
    assert (GENERATED_DIR / "blocks" / "__init__.py").exists(), (
        "cxf/_generated/ not found - run `python -m semantic_objects.ingest.cli --ontology cxf` first"
    )
    import semantic_objects.cxf as cxf
    return cxf


def test_every_block_and_enum_kind_imports_and_instantiates(cxf):
    assert len(cxf.blocks.__all__) == 37
    for name in cxf.blocks.__all__:
        getattr(cxf.blocks, name)()  # every field defaults via a factory - must not raise
    for name in cxf.enumerationkinds.__all__:
        getattr(cxf.enumerationkinds, name)._get_iri()


def test_no_name_collisions_survive_flattening(cxf):
    # Several distinct blocks/literals share a leaf name across sibling CXF
    # folders (three different Controllers, two different Alarms, two
    # different 'Not_Specified' climate-zone literals) - the flat re-export
    # surfaces must alias every one of them rather than silently shadowing.
    import collections
    block_dupes = [n for n, c in collections.Counter(cxf.blocks.__all__).items() if c > 1]
    enum_dupes = [n for n, c in collections.Counter(cxf.enumerationkinds.__all__).items() if c > 1]
    assert block_dupes == []
    assert enum_dupes == []
    assert "CoolingOnlyController" in cxf.blocks.__all__
    assert "ReheatController" in cxf.blocks.__all__
    assert "VavController" in cxf.blocks.__all__


def test_controller_fields_carry_qk_unit_description(cxf):
    controller = cxf.blocks.CoolingOnlyController()
    from semantic_objects.qudt import quantitykinds, units
    assert controller.TZon.qk is quantitykinds.ThermodynamicTemperature
    assert controller.TZon.unit is units.K
    assert controller.TZon.description == "Measured room temperature"
    assert controller.kCooCon.value == 0.1


def test_sub_block_composition_resolves_to_real_generated_classes(cxf):
    from semantic_objects.cxf.core import SubBlock
    controller = cxf.blocks.CoolingOnlyController()
    assert isinstance(controller.dam, SubBlock)
    assert controller.dam.block_type is cxf.blocks.Dampers


def test_ambiguous_sub_blocks_resolve_to_distinct_types(cxf):
    # `minFlo` (Title24 Setpoints) and `setPoi` (ASHRAE62_1 Setpoints) on the
    # same Controller must not collapse onto the same imported block_type.
    controller = cxf.blocks.CoolingOnlyController()
    assert controller.minFlo.block_type is not controller.setPoi.block_type


def test_enum_parameter_resolves_to_generated_enumeration_kind(cxf):
    vav = cxf.blocks.VavController()
    assert vav.ashCliZon.enumeration_kind is cxf.enumerationkinds.ASHRAEClimateZone
    assert issubclass(vav.ashCliZon.value, cxf.enumerationkinds.ASHRAEClimateZone)
    assert vav.ashCliZon.value.__name__ == "ASHRAEClimateZone_Not_Specified"


def test_unresolvable_parameter_type_falls_back_without_crashing(cxf):
    controller = cxf.blocks.CoolingOnlyController()
    assert controller.venStd.value is None
    assert controller.damCon.value == "Buildings.Controls.OBC.CDL.Types.SimpleController.PI"
