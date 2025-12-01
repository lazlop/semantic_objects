from ..core import * 
from ..units import * 
from .core import Node, EnumerationKind, ExternalReference
from .relations import * 
from typing import Optional
from semantic_mpc_interface.namespaces import QK, UNIT
from rdflib import URIRef
from ..qudt import quantitykinds, units, DEFAULT_UNIT_SYSTEM, DEFAULT_UNIT_MAP



@semantic_object
class Property(Node):
    _valid_relations = [(hasAspect, EnumerationKind),
                        (hasValue, ExternalReference),
                        (hasValue, Literal),
                        (hasUnit, Unit)]

@semantic_object
class QuantifiableObervableProperty(Property):
    qk: quantitykinds.QuantityKind = required_field(qualified=False)
    value: float = required_field()
    unit: Unit = required_field()
    def __init__(self, value, unit: Optional[Unit] = None):
        self.value = value
        if unit == None:
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

