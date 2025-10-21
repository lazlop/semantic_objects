from .. import core 
from typing import List, Dict, Tuple, Type, Union,get_origin
from dataclasses import dataclass, field
from semantic_mpc_interface.namespaces import S223, SH, A
from . import relations

# Build DEFAULT_RELATIONS from relation class metadata
DEFAULT_RELATIONS = core.build_relations_registry(relations)

@dataclass
class Node(core.Node):
    _ns = S223
    _type = S223.Class
    _other_types = [SH.NodeShape]
