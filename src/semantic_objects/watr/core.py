from dataclasses import dataclass

from .. import core
from ..namespaces import RDFS, SH, WATR


@dataclass
class Node(core.Node):
    _ns = WATR
    _name = 'Class'
    _other_types = [SH.NodeShape, RDFS.Class]


@dataclass
class ExternalReference(Node):
    _name = 'ExternalReference'


@dataclass
class EnumerationKind(Node):
    pass
