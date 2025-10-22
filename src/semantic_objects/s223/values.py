from ..core import * 
from ..units import * 
from .core import Node
from .relations import * 
from typing import Optional
from semantic_mpc_interface.namespaces import QK, UNIT
from rdflib import URIRef
from ..qudt import quantitykinds
from dataclasses import dataclass, Field


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
class Property(Node, Value):
    _local_name = 'Property'
    _valid_relations = [(hasQuantityKind, quantitykinds.QuantityKind),
                        (hasValue, Value),
                        (hasUnit, Unit)]

@dataclass
class QuantifiableObervableProperty(Property):
    _local_name = 'QuantifiableObservableProperty'
    qk: quantitykinds.QuantityKind = required_field(qualified=False)
    value: Value = required_field()
    unit: Unit = required_field()
    def __init__(self, value, unit: Optional[Unit] = None):
        self.value = value
        if unit == None:
            self.unit = DEFAULT_UNIT_MAP[self.qk][DEFAULT_UNIT_SYSTEM]

# should probably be part of global behavior for rewritten 
def auto_fixed_fields(cls):
    """Automatically converts any redefined parent fields into fixed fields"""
    # Get parent class fields and their types
    parent_fields = {}
    for base in cls.__mro__[1:]:
        if hasattr(base, '__dataclass_fields__'):
            parent_fields.update(base.__dataclass_fields__)
    
    # Ensure cls has __annotations__
    if not hasattr(cls, '__annotations__'):
        cls.__annotations__ = {}
    
    # Check which ones are redefined in this class
    for field_name, parent_field in parent_fields.items():
        if field_name in cls.__dict__ and not isinstance(getattr(cls, field_name), type(field)):
            fixed_value = cls.__dict__[field_name]
            # Copy the type annotation from parent
            cls.__annotations__[field_name] = parent_field.type
            # Set as fixed field
            setattr(cls, field_name, field(default=fixed_value, init=False))
    
    return dataclass(cls)

@auto_fixed_fields
class Area(QuantifiableObervableProperty):
    _local_name = 'Area'
    qk = quantitykinds.Area

class Azimuth(QuantifiableObervableProperty):
    _local_name = 'Azimuth'
    qk = quantitykinds.Azimuth

class Tilt(QuantifiableObervableProperty):
    _local_name = 'Tilt'
    qk = quantitykinds.Tilt
