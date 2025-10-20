from .. import core 
from typing import List, Dict, Tuple, Type, Union,get_origin
from dataclasses import dataclass, field
from ..namespaces import S223, SH, A, WATR, RDFS
from .relations import hasProcess
from ..core import required_field, optional_field
from ..s223 import relations as s223_relations
from . import relations

# Build DEFAULT_RELATIONS from relation class metadata
# This includes both watr-specific relations and s223 relations used by watr
DEFAULT_RELATIONS = {}
DEFAULT_RELATIONS.update(core.build_relations_registry(s223_relations))
DEFAULT_RELATIONS.update(core.build_relations_registry(relations))


# TODO: Consider how we want rdfs:subClassOf to work (use python inheritance for subclass?), 

# Note: Not focused on this level of the ontology, is there a point in modeling it at all? 
@dataclass
class Class(core.Node):
    _ns = WATR
    # declaring predicate_objects
    _type = RDFS.Class
    _other_types = [SH.NodeShape]
    _predicate_objects = [
        (RDFS.subClassOf, RDFS.Class)
    ]

@dataclass
class Node(core.Node):
    _ns = WATR
    # declaring predicate_objects
    _type = WATR.Class
    _other_types = [SH.NodeShape]

@dataclass
class Equipment(core.Node):
    _local_name = 'Equipment'
    _ns = S223
    _type = S223.Class
    _other_types = [SH.NodeShape]

# TODO: correct this to be enumerationkind
@dataclass
class Process(Class):
    _ns = WATR
    _type = WATR.Class
    label = 'Process'

@dataclass
class UnitProcess(Class):
    _ns = WATR
    _type = WATR.Class
    label = 'Unit process'
    # TODO: Decide if it makes sense to allow arbitrary triples, and if these triples should be inherited
    _class_triples = [
        (RDFS.subClassOf, [RDFS.Class, S223.Equipment])
    ]
    _instance_triples = [
        (RDFS.subClassOf, [RDFS.Class, S223.Equipment])
    ]
    process: Process = required_field(hasProcess, min = 1, qualified = False,
                comment = 'a Unit Process must be associated with a water treatment process')
