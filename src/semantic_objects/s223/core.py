from .. import core 
from typing import List, Dict, Tuple, Type, Union,get_origin
from dataclasses import dataclass, field
from semantic_mpc_interface.namespaces import S223, SH, A
from . import relations

@dataclass
class Node(core.Node):
    _ns = S223
    _type = S223.Class
    _other_types = [SH.NodeShape]
