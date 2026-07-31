from dataclasses import dataclass

from .. import core
from ..namespaces import G36, RDFS, SH


@dataclass
class Node(core.Node):
    _ns = G36
    _name = 'Class'
    _other_types = [SH.NodeShape, RDFS.Class]


@dataclass
class ExternalReference(Node):
    _name = 'ExternalReference'


@dataclass
class EnumerationKind(Node):
    pass
