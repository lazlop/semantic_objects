from .core import NamedNode
from semantic_mpc_interface.namespaces import UNIT

# TODO: maybe just change to requiring a URIRef in the UNIT namespace
class Unit(NamedNode):
    _ns = UNIT

class FT_2(Unit):
    _name = "FT_2"