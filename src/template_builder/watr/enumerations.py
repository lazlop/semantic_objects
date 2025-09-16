from .. import core 
from typing import List, Dict, Tuple, Type, Union,get_origin
from dataclasses import dataclass, field
from ..namespaces import S223, SH, A, WATR, RDFS
from .relations import hasProcess
from .core import Node
from ..core import valid_field, required_field, optional_field

#TODO: model these enumerations correctly 
class Fluid(Node):
    _local_name = 'Mix-Fluid'
    label = 'Mix-Fluid'