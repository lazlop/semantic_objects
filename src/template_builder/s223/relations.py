from .. import core
from semantic_mpc_interface import S223


# Sinse Predicate has no node type, it will be like the "any predicate" for a template
class Predicate(core.Predicate):
    _ns = S223

class hasValue(Predicate):
    # can validate predicates against classes optionally 
    _iri = 'hasValue'

class hasUnit(Predicate):
    _iri = 'hasUnit'

class hasProperty(Predicate):
    _iri = 'hasProperty'

class hasQuantityKind(Predicate):
    _iri = 'hasQuantityKind'