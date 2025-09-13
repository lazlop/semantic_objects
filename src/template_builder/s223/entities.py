from ..core import * 
from .core import Node
from .. import units
from .values import Area, Azimuth, Tilt
from .relations import * 

# Should node_uris be generated based on var names? should that or label be required or optionally provided? 

class Space(Node):
    _iri = 'PhysicalSpace'
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