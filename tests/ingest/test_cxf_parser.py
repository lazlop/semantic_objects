from pathlib import Path

import pytest

from semantic_objects.ingest.cxf.parser import CxfParser

REPO_ROOT = Path(__file__).resolve().parents[2]
CXF_SOURCE_DIR = (REPO_ROOT / "src" / "semantic_objects" / "ontologies" / "cxf"
                  / "Buildings" / "Controls" / "OBC" / "ASHRAE" / "G36")


@pytest.fixture(scope="module")
def ir():
    assert CXF_SOURCE_DIR.exists(), f"CXF ontology not found at {CXF_SOURCE_DIR}"
    return CxfParser(CXF_SOURCE_DIR).parse()


def test_parses_every_file_without_warnings():
    parser = CxfParser(CXF_SOURCE_DIR)
    ir = parser.parse()
    n_files = len(list(CXF_SOURCE_DIR.rglob("*.jsonld")))
    assert len(ir.blocks) + len(ir.enum_types) == n_files
    assert parser.warnings == []


def test_controller_signature(ir):
    block = ir.blocks["TerminalUnits.CoolingOnly.Controller"]
    assert block.class_name == "Controller"
    assert "Controller for cooling only terminal box" in block.description
    input_names = {p.name for p in block.inputs}
    assert {"TZon", "TCooSet", "TSup", "uOpeMod"} <= input_names
    output_names = {p.name for p in block.outputs}
    assert {"VSet_flow", "yDam", "yLowFloAla"} <= output_names
    sub_block_names = {sb.name: sb.block_type_dotted for sb in block.sub_blocks}
    assert sub_block_names["dam"] == "TerminalUnits.CoolingOnly.Subsequences.Dampers"
    assert sub_block_names["ala"] == "TerminalUnits.CoolingOnly.Subsequences.Alarms"


def test_real_port_carries_quantitykind_and_unit(ir):
    block = ir.blocks["TerminalUnits.CoolingOnly.Controller"]
    tzon = next(p for p in block.inputs if p.name == "TZon")
    assert tzon.value_type == "Real"
    assert tzon.quantitykind_local == "ThermodynamicTemperature"
    assert tzon.unit_local == "K"


def test_untyped_parameter_node_is_still_captured(ir):
    # `venStd` has no @type at all in the source JSON-LD (no S231:Parameter,
    # no S231:isOfDataType) - it must not be silently dropped just because its
    # type can't be recovered.
    block = ir.blocks["TerminalUnits.CoolingOnly.Controller"]
    venstd = next(p for p in block.parameters if p.name == "venStd")
    assert venstd.value_type == "Unknown"
    assert "Ventilation standard" in venstd.description


def test_enum_typed_parameter_recovered_from_dotted_default(ir):
    # `ashCliZon` also has no S231:isOfDataType, but its S231:value is the
    # fully-dotted literal path - the parser should recover the enum type from
    # that rather than leaving it 'Unknown' (see damCon/venStd for the -rarer-
    # case where even that isn't possible).
    block = ir.blocks["AHUs.MultiZone.VAV.Controller"]
    ashclizon = next(p for p in block.parameters if p.name == "ashCliZon")
    assert ashclizon.value_type == "Types.ASHRAEClimateZone"
    assert ashclizon.default_value == "Not_Specified"
    assert ashclizon.value_type in ir.enum_types


def test_cdl_external_default_stays_unresolved(ir):
    # `damCon`'s default names a Buildings.Controls.OBC.CDL.* type, which isn't
    # part of the ~45-file G36 corpus we ingest - it must not be mistaken for
    # one of our own EnumerationTypes.
    block = ir.blocks["TerminalUnits.CoolingOnly.Controller"]
    damcon = next(p for p in block.parameters if p.name == "damCon")
    assert damcon.value_type == "Unknown"
    assert damcon.default_value == "Buildings.Controls.OBC.CDL.Types.SimpleController.PI"


def test_sub_block_composition_without_wiring(ir):
    # containsBlock entries become SubBlockIR (name + type); SubBlockIR itself
    # has no field for isConnectedTo/isFinal wiring - composition is captured,
    # wiring is dropped, per design.
    block = ir.blocks["TerminalUnits.CoolingOnly.Controller"]
    assert len(block.sub_blocks) == 9
    from dataclasses import fields as dc_fields
    from semantic_objects.ingest.cxf.ir import SubBlockIR
    assert {f.name for f in dc_fields(SubBlockIR)} == {"name", "block_type_dotted", "description"}


def test_ventilation_standard_enum_type(ir):
    et = ir.enum_types["Types.VentilationStandard"]
    assert et.class_name == "VentilationStandard"
    literal_names = {name for name, _ in et.literals}
    assert literal_names == {"ASHRAE62_1", "California_Title_24"}


def test_quantitykinds_and_units_referenced(ir):
    assert ir.quantitykinds_referenced == {
        "Pressure", "SpecificEnergy", "TemperatureDifference",
        "ThermodynamicTemperature", "Time", "VolumeFlowRate",
    }
    assert ir.units_referenced == {
        "J-PER-KiloGM", "K", "M3-PER-SEC", "PA", "SEC", "UNITLESS",
    }
