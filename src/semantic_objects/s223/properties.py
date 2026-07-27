"""Hand-written overrides on top of the ontology-generated properties.

See _generated/properties.py (regenerated via
`python -m semantic_objects.ingest.cli --ontology s223`) for the Property/
ObservableProperty/QuantifiableProperty/QuantifiableObservableProperty/
EnumerableProperty hierarchy derived from the vendored ontology's SHACL shapes.

qk/value/unit aren't derivable from generation: the ontology models them via
qudt:hasQuantityKind/qudt:hasUnit/s223:hasValue, which live in the QUDT namespace
this pilot doesn't ingest (see docs/exact_values_generalization.md and the ingestion
plan). This module extends the generated QuantifiableObservableProperty with them,
plus the concrete QUDT-quantity-kind leaf classes used for real modeling.
"""
from typing import Optional

from dataclasses import field

from ..core import *
from ..units import *
from ..qudt import quantitykinds, QuantityKind, units, DEFAULT_UNIT_SYSTEM, DEFAULT_UNIT_MAP
from ._generated.properties import *
from ._generated.properties import QuantifiableObservableProperty as _GeneratedQOP
from .enumerationkinds import Setpoint, Threshold, Occupancy
from .relations import hasAspect, hasValue, Predicate as _S223Predicate


@semantic_object
class hasQuantityKind(_S223Predicate):
    """Historical S223-namespaced stand-in for qudt:hasQuantityKind, which this
    pilot doesn't ingest (out of the s223 namespace it walks)."""
    pass


@semantic_object
class hasUnit(_S223Predicate):
    """Historical S223-namespaced stand-in for qudt:hasUnit, same reason as above."""
    pass


@semantic_object
class QuantifiableObservableProperty(_GeneratedQOP):
    qk: quantitykinds.QuantityKind = required_field(relation=hasQuantityKind, qualified=False)
    value: float = required_field(relation=hasValue)
    unit: Optional[Unit] = field(default=None, metadata={'relation': hasUnit, 'min': 1, 'max': None, 'qualified': True})

    def __post_init__(self):
        """Set default unit if not provided"""
        super().__post_init__()
        if self.unit is None:
            self.unit = DEFAULT_UNIT_MAP[self.qk][DEFAULT_UNIT_SYSTEM]


@semantic_object
class Area(QuantifiableObservableProperty):
    qk = quantitykinds.Area
    _semantic_type = QuantifiableObservableProperty


@semantic_object
class Azimuth(QuantifiableObservableProperty):
    qk = quantitykinds.Azimuth
    _semantic_type = QuantifiableObservableProperty


@semantic_object
class Tilt(QuantifiableObservableProperty):
    qk = quantitykinds.Tilt
    _semantic_type = QuantifiableObservableProperty


@semantic_object
class Area_FT2(Area):
    unit = units.FT2
    _semantic_type = QuantifiableObservableProperty


@semantic_object
class Area_SP(Area):
    _semantic_type = QuantifiableObservableProperty
    aspects: Optional[list] = field(
        default=None,
        init=False,
        metadata={
            'relation': hasAspect,
            'exact_values': [Setpoint, Threshold, Occupancy],
            'qualified': False
        }
    )


@semantic_object
class Power(QuantifiableObservableProperty):
    qk = quantitykinds.Power
    _semantic_type = QuantifiableObservableProperty
