import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..naming import class_name_for
from .ir import BlockIR, CxfIR, EnumTypeIR, PortIR, SubBlockIR

# Constant root every CXF @id in this corpus is nested under - stripped to get
# the dotted path used for Python module/class naming (see emitter.py).
ROOT_PREFIX = 'Buildings.Controls.OBC.ASHRAE.G36.'

_IO_TYPES = {
    'S231:RealInput': ('Real', 'input'),
    'S231:RealOutput': ('Real', 'output'),
    'S231:BooleanInput': ('Boolean', 'input'),
    'S231:BooleanOutput': ('Boolean', 'output'),
    'S231:IntegerInput': ('Integer', 'input'),
    'S231:IntegerOutput': ('Integer', 'output'),
}


def _strip_root(iri_local: str) -> str:
    """'ex:Buildings.Controls.OBC.ASHRAE.G36.Foo.Bar' -> 'Foo.Bar'"""
    if iri_local.startswith('ex:'):
        iri_local = iri_local[len('ex:'):]
    if iri_local.startswith(ROOT_PREFIX):
        iri_local = iri_local[len(ROOT_PREFIX):]
    return iri_local


def _local(ref: Optional[Dict[str, str]], prefix: str) -> Optional[str]:
    """Local name of a {'@id': 'prefix:Name'} reference, or None."""
    if not ref or '@id' not in ref:
        return None
    iri = ref['@id']
    if iri.startswith(prefix):
        return iri[len(prefix):]
    return iri.rsplit('#', 1)[-1].rsplit('/', 1)[-1]


def _extract_default(raw: Any) -> Any:
    """S231:value is either a bare JSON literal, or a typed-literal object
    ({'@value': '0.25', '@type': xsd:decimal}) for values that need to stay
    exact (e.g. '0.005' rather than float rounding surprises elsewhere) - we
    only need a Python-literal-safe repr of it, so normalize both forms to a
    plain str/float/int/bool."""
    if isinstance(raw, dict):
        raw = raw.get('@value')
    if isinstance(raw, str):
        try:
            return float(raw) if ('.' in raw or 'e' in raw.lower()) else int(raw)
        except ValueError:
            return raw  # a Modelica expression like "0.01*VMin_flow" - kept as a string note, not evaluated
    return raw


def _refs(node: Dict[str, Any], key: str) -> List[Dict[str, str]]:
    val = node.get(key)
    if val is None:
        return []
    return val if isinstance(val, list) else [val]


def dotted_to_class_name(dotted_path: str) -> str:
    return class_name_for(dotted_path.rsplit('.', 1)[-1])


