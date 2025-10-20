from .. import core
from ..s223.relations import hasValue, hasConnectionPoint, hasMedium
from ..namespaces import WATR,S223, QUDT

# Sinse Predicate has no node type, it will be like the "any predicate" for a template
class Predicate(core.Predicate):
    _ns = WATR

class hasProcess(Predicate):
    _local_name = 'hasProcess'
    _applies_to = [
        ('UnitProcess', 'Process'),
    ]
