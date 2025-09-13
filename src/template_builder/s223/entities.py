from ..core import * 
from .core import Node
from .. import units
from .values import Area, Azimuth, Tilt
from .relations import * 

class Space(Node):
    _iri = 'PhysicalSpace'
    area: Area
    relations = [
        (hasProperty, 'area')
        ]
class Space_OptArea(Space):
    _optional = ['area']
    
class Space_TwoArea(Space):
    area: Area
    area2: Area

    relations = [
            (hasProperty, ['area','area2'])
        ]
    
class Window(Node):
    _iri = 'Window'
    area: Area
    azimuth: Azimuth
    tilt: Tilt 

    relations = [
        (hasProperty, ['area','azimuth','tilt'])
    ]
