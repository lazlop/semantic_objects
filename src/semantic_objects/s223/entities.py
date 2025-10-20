from ..core import * 
from .core import Node
from .. import units
from .values import Area, Azimuth, Tilt
from .relations import * 
from typing import Optional, Self
from dataclasses import dataclass, field

# Should node_uris be generated based on var names? should that or label be required or optionally provided?
# For rdfs subclasses, should instance also be declared instances of the thing we are subclassing

class DomainSpace(Node):
    _local_name = 'DomainSpace'
    label = "Domain Space"

@dataclass
class PhysicalSpace(Node):
    _local_name = 'PhysicalSpace'
    label = "Physical Space"
    comment = "A `PhysicalSpace` is an architectural concept representing a room, a part of a room, a collection of rooms, or any other physical region in a building. PhysicalSpaces may be grouped to define larger `PhysicalSpace`s using the relation `contains` (see {s223:contains})."
    contains: Self = valid_field()
    encloses: DomainSpace = valid_field()

@dataclass
class Space(PhysicalSpace):
    area: Area = required_field()  # relation will be inferred as hasProperty

    
@dataclass
class Space_TwoArea(Space):
    area: Area = required_field()
    area2: Area = required_field()
    

@dataclass
class SpaceOptArea(PhysicalSpace):
    """Space with optional area using field metadata"""
    # INIT false means optional 
    area: Area = optional_field()

@dataclass
class Window(Node):
    """Window with multiple properties using field-based relations"""
    _local_name = 'Window'
    area: Area = required_field()
    azimuth: Azimuth = required_field()
    tilt: Tilt = required_field()

@dataclass
class DomainAndPhysicalSpace(PhysicalSpace, DomainSpace):
    """Space with optional area using field metadata"""
    _local_name = 'DomainAndPhysicalSpace'

class ConnectionPoint(Node):
    _local_name = 'ConnectionPoint'
    label = "ConnectionPoint"
class Inlet(ConnectionPoint):
    _local_name = 'InletConnectionPoint'
    label = "Inlet"

class Outlet(ConnectionPoint):
    _local_name = 'OutletConnectionPoint'
    label = "Outlet"
