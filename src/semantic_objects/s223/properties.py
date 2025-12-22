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
class QuantifiableObservableProperty(Property):
    qk: quantitykinds.QuantityKind = required_field(qualified=False)
    value: float = required_field()
    unit: Optional[Unit] = field(default=None, metadata={'relation': None, 'min': 1, 'max': None, 'qualified': True})
    
    def __post_init__(self):
        """Set default unit if not provided"""
        super().__post_init__()
        # If unit wasn't set, set it from DEFAULT_UNIT_MAP
        if self.unit is None:
            self.unit = DEFAULT_UNIT_MAP[self.qk][DEFAULT_UNIT_SYSTEM]


@semantic_object
class Area(QuantifiableObservableProperty):
    qk = quantitykinds.Area


@semantic_object
class Azimuth(QuantifiableObservableProperty):
    qk = quantitykinds.Azimuth


@semantic_object
class Tilt(QuantifiableObservableProperty):
    qk = quantitykinds.Tilt

@semantic_object
class Area_FT2(Area):
    unit = units.FT2

# TODO: handle lists for things like aspect
@semantic_object
class Area_SP(Area):
    aspects = [Setpoint, Deadband, Occupancy]
