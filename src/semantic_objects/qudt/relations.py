from ..core import semantic_object, Predicate as corePredicate
from semantic_mpc_interface import QUDT

@semantic_object
class hasQuantityKind(corePredicate):
    _ns = QUDT
    _type = 'hasQuantityKind'