class CxfParser:
    """Walks a directory of CXF JSON-LD files (Modelica control-block
    signatures) into a CxfIR. Ontology-agnostic RDF/SHACL machinery in
    ingest/parser.py doesn't apply here - blocks aren't RDF classes with
    rdfs:subClassOf/sh:property, they're Modelica block signatures (named
    inputs/outputs/parameters, optionally composed of named sub-block
    instances) - see the design notes in tutorial/cxf-ingestion-tutorial.ipynb.
    """

    def __init__(self, source_dir: Path):
        self.source_dir = Path(source_dir)
        self.warnings: List[str] = []

    def parse(self) -> CxfIR:
        ir = CxfIR()
        for path in sorted(self.source_dir.rglob('*.jsonld')):
            self._parse_file(path, ir)
        self._resolve_unknown_enum_defaults(ir)
        for block in ir.blocks.values():
            for port in block.inputs + block.outputs + block.parameters:
                if port.quantitykind_local:
                    ir.quantitykinds_referenced.add(port.quantitykind_local)
                if port.unit_local:
                    ir.units_referenced.add(port.unit_local)
        return ir

    def _resolve_unknown_enum_defaults(self, ir: CxfIR) -> None:
        """Some parameter nodes omit S231:isOfDataType entirely but still carry
        a fully-dotted default value, e.g. S231:value =
        'Buildings.Controls.OBC.ASHRAE.G36.Types.ASHRAEClimateZone.Not_Specified'
        for the `ashCliZon` parameter. Once every file (including Types/*.jsonld)
        has been parsed, recover the enum type from that dotted default rather
        than leaving the parameter's type as 'Unknown' - see venStd/damCon for
        the (rarer) case where no such recovery is possible."""
        for block in ir.blocks.values():
            for port in block.parameters:
                if port.value_type != 'Unknown' or not isinstance(port.default_value, str):
                    continue
                prefix, sep, literal_name = port.default_value.rpartition('.')
                if not sep:
                    continue
                dotted_type = _strip_root(prefix)
                if dotted_type in ir.enum_types:
                    port.value_type = dotted_type
                    port.default_value = literal_name

    def _parse_file(self, path: Path, ir: CxfIR) -> None:
        data = json.loads(path.read_text())
        graph = data.get('@graph', [])
        by_id = {node['@id']: node for node in graph if '@id' in node}

        block_nodes = [n for n in graph if n.get('@type') == 'S231:Block']
        enum_type_nodes = [n for n in graph if n.get('@type') == 'S231:EnumerationType']

        for node in block_nodes:
            self._parse_block(node, by_id, ir)
        for node in enum_type_nodes:
            self._parse_enum_type(node, graph, ir)

        if not block_nodes and not enum_type_nodes:
            self.warnings.append(f"{path}: no S231:Block or S231:EnumerationType node found")

    def _parse_block(self, node: Dict[str, Any], by_id: Dict[str, Any], ir: CxfIR) -> None:
        dotted_path = _strip_root(node['@id'])
        description = node.get('S231:documentation') or node.get('S231:description')
        block = BlockIR(
            dotted_path=dotted_path,
            class_name=dotted_to_class_name(dotted_path),
            description=description,
        )

        io_refs = {ref['@id'] for ref in _refs(node, 'S231:hasInput') + _refs(node, 'S231:hasOutput')
                   + _refs(node, 'S231:hasParameter')}

        for ref in _refs(node, 'S231:hasInput'):
            port = self._parse_io(ref, by_id, 'input')
            if port is not None:
                block.inputs.append(port)
        for ref in _refs(node, 'S231:hasOutput'):
            port = self._parse_io(ref, by_id, 'output')
            if port is not None:
                block.outputs.append(port)
        for ref in _refs(node, 'S231:hasParameter'):
            port = self._parse_parameter(ref, by_id)
            if port is not None:
                block.parameters.append(port)
        for ref in _refs(node, 'S231:containsBlock'):
            if ref['@id'] in io_refs:
                continue  # already captured as an input/output/parameter above
            sub = self._parse_sub_block(ref, by_id)
            if sub is not None:
                block.sub_blocks.append(sub)

        ir.blocks[dotted_path] = block

    def _parse_io(self, ref: Dict[str, str], by_id: Dict[str, Any], kind: str) -> Optional[PortIR]:
        target = by_id.get(ref['@id'])
        if target is None:
            self.warnings.append(f"unresolved {kind} reference: {ref['@id']}")
            return None
        type_info = _IO_TYPES.get(target.get('@type'))
        value_type = type_info[0] if type_info else 'Unknown'
        name = target.get('S231:label') or _strip_root(target['@id']).rsplit('.', 1)[-1]
        qk_local = _local(target.get('qudt:hasQuantityKind'), 'q:')
        unit_local = _local(target.get('qudt:hasUnit'), 'unit:')
        return PortIR(
            name=name,
            kind=kind,
            value_type=value_type,
            description=target.get('S231:description'),
            quantitykind_local=qk_local,
            unit_local=unit_local,
        )

    def _parse_parameter(self, ref: Dict[str, str], by_id: Dict[str, Any]) -> Optional[PortIR]:
        target = by_id.get(ref['@id'])
        if target is None:
            self.warnings.append(f"unresolved parameter reference: {ref['@id']}")
            return None
        name = target.get('S231:label') or _strip_root(target['@id']).rsplit('.', 1)[-1]
        datatype_ref = target.get('S231:isOfDataType')
        if datatype_ref is None:
            value_type = 'Unknown'
        else:
            dt_id = datatype_ref.get('@id', '')
            if dt_id.startswith('S231:'):
                value_type = dt_id[len('S231:'):]  # Real | Boolean | Integer
            else:
                value_type = _strip_root(dt_id)  # dotted path of a custom EnumerationType
        return PortIR(
            name=name,
            kind='parameter',
            value_type=value_type,
            description=target.get('S231:description'),
            quantitykind_local=_local(target.get('qudt:hasQuantityKind'), 'q:'),
            unit_local=_local(target.get('qudt:hasUnit'), 'unit:'),
            default_value=_extract_default(target.get('S231:value')),
        )

    def _parse_sub_block(self, ref: Dict[str, str], by_id: Dict[str, Any]) -> Optional[SubBlockIR]:
        target = by_id.get(ref['@id'])
        if target is None or target.get('@type') is None:
            return None
        block_type = target['@type']
        if block_type.startswith('S231:'):
            return None  # a plain leaf value (S231:Parameter/etc under containsBlock), not a sub-block instance
        name = target.get('S231:label') or _strip_root(target['@id']).rsplit('.', 1)[-1]
        return SubBlockIR(
            name=name,
            block_type_dotted=_strip_root(block_type),
            description=target.get('S231:description'),
        )

    def _parse_enum_type(self, node: Dict[str, Any], graph: List[Dict[str, Any]], ir: CxfIR) -> None:
        dotted_path = _strip_root(node['@id'])
        enum_type = EnumTypeIR(
            dotted_path=dotted_path,
            class_name=dotted_to_class_name(dotted_path),
            description=node.get('S231:description'),
        )
        for literal in graph:
            if literal.get('@type') == node['@id']:
                lit_name = literal.get('S231:label') or literal['@id'].rsplit('.', 1)[-1]
                enum_type.literals.append((lit_name, literal.get('S231:description')))
        ir.enum_types[dotted_path] = enum_type
