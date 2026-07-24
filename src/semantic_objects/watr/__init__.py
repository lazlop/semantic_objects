from . import properties
from .core import *
from .entities import * 
from .properties import * 
from .relations import *
from .constraints import *

def get_module_classes():
    from .. import core 
    from . import entities, relations
    return core.get_module_classes([entities, relations, properties])
