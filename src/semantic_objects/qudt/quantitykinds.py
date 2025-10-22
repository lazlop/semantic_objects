from ..core import NamedNode, semantic_object
from ..namespaces import QK

@semantic_object
class QuantityKind(NamedNode):
    _type = 'QuantityKind'
    _ns = QK

@semantic_object
class Area(QuantityKind):
    _type = 'Area'

@semantic_object
class Azimuth(QuantityKind):
    _type = 'Azimuth'

@semantic_object
class Tilt(QuantityKind):
    _type = 'Tilt'