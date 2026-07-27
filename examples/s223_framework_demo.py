"""Framework-mechanics demo classes - not derived from the real s223 ontology.

These classes exist to exercise framework mechanics (required_field/__post_init__
coercion, inter_field_relation, exact_values) with simple, self-contained shapes.
They are NOT ontology-accurate: the real, ontology-generated classes with these
names (Space, Window, Pump, ...) live in semantic_objects.s223 and have different
fields, since they're derived from the actual vendored s223 SHACL shapes - see
semantic_objects.s223._generated. Use those for real modeling; use these only to
see how the framework's field/relation mechanics work.
"""
from semantic_objects.core import Predicate, semantic_object
from semantic_objects.fields import required_field, inter_field_relation
from semantic_objects.namespaces import S223
from semantic_objects.s223.core import Node as _S223Node
from semantic_objects.s223.properties import Area, Azimuth, Tilt
from semantic_objects.s223.relations import connectedTo, hasDomainSpace, hasProperty


@semantic_object
class DemoPredicate(Predicate):
    _ns = S223


@semantic_object
class hasWindow(DemoPredicate):
    label = "has window"
    comment = "Indicates that a DomainSpace has a Window. Subproperty of connectedTo."
    _subproperty_of = connectedTo


@semantic_object
class Connectable(_S223Node):
    label = "Connectable"
    abstract = True


@semantic_object
class DomainSpace(Connectable):
    label = "Domain Space"


@semantic_object
class Space(DomainSpace):
    area: Area = required_field(relation=hasProperty)

    def __post_init__(self):
        """Convert raw values to proper types"""
        super().__post_init__()
        if not isinstance(self.area, Area):
            self.area = Area(self.area)


@semantic_object
class Space_TwoArea(Space):
    """Space with two area fields for testing hierarchy"""
    area2: Area = required_field(relation=hasProperty)


@semantic_object
class Window(_S223Node):
    """Window with multiple properties using field-based relations"""
    area: Area = required_field(relation=hasProperty)
    azimuth: Azimuth = required_field(relation=hasProperty)
    tilt: Tilt = required_field(relation=hasProperty)


@semantic_object
class SpaceWithWindow(Space):
    """Example of a Space with a Window using inter-field relations"""
    space: Space = required_field(relation=hasDomainSpace)
    window: Window = required_field(relation=hasWindow)

    _inter_field_relations = [
        inter_field_relation(
            source_field='space',
            relation=connectedTo,
            target_field='window',
            min=1,
            max=1
        )
    ]


@semantic_object
class SpaceWithWindowNoMainRelation(Space):
    """Example where window has no relation to main entity, only space->window relation"""
    space: Space = required_field(relation=hasDomainSpace)
    window: Window = required_field(relation=None)  # No relation from main entity to window

    _inter_field_relations = [
        inter_field_relation(
            source_field='space',
            relation=connectedTo,
            target_field='window',
            min=1,
            max=1
        )
    ]
