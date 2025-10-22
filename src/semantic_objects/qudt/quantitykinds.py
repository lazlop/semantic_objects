from ..core import NamedNode
from dataclasses import dataclass
from ..namespaces import QK

@dataclass
class QuantityKind(NamedNode):
    _local_name = 'QuantityKind'
    _ns = QK

@dataclass
class Area(QuantityKind):
    _local_name = 'Area'

@dataclass
class Azimuth(QuantityKind):
    _local_name = 'Azimuth'

@dataclass
class Tilt(QuantityKind):
    _local_name = 'Tilt'