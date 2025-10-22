from .. import core
from semantic_mpc_interface import S223, QUDT

# NOTE: not totally happy with declaring domains and ranges this way. Probably better to do it in the entities. I think this is ok for now. 
# Advantage of doing it here: makes entities less of a mixture between object and graph. 
# Disadvantage: Using Strings to specify domains and ranges, rather than classes. Registry concept probbaly not as good as just declaring the valid relatoins in the entities
class Predicate(core.Predicate):
    _ns = S223

class hasValue(Predicate):
    # can validate predicates against classes optionally 
    _type = 'hasValue'

class hasUnit(Predicate):
    _type = 'hasUnit'

class hasProperty(Predicate):
    _type = 'hasProperty'

class contains(Predicate):
    _type = 'contains'

class encloses(Predicate):
    _type = 'encloses'

class hasQuantityKind(core.Predicate):
    _ns = QUDT
    _type = 'hasQuantityKind'

class hasConnectionPoint(Predicate):
    _type = 'hasConnectionPoint'

class hasMedium(Predicate):
    _type = 'hasMedium'

class connectedTo(Predicate):
    _type = 'connectedTo'
    label = "connected to"
    comment = "Indicates that two entities are connected in some way."

class hasWindow(Predicate):
    _type = 'hasWindow'
    label = "has window"
    comment = "Indicates that a DomainSpace has a Window. This is a subproperty of connectedTo."
    _subproperty_of = connectedTo
    # Domain and range will be set dynamically to avoid circular imports
