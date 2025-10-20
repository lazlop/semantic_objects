from ..core import * 
from .core import Equipment
from .enumerations import Fluid
from .. import units
from .relations import *
from typing import Optional, Self
from dataclasses import dataclass, field
from ..namespaces import WATR, A
from ..s223.relations import hasMedium, hasConnectionPoint
from ..s223.entities import Inlet, Outlet

class FluidInlet(Inlet):
    medium: Fluid = required_field(hasMedium)

class FluidOutlet(Outlet):
    medium: Fluid = required_field(hasMedium)

@dataclass
class Tank(Equipment):
    _local_name = 'Tank'
    label = "Tank"
    comment = "A tank for storing liquid"
    # should probably actually be optional[list[self]], since multiple spaces can be contained, but I want to minimize typing if possible
    inlet: FluidInlet = required_field()
    outlet: FluidOutlet = required_field()


@dataclass
class MyCoolAnaerobicPFR(Tank):
    _local_name = 'MyCoolAnerobicPFR'
    # These would show up in a template like p:name a watr:PlugFlowReactor, water:AnaerobicDigester.
    A = [WATR.PlugFlowReactor, WATR.AnaerobicDigester]
    # _instance_triples = [
    #     (A, [WATR.PlugFlowReactor, WATR.AnaerobicDigester])
    # ]

