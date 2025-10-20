from .. import core 
from typing import List, Dict, Tuple, Type, Union,get_origin
from dataclasses import dataclass, field
from semantic_mpc_interface.namespaces import S223, SH, A
from . import relations

# Default relation mappings for s223 ontology
# Maps (source_class_name, target_class_name) -> relation
DEFAULT_RELATIONS = {
    # Node -> QuantifiableObervableProperty uses hasProperty (note: typo in class name)
    ('Node', 'QuantifiableObervableProperty'): relations.hasProperty,
    # PhysicalSpace -> PhysicalSpace uses contains
    ('PhysicalSpace', 'PhysicalSpace'): relations.contains,
    # PhysicalSpace -> DomainSpace uses encloses
    ('PhysicalSpace', 'DomainSpace'): relations.encloses,
    # Node -> ConnectionPoint types use hasConnectionPoint
    ('Node', 'ConnectionPoint'): relations.hasConnectionPoint,
}

@dataclass
class Node(core.Node):
    _ns = S223
    _type = S223.Class
    _other_types = [SH.NodeShape]

    # TODO: may want to replace dataclass repr using this or field-based method
    # def __repr__(self):
    #     # attr_strs = [f"{attr}={getattr(self, attr, None)}" for attr in attributes.keys() if attr != 'name']
    #     # counts = []
    #     # for entity_type in contained_types:
    #     #     attr_name = f"{entity_type}s"
    #     #     count = len(getattr(self, attr_name, []))
    #     #     counts.append(f"{entity_type}s={count}")

    #     # return f"{class_name}(name='{self.name}', {', '.join(attr_strs)}, {', '.join(counts)})"
    #     attrs = self._get_attributes()
    #     return f"{self.__class__.__name__}, {self.__dict__}"
