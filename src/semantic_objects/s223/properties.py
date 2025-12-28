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
    _semantic_type = QuantifiableObservableProperty


@semantic_object
class Azimuth(QuantifiableObservableProperty):
    qk = quantitykinds.Azimuth
    _semantic_type = QuantifiableObservableProperty


@semantic_object
class Tilt(QuantifiableObservableProperty):
    qk = quantitykinds.Tilt
    _semantic_type = QuantifiableObservableProperty

@semantic_object
class Area_FT2(Area):
    unit = units.FT2
    _semantic_type = QuantifiableObservableProperty

@semantic_object
class Area_SP(Area):
    _semantic_type = QuantifiableObservableProperty
    aspects: Optional[list] = field(
        default=None,
        init=False,
        metadata={
            'relation': hasAspect,
            'exact_values': [Setpoint, Deadband, Occupancy],
            'qualified': False
        }
    )

@semantic_object
class Power(QuantifiableObservableProperty):
    qk = quantitykinds.Power
    _semantic_type = QuantifiableObservableProperty

@semantic_object
class PowerConsumption(QuantifiableObservableProperty):
    qk = quantitykinds.Power
    _semantic_type = QuantifiableObservableProperty

@semantic_object
class AirPressure(QuantifiableObservableProperty):
    qk = quantitykinds.Pressure
    _semantic_type = QuantifiableObservableProperty

@semantic_object
class EnvironmentalStation(Node):
    _name = "Environmental_Station"
    label = "Environmental Station"
    comment = "A comprehensive environmental monitoring station"
    
    power_consumption: PowerConsumption = required_field()
    air_pressure: AirPressure = required_field()
    
    # Optional fields - using hasExternalReference for the station ID
    station_id: Optional[str] = optional_field(relation=hasExternalReference)
    
    def __post_init__(self):
        """Convert raw values to proper property types"""
        super().__post_init__()
        if not isinstance(self.power_consumption, PowerConsumption):
            self.power_consumption = PowerConsumption(self.power_consumption)
        if not isinstance(self.air_pressure, AirPressure):
            self.air_pressure = AirPressure(self.air_pressure)

# Set up valid relations for Node to include hasProperty for QuantifiableObservableProperty
# This needs to be done here to avoid circular imports
if not hasattr(Node, '_valid_relations') or not Node._valid_relations:
    Node._valid_relations = []

# Add the hasProperty relation for QuantifiableObservableProperty
Node._valid_relations.append((hasProperty, QuantifiableObservableProperty))