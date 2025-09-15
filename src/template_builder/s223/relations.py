from .. import core
from semantic_mpc_interface import S223, QUDT

# Sinse Predicate has no node type, it will be like the "any predicate" for a template
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
