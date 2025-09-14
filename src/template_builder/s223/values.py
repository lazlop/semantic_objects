from ..core import * 
from ..units import * 
from .core import Node
from .relations import * 
from typing import Optional
from semantic_mpc_interface.namespaces import QK, UNIT
from rdflib import URIRef


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

@dataclass
class QuantifiableObervableProperty(Node):
    _iri = 'QuantifiableObservableProperty'
    qk: URIRef
    # TODO: maybe also just make unit a URIRef? Make simple wrappers for URIRefs? 

    # TODO: need to add a bit more to this class
    # QK: Always just doing URIRef? Should this be a class too? 
    def __init__(self, value, unit: Optional[Unit] = None):
        self.value = value
        if unit == None:
            self.unit = DEFAULT_UNIT_MAP[self.qk][DEFAULT_UNIT_SYSTEM]
    
    # def __repr__(self):
    #     return f"QOP(value={self.value}, unit='{self.unit}, qk='{self.qk}')"


class Area(QuantifiableObervableProperty):
    # predicates and objects
    value: Value 
    unit: Unit
    qk = QK['Area']
    relations = [
        (hasValue, 'value'),
        (hasUnit, 'unit'),
        (hasQuantityKind, 'qk')
    ]

class Azimuth(QuantifiableObervableProperty):
    _iri = 'Azimuth'
    value: Value
    unit: Unit
    qk = QK['Azimuth']
    relations = [
        (hasValue, 'value'),
        (hasUnit, 'unit'),
        (hasQuantityKind, 'qk')
    ]

class Tilt(QuantifiableObervableProperty):
    _iri = 'Tilt'
    value: Value
    unit: Unit
    qk = QK['Tilt']
    relations = [
        (hasValue, 'value'),
        (hasUnit, 'unit'),
        (hasQuantityKind, 'qk')
    ]