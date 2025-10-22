from ..core import * 
from .core import Node
from .. import units
from .values import Area, Azimuth, Tilt, QuantifiableObervableProperty
from .relations import * 
from typing import Optional, Self
from dataclasses import dataclass, field

class Entity(Node, core.Entity):
    _valid_relations = [
        (hasProperty, QuantifiableObervableProperty),
    ]

@dataclass
class DomainSpace(Entity):
    _local_name = 'DomainSpace'
    label = "Domain Space"

@dataclass
class PhysicalSpace(Entity):
    _local_name = 'PhysicalSpace'
    label = "Physical Space"
    comment = "A `PhysicalSpace` is an architectural concept representing a room, a part of a room, a collection of rooms, or any other physical region in a building. PhysicalSpaces may be grouped to define larger `PhysicalSpace`s using the relation `contains` (see {s223:contains})."
    _valid_relations = [
        (contains, Self),
        (encloses, DomainSpace)
    ]

@dataclass
class Space(PhysicalSpace):
    area: Area = required_field() 

@dataclass
class Space_TwoArea(Space):
    """Space with two area fields for testing hierarchy"""
    _local_name = 'Space'
    area2: Area = required_field()

@dataclass
class Window(Entity):
    """Window with multiple properties using field-based relations"""
    _local_name = 'Window'
    area: Area = required_field()
    azimuth: Azimuth = required_field()
    tilt: Tilt = required_field()

DomainSpace._valid_relations = [
    (hasWindow, Window),
]