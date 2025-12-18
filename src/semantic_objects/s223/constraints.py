from .entities import *
from .relations import *
from .core import * 
from ..qudt import QuantityKind, Unit

# describing valid relations 
Node._valid_relations = [
    (hasProperty, QuantifiableObervableProperty),
]
DomainSpace._valid_relations = [
    (contains, PhysicalSpace),
    (encloses, DomainSpace),
]

QuantifiableObervableProperty._valid_relations = [
    (hasAspect, EnumerationKind),
    (hasValue, ExternalReference),
    (hasValue, Literal),
    (hasValue, float),
    (hasUnit, Unit),
    (hasQuantityKind, QuantityKind),
]