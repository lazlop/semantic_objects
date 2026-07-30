from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class PortIR:
    """One S231:RealInput/RealOutput/BooleanInput/.../S231:Parameter entry from
    a block's hasInput/hasOutput/hasParameter list."""
    name: str
    kind: str  # 'input' | 'output' | 'parameter'
    value_type: str  # 'Real' | 'Boolean' | 'Integer' | '<dotted enum type path>' | 'Unknown'
    description: Optional[str]
    quantitykind_local: Optional[str] = None
    unit_local: Optional[str] = None
    default_value: Any = None  # parameters only


@dataclass
class SubBlockIR:
    """A named sub-block instance referenced via containsBlock (composition
    only - wiring between sub-block ports, S231:isConnectedTo, is dropped)."""
    name: str
    block_type_dotted: str
    description: Optional[str]


@dataclass
class BlockIR:
    dotted_path: str  # e.g. TerminalUnits.CoolingOnly.Controller (G36. root stripped)
    class_name: str
    description: Optional[str]
    inputs: List[PortIR] = field(default_factory=list)
    outputs: List[PortIR] = field(default_factory=list)
    parameters: List[PortIR] = field(default_factory=list)
    sub_blocks: List[SubBlockIR] = field(default_factory=list)


@dataclass
class EnumTypeIR:
    dotted_path: str
    class_name: str
    description: Optional[str]
    literals: List[Any] = field(default_factory=list)  # list of (name, description)


@dataclass
class CxfIR:
    blocks: Dict[str, BlockIR] = field(default_factory=dict)       # keyed by dotted_path
    enum_types: Dict[str, EnumTypeIR] = field(default_factory=dict)  # keyed by dotted_path
    quantitykinds_referenced: Set[str] = field(default_factory=set)
    units_referenced: Set[str] = field(default_factory=set)
