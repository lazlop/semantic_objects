from ..core import semantic_object, Predicate as corePredicate
from semantic_mpc_interface import S223, QUDT

# NOTE: not totally happy with declaring domains and ranges this way. Probably better to do it in the entities. I think this is ok for now. 
# Advantage of doing it here: makes entities less of a mixture between object and graph. 
# Disadvantage: Using Strings to specify domains and ranges, rather than classes. Registry concept probbaly not as good as just declaring the valid relatoins in the entities

# TODO: move qudt predicate
@semantic_object
class hasQuantityKind(corePredicate):
    _ns = QUDT
    _type = 'hasQuantityKind'
@semantic_object
class Predicate(corePredicate):
    _ns = S223
@semantic_object
class hasValue(Predicate):
    # can validate predicates against classes optionally 
    _type = 'hasValue'
@semantic_object
class hasUnit(Predicate):
    _type = 'hasUnit'
@semantic_object
class hasProperty(Predicate):
    _type = 'hasProperty'
@semantic_object
class contains(Predicate):
    _type = 'contains'
@semantic_object
class encloses(Predicate):
    _type = 'encloses'
@semantic_object
class hasConnectionPoint(Predicate):
    _type = 'hasConnectionPoint'
@semantic_object
class hasMedium(Predicate):
    _type = 'hasMedium'
@semantic_object
class connectedTo(Predicate):
    _type = 'connectedTo'
    label = "connected to"
    comment = "Indicates that two entities are connected in some way."
@semantic_object
class hasWindow(Predicate):
    _type = 'hasWindow'
    label = "has window"
    comment = "Indicates that a DomainSpace has a Window. This is a subproperty of connectedTo."
    _subproperty_of = connectedTo
    # Domain and range will be set dynamically to avoid circular imports
@semantic_object
class hasExternalReference(Predicate):
    _type = 'hasExternalReference'