from ..core import * 
from ..units import * 
from .core import Node
from .relations import * 
from typing import Optional
from semantic_mpc_interface.namespaces import QK, UNIT
from rdflib import URIRef
from ..qudt import quantitykinds


# IP or SI
DEFAULT_UNIT_SYSTEM = 'SI'

#DEFAULT IP: SI units 
DEFAULT_UNIT_MAP = {
    QK['Area']:{
        "SI": UNIT["M2"],
        "IP": UNIT["FT2"]
    },
    QK['Azimuth']:{
        "SI": UNIT["Degree"],
        "IP": UNIT["Degree"]
    },
    QK['Tilt']:{
        "SI": UNIT["Degree"],
        "IP": UNIT["Degree"]
    },
    QK['Power']:{
        "SI": UNIT["KiloW"],
        "IP": UNIT["BTU_IT-PER-HR"]
    },
    QK['Pressure']:{
        "SI": UNIT["PA"],
        "IP": UNIT["PSI"]
    },
}
@semantic_object
class Property(Node, Value):
    _type = 'Property'
    _valid_relations = [(hasQuantityKind, quantitykinds.QuantityKind),
                        (hasValue, Value),
                        (hasValue, Num),
                        (hasUnit, Unit)]

# TODO: need to come up with a better solution for value and unit 
@semantic_object
class QuantifiableObervableProperty(Property):
    _type = 'QuantifiableObservableProperty'
    qk: quantitykinds.QuantityKind = required_field(qualified=False)
    value: Num = required_field()
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
