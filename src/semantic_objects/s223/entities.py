from ..core import * 
from .core import Node
from .. import units
from .properties import Area, Azimuth, Tilt, QuantifiableObervableProperty
from .relations import * 
from typing import Optional, Self
from dataclasses import dataclass, field

# TODO: Consider how I'm using localname vs class name. Not consistent 

@semantic_object
class DomainSpace(Node):
    label = "Domain Space"

@semantic_object
class PhysicalSpace(Node):
    label = "Physical Space"
    comment = "A `PhysicalSpace` is an architectural concept representing a room, a part of a room, a collection of rooms, or any other physical region in a building. PhysicalSpaces may be grouped to define larger `PhysicalSpace`s using the relation `contains` (see {s223:contains})."

@semantic_object
class Space(PhysicalSpace):
    area: Area = required_field() 

@semantic_object
class Space_TwoArea(Space):
    """Space with two area fields for testing hierarchy"""
    area2: Area = required_field()

@semantic_object
class Window(Node):
    """Window with multiple properties using field-based relations"""
    area: Area = required_field()
    azimuth: Azimuth = required_field()
    tilt: Tilt = required_field()