from ..core import * 
from .core import Node
from .. import units
from .values import Area, Azimuth, Tilt
from .relations import * 

# Should node_uris be generated based on var names? should that or label be required or optionally provided? 

class DomainSpace(Node):
    _iri = 'DomainSpace'
    label = "Domain Space"
class PhysicalSpace(Node):
    _iri = 'PhysicalSpace'
    label = "Physical Space"
    comment = "A `PhysicalSpace` is an architectural concept representing a room, a part of a room, a collection of rooms, or any other physical region in a building. PhysicalSpaces may be grouped to define larger `PhysicalSpace`s using the relation `contains` (see {s223:contains})."
    # Missing a comment for the possible relations. May want to use pydantic with fields or something
    possible_relations = [
            (contains, __qualname__)
            # not correct, just for testing
            (encloses, DomainSpace)
        ]
class Space(PhysicalSpace):
    area: Area
    relations = [
        (hasProperty, 'area')
        ]
    # TODO: consider smoothing this and just requiring params for area instead of actually requiring Area, or make generic by requiring kwargs for all annotations
    def __init__(self, area: Area):
        self.area = area


# just for testing out what this looks like
class Space_OptArea(Space):
    area: Area
    relations = [
        (hasProperty, 'area')
        ]
    _optional = ['area']
    
class Space_TwoArea(Space):
    area: Area
    area2: Area

    relations = [
            (hasProperty, ['area','area2'])
        ]