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
class Property(Node):
    _local_name = 'Property'

@dataclass
class QuantifiableObervableProperty(Property):
    _local_name = 'QuantifiableObservableProperty'
    qk: URIRef = required_field(qualified=False)
    value: Value = required_field()
    unit: Unit = required_field()
    def __init__(self, value, unit: Optional[Unit] = None):
        self.value = value
        if unit == None:
            self.unit = DEFAULT_UNIT_MAP[self.qk][DEFAULT_UNIT_SYSTEM]
class Area(QuantifiableObervableProperty):
    qk = QK['Area']
    relations = [
        (hasValue, 'value'),
        (hasUnit, 'unit'),
        (hasQuantityKind, 'qk')
    ]

class Azimuth(QuantifiableObervableProperty):
    _local_name = 'Azimuth'
    qk = QK['Azimuth']
    relations = [
        (hasValue, 'value'),
        (hasUnit, 'unit'),
        (hasQuantityKind, 'qk')
    ]

class Tilt(QuantifiableObervableProperty):
    _local_name = 'Tilt'
    qk = QK['Tilt']
    relations = [
        (hasValue, 'value'),
        (hasUnit, 'unit'),
        (hasQuantityKind, 'qk')
    ]
