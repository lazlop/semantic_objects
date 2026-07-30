"""Field-declaration helpers for generated CXF Block classes.

Each helper returns a dataclasses.field() whose default_factory builds the
right Port/Parameter value object (see core.py) for that field, with
metadata={'relation': None, ...} so semantic_object's RDF-relation inference
(core.py's get_relations()/_infer_relation_for_field) skips these fields
outright - a CXF port isn't part of the s223 RDF relation graph, so there is
no relation to infer.
"""
from dataclasses import field
from typing import Optional

from ..qudt import QuantityKind, Unit
from .core import (
    BooleanInputPort, BooleanOutputPort, BooleanParameter, EnumParameter,
    IntegerInputPort, IntegerOutputPort, IntegerParameter, Parameter,
    RealInputPort, RealOutputPort, RealParameter, SubBlock,
)


def real_input_field(qk: Optional[QuantityKind] = None, unit: Optional[Unit] = None,
                      description: Optional[str] = None):
    return field(
        default_factory=lambda: RealInputPort(qk=qk, unit=unit, description=description),
        metadata={'relation': None, 'kind': 'input'},
    )


def real_output_field(qk: Optional[QuantityKind] = None, unit: Optional[Unit] = None,
                       description: Optional[str] = None):
    return field(
        default_factory=lambda: RealOutputPort(qk=qk, unit=unit, description=description),
        metadata={'relation': None, 'kind': 'output'},
    )


def boolean_input_field(description: Optional[str] = None):
    return field(
        default_factory=lambda: BooleanInputPort(description=description),
        metadata={'relation': None, 'kind': 'input'},
    )


def boolean_output_field(description: Optional[str] = None):
    return field(
        default_factory=lambda: BooleanOutputPort(description=description),
        metadata={'relation': None, 'kind': 'output'},
    )


def integer_input_field(description: Optional[str] = None):
    return field(
        default_factory=lambda: IntegerInputPort(description=description),
        metadata={'relation': None, 'kind': 'input'},
    )


def integer_output_field(description: Optional[str] = None):
    return field(
        default_factory=lambda: IntegerOutputPort(description=description),
        metadata={'relation': None, 'kind': 'output'},
    )


def real_parameter_field(default: Optional[float] = None, qk: Optional[QuantityKind] = None,
                          unit: Optional[Unit] = None, description: Optional[str] = None):
    return field(
        default_factory=lambda: RealParameter(qk=qk, unit=unit, value=default, description=description),
        metadata={'relation': None, 'kind': 'parameter'},
    )


def boolean_parameter_field(default: Optional[bool] = None, description: Optional[str] = None):
    return field(
        default_factory=lambda: BooleanParameter(value=default, description=description),
        metadata={'relation': None, 'kind': 'parameter'},
    )


def integer_parameter_field(default: Optional[int] = None, description: Optional[str] = None):
    return field(
        default_factory=lambda: IntegerParameter(value=default, description=description),
        metadata={'relation': None, 'kind': 'parameter'},
    )


def enum_parameter_field(enumeration_kind: Optional[type] = None, default: Optional[type] = None,
                          description: Optional[str] = None):
    return field(
        default_factory=lambda: EnumParameter(enumeration_kind=enumeration_kind, value=default,
                                               description=description),
        metadata={'relation': None, 'kind': 'parameter'},
    )


def unknown_parameter_field(default=None, description: Optional[str] = None):
    """For the handful of parameters whose datatype can't be recovered from
    the source data at all (see Parameter's docstring in core.py)."""
    return field(
        default_factory=lambda: Parameter(value=default, description=description),
        metadata={'relation': None, 'kind': 'parameter'},
    )


def subblock_field(block_type: Optional[type] = None, description: Optional[str] = None):
    return field(
        default_factory=lambda: SubBlock(block_type=block_type, description=description),
        metadata={'relation': None, 'kind': 'subblock'},
    )
