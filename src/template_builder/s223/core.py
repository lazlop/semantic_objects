from .. import core 
from typing import List, Dict, Tuple, Type, Union,get_origin
from dataclasses import dataclass, field
from semantic_mpc_interface.namespaces import * 
from . import relations

@dataclass
class Node(core.Node):
    _ns = S223
    relations = []
