from .entities import *
from .relations import *
from .core import * 

# describing valid relations 
Node._valid_relations = [
    (hasProperty, QuantifiableObervableProperty),
]
DomainSpace._valid_relations = [
    (contains, PhysicalSpace),
    (encloses, DomainSpace),
]

QuantifiableObervableProperty._valid_relations = [
    (hasAspect, EnumerationKind)
]