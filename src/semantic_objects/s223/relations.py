from .. import core
from semantic_mpc_interface import S223, QUDT

# NOTE: not totally happy with declaring domains and ranges this way. Probably better to do it in the entities. I think this is ok for now. 
# Advantage of doing it here: makes entities less of a mixture between object and graph. 
# Disadvantage: Using Strings to specify domains and ranges, rather than classes. Registry concept probbaly not as good as just declaring the valid relatoins in the entities
class Predicate(core.Predicate):
    _ns = S223

class hasValue(Predicate):
    # can validate predicates against classes optionally 
    _local_name = 'hasValue'

class hasUnit(Predicate):
    _local_name = 'hasUnit'

class hasProperty(Predicate):
    _local_name = 'hasProperty'

class contains(Predicate):
    _local_name = 'contains'

class encloses(Predicate):
    _local_name = 'encloses'

class hasQuantityKind(core.Predicate):
    _ns = QUDT
    _local_name = 'hasQuantityKind'

class hasConnectionPoint(Predicate):
    _local_name = 'hasConnectionPoint'

class hasMedium(Predicate):
    _local_name = 'hasMedium'

class connectedTo(Predicate):
    _local_name = 'connectedTo'
    label = "connected to"
    comment = "Indicates that two entities are connected in some way."

class hasWindow(Predicate):
    _local_name = 'hasWindow'
    label = "has window"
    comment = "Indicates that a DomainSpace has a Window. This is a subproperty of connectedTo."
    _subproperty_of = connectedTo
    # Domain and range will be set dynamically to avoid circular imports
