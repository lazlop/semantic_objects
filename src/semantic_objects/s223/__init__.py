from .core import *
from .entities import * 
from .values import * 
from .relations import * 

def get_all_classes():
    from .. import core 
    from . import entities, values, relations
    return core.get_all_classes([entities, relations, values])