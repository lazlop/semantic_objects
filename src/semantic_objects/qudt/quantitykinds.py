from ..core import NamedNode, semantic_object
from ..namespaces import QK

@semantic_object
class QuantityKind(NamedNode):
    _name = 'QuantityKind'
    _ns = QK

@semantic_object
class Area(QuantityKind):
    _name = 'Area'

@semantic_object
class Azimuth(QuantityKind):
    _name = 'Azimuth'

@semantic_object
class Tilt(QuantityKind):
    _name = 'Tilt'

@semantic_object
class Power(QuantityKind):
    _name = 'Power'

@semantic_object
class Pressure(QuantityKind):
    _name = 'Pressure'

@semantic_object
class Temperature(QuantityKind):
    pass