from ..core import * 
from .core import Equipment
from .enumerations import Fluid
from .. import units
from .relations import *
from typing import Optional, Self
from dataclasses import dataclass, field
from ..namespaces import WATR, A
from rdflib import URIRef
from ..s223.relations import hasMedium, hasConnectionPoint
from ..s223.entities import Inlet, Outlet

class FluidInlet(Inlet):
    medium: Fluid = required_field(hasMedium)

class FluidOutlet(Outlet):
    medium: Fluid = required_field(hasMedium)


@dataclass
class Tank(Equipment):
    _local_name = 'Tank'
    label: str = triple_field(RDFS.label, 'Tank')
    comment: str = triple_field(RDFS.comment, "A tank for storing water") 
    inlet: FluidInlet = required_field(hasConnectionPoint)
    outlet: FluidOutlet = required_field(hasConnectionPoint)
    temperature: WaterTemperature = required_field(hasProperty)
    tank_volume: Volume = required_field(hasProperty)





@dataclass
class MyCoolAnaerobicPFR(Tank):
    _local_name = 'MyCoolAnerobicPFR'
    # These would show up in a template like p:name a watr:PlugFlowReactor, water:AnaerobicDigester.
    types: URIRef = triple_field(A, [WATR.PlugFlowReactor, WATR.AnaerobicDigester])
    # _instance_triples = [
    #     (A, [WATR.PlugFlowReactor, WATR.AnaerobicDigester])
    # ]

