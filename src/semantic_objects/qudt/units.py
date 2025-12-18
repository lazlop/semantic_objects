from ..core import NamedNode, semantic_object
from ..namespaces import UNIT

@semantic_object
class Unit(NamedNode):
    _name = 'Unit'
    _ns = UNIT

@semantic_object
class M2(Unit):
    _name = 'M2'

@semantic_object
class FT2(Unit):
    _name = 'FT2'

@semantic_object
class Degree(Unit):
    _name = 'Degree'

@semantic_object
class KiloW(Unit):
    _name = 'KiloW'

@semantic_object
class BTU_IT_PER_HR(Unit):
    _name = 'BTU_IT-PER-HR'

@semantic_object
class PSI(Unit):
    _name = 'PSI'

@semantic_object
class PA(Unit):
    _name = 'PA'