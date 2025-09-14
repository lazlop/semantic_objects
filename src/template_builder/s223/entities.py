from ..core import * 
from .core import Node
from .. import units
from .values import Area, Azimuth, Tilt
from .relations import * 
from typing import Optional, Self
from dataclasses import dataclass, field
from functools import partial
# Should node_uris be generated based on var names? should that or label be required or optionally provided?

class DomainSpace(Node):
    _iri = 'DomainSpace'
    label = "Domain Space"

@dataclass
class PhysicalSpace(Node):
    _iri = 'PhysicalSpace'
    label = "Physical Space"
    comment = "A `PhysicalSpace` is an architectural concept representing a room, a part of a room, a collection of rooms, or any other physical region in a building. PhysicalSpaces may be grouped to define larger `PhysicalSpace`s using the relation `contains` (see {s223:contains})."
    # should probably be optional[list[self]], since multiple spaces can be contained, but I want to minimize typing if possible
    contains: Self = valid_field(contains)
    encloses: DomainSpace = valid_field(encloses)

@dataclass
class Space(PhysicalSpace):
    area: Area = required_field(hasProperty)

    
@dataclass
class Space_TwoArea(Space):
    area: Area = required_field(hasProperty)
    area2: Area = required_field(hasProperty)
    

@dataclass
class SpaceOptArea(PhysicalSpace):
    """Space with optional area using field metadata"""
    # INIT false means optional 
    area: Area = optional_field(hasProperty)

@dataclass
class Window(Node):
    """Window with multiple properties using field-based relations"""
    _iri = 'Window'
    area: Area = required_field(hasProperty)
    azimuth: Azimuth = required_field(hasProperty)
    tilt: Tilt = required_field(hasProperty)