from dataclasses import dataclass
from typing import Any, Optional

from .. import core
from ..namespaces import S231
from ..qudt import QuantityKind, Unit


@dataclass
class Node(core.Node):
    _ns = S231
    _name = 'Class'


@dataclass
class EnumerationKind(Node):
    pass


@dataclass
class Block(Node):
    """A CXF control-block signature: named inputs, outputs, parameters, and
    (for composite blocks) named sub-block instances.

    Captures the block's I/O contract only - internal wiring between ports
    (S231:isConnectedTo, S231:isFinal) is out of scope; see
    tutorial/cxf-ingestion-tutorial.ipynb.
    """


# --- port / parameter value objects -----------------------------------------
# Plain dataclasses, not @semantic_object/Resource subclasses: a CXF port isn't
# part of the s223 RDF relation graph (no hasQuantityKind/hasValue relations
# apply here) - it's a signal on a control-block signature, so it only needs to
# carry qk/unit/value/description, not RDF-export or relation-inference
# machinery.

@dataclass
class Port:
    description: Optional[str] = None


@dataclass
class RealPort(Port):
    qk: Optional[QuantityKind] = None
    unit: Optional[Unit] = None
    value: Optional[float] = None


@dataclass
class RealInputPort(RealPort):
    pass


@dataclass
class RealOutputPort(RealPort):
    pass


@dataclass
class BooleanPort(Port):
    value: Optional[bool] = None


@dataclass
class BooleanInputPort(BooleanPort):
    pass


@dataclass
class BooleanOutputPort(BooleanPort):
    pass


@dataclass
class IntegerPort(Port):
    value: Optional[int] = None


@dataclass
class IntegerInputPort(IntegerPort):
    pass


@dataclass
class IntegerOutputPort(IntegerPort):
    pass


@dataclass
class Parameter:
    """Base parameter value carrier. Also used as-is (without a Real/Boolean/
    Integer/Enum subclass) for the handful of source parameters whose datatype
    can't be recovered at all - no S231:isOfDataType and a default value that
    isn't a resolvable enum literal path (e.g. `damCon`, whose default is the
    CDL-external 'Buildings.Controls.OBC.CDL.Types.SimpleController.PI') -
    `value` then holds that raw string as-is."""
    description: Optional[str] = None
    value: Optional[Any] = None


@dataclass
class RealParameter(Parameter):
    qk: Optional[QuantityKind] = None
    unit: Optional[Unit] = None
    value: Optional[float] = None


@dataclass
class BooleanParameter(Parameter):
    value: Optional[bool] = None


@dataclass
class IntegerParameter(Parameter):
    value: Optional[int] = None


@dataclass
class EnumParameter(Parameter):
    """A parameter whose S231:isOfDataType is a CXF EnumerationType rather than
    Real/Boolean/Integer. `enumeration_kind` is the generated EnumerationKind
    subclass (the type); `value` is one of its literal subclasses (the default),
    mirroring how the rest of semantic_objects references enumeration values by
    class rather than instance."""
    enumeration_kind: Optional[type] = None
    value: Optional[type] = None


@dataclass
class SubBlock:
    """Records that a composite block contains a named instance of another
    block type - structural composition only, no wiring between ports."""
    block_type: Optional[type] = None
    description: Optional[str] = None
