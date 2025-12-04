from .entities import *
from .relations import *

# describing valid relations 
Node._valid_relations = [
    (hasProperty, QuantifiableObervableProperty),
]
DomainSpace._valid_relations = [
    (contains, PhysicalSpace),
    (encloses, DomainSpace),
]

