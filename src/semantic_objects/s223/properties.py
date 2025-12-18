from typing import Optional

from rdflib import URIRef

from ..core import *
from ..units import *
from ..qudt import quantitykinds, QuantityKind, units, DEFAULT_UNIT_SYSTEM, DEFAULT_UNIT_MAP
from .core import Node, EnumerationKind, ExternalReference
from .relations import *
from .enumerationkinds import Setpoint, Deadband, Occupancy
from semantic_mpc_interface.namespaces import QK, UNIT


@semantic_object
class Property(Node):
    _valid_relations = [
        (hasAspect, EnumerationKind),
        (hasValue, ExternalReference),
        (hasValue, Literal),
        (hasUnit, Unit),
        (hasQuantityKind, QuantityKind),
    ]


@semantic_object
class QuantifiableObervableProperty(Property):
    qk: quantitykinds.QuantityKind = required_field(qualified=False)
    value: float = required_field()
    unit: Unit = required_field()
    
    def __init__(self, value, unit: Optional[Unit] = None):
        self.value = value
        if unit is None:
            self.unit = DEFAULT_UNIT_MAP[self.qk][DEFAULT_UNIT_SYSTEM]


@semantic_object
class Area(QuantifiableObervableProperty):
    qk = quantitykinds.Area


@semantic_object
class Azimuth(QuantifiableObervableProperty):
    qk = quantitykinds.Azimuth


@semantic_object
class Tilt(QuantifiableObervableProperty):
    qk = quantitykinds.Tilt

@semantic_object
class Area_FT2(Area):
    unit = units.FT2

# TODO: handle lists for things like aspect
@semantic_object
class Area_SP(Area):
    aspects = [Setpoint, Deadband, Occupancy]