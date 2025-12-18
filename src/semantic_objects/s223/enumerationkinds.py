from ..core import NamedNode, semantic_object
# TODO move enumerationkind
# TODO seems like I can actually remove NamedNode
from .core import EnumerationKind

@semantic_object
class Aspect(EnumerationKind):
    _name = 'EnumerationKind-Aspect'

@semantic_object
class Setpoint(Aspect):
    _name = 'Aspect-Setpoint'

@semantic_object
class Deadband(Aspect):
    _name = 'Aspect-Deadband'

@semantic_object
class Deadband(Aspect):
    _name = 'Aspect-Threshold'

@semantic_object
class Domain(EnumerationKind):
    _name = 'EnumerationKind-Domain'

@semantic_object
class Occupancy(Domain):
    _name = 'Domain-Occupancy'