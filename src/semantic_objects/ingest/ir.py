from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class ComplexConstraintIR:
    """A SHACL constraint that can't be represented as a single typed field."""
    path_local: Optional[str]
    kind: str  # 'sparql' | 'or' | 'nested-node' | 'inverse-path' | 'forbidden' | 'other'
    comment: Optional[str]
    message: Optional[str]
    severity: Optional[str]
    raw_turtle: str


@dataclass
class PropertyShapeIR:
    """A SHACL property shape that maps to one required_field()/optional_field()."""
    path_local: str
    field_name: str
    target_class_local: Optional[str]
    datatype_local: Optional[str]
    min_count: Optional[int]
    max_count: Optional[int]
    qualified: bool
    comment: Optional[str]
    message: Optional[str]
    supplementary_notes: List[ComplexConstraintIR] = field(default_factory=list)


@dataclass
class ClassIR:
    iri: str
    local_name: str
    class_name: str
    label: Optional[str]
    comment: Optional[str]
    parent_local_names: List[str]
    is_abstract: bool
    is_enumeration_value: bool
    bucket: str  # 'entities' | 'properties' | 'enumerationkinds'
    property_shapes: List[PropertyShapeIR] = field(default_factory=list)
    complex_constraints: List[ComplexConstraintIR] = field(default_factory=list)


@dataclass
class RelationIR:
    iri: str
    local_name: str
    class_name: str
    label: Optional[str]
    comment: Optional[str]
    kind: str  # 'Relation' | 'RelationWithInverse' | 'SymmetricRelation'
    inverse_of_local: Optional[str]


@dataclass
class OntologyIR:
    classes: Dict[str, ClassIR] = field(default_factory=dict)      # keyed by local_name
    relations: Dict[str, RelationIR] = field(default_factory=dict)  # keyed by local_name
    quantitykinds_referenced: Set[str] = field(default_factory=set)
    source_meta: dict = field(default_factory=dict)
