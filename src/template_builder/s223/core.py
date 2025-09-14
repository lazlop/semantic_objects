from .. import core 
from typing import List, Dict, Tuple, Type, Union,get_origin
from dataclasses import dataclass, field
from semantic_mpc_interface.namespaces import * 
from . import relations

@dataclass
class Node(core.Node):
    _ns = S223
    definition = [
        (A, [SH.NodeShape, S223.Class]),
    ]
    # TODO: Fix for production, helpful debugging repr for now
    def __repr__(self):
        # attr_strs = [f"{attr}={getattr(self, attr, None)}" for attr in attributes.keys() if attr != 'name']
        # counts = []
        # for entity_type in contained_types:
        #     attr_name = f"{entity_type}s"
        #     count = len(getattr(self, attr_name, []))
        #     counts.append(f"{entity_type}s={count}")

        # return f"{class_name}(name='{self.name}', {', '.join(attr_strs)}, {', '.join(counts)})"
        attrs = self._get_attributes()
        return f"{self.__class__.__name__}, {self.__dict__}"
