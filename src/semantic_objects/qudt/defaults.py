from ..core import semantic_object
from .quantitykinds import * 
from .units import *

# IP or SI
DEFAULT_UNIT_SYSTEM = 'SI'

#DEFAULT IP: SI units 
DEFAULT_UNIT_MAP = {
    Area:{
        "SI": M2,
        "IP": FT2
    },
    Azimuth:{
        "SI": Degree,
        "IP": Degree
    },
    Tilt:{
        "SI": Degree,
        "IP": Degree
    },
    Power:{
        "SI": KiloW,
        "IP": BTU_IT_PER_HR
    },
    Pressure:{
        "SI": PA,
        "IP": PSI
    },
}