from . import properties
from .entities import *
from .properties import *
from .relations import *

def get_module_classes():
    from .. import core
    from . import entities, relations
    return core.get_module_classes([entities, relations, properties])
