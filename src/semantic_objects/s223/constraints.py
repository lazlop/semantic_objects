from .entities import *
from .relations import *

# describing valid relations 
DomainSpace._valid_relations = [
    (hasProperty, QuantifiableObervableProperty),
    (contains, PhysicalSpace),
    (encloses, DomainSpace),
]

