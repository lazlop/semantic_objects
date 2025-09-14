from ..core import * 
from .core import Node
from .. import units
from .values import Area, Azimuth, Tilt
from .relations import * 
from typing import Optional, Self
from dataclasses import dataclass, field
# Should node_uris be generated based on var names? should that or label be required or optionally provided?

class DomainSpace(Node):
    _iri = 'DomainSpace'
    label = "Domain Space"

@dataclass
class PhysicalSpace(Node):
    _iri = 'PhysicalSpace'
    label = "Physical Space"
    comment = "A `PhysicalSpace` is an architectural concept representing a room, a part of a room, a collection of rooms, or any other physical region in a building. PhysicalSpaces may be grouped to define larger `PhysicalSpace`s using the relation `contains` (see {s223:contains})."
    # should really be List[Self], since could be multiple
    contains: Optional[Self] = field(
        default=None, 
        init=False, 
        metadata={'relation': contains,'templatize': False}
        )
    
    encloses: Optional[DomainSpace] = field(
        default=None, 
        init=False, 
        metadata={'relation': encloses, 'templatize': False}
        )

@dataclass
class Space(PhysicalSpace):
    area: Area = field(metadata={'relation': hasProperty})

    
@dataclass
class Space_TwoArea(Space):
    area: Area = field(metadata={'relation': hasProperty})
    area2: Area = field(metadata={'relation': hasProperty})
    

@dataclass
class SpaceOptArea(PhysicalSpace):
    """Space with optional area using field metadata"""
    # INIT false means optional 
    area: Area = field(init = False, metadata={'relation': hasProperty})

@dataclass
class Window(Node):
    """Window with multiple properties using field-based relations"""
    _iri = 'Window'
    area: Area = field(metadata={'relation': hasProperty})
    azimuth: Azimuth = field(metadata={'relation': hasProperty})
    tilt: Tilt = field(metadata={'relation': hasProperty})