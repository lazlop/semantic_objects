"""
Test that Resource/Node can be hand-subclassed directly, with no ontology
package (s223/watr/cxf) involved.

Regression tests for two bugs found while prototyping hand-authored
templates:

1. RdfExporter.generate_rdf_class_definition() reads cls._other_types
   unconditionally, but only ontology packages set it on their own shared
   base (s223/core.py, watr/core.py) - a bare Resource/Node subclass had no
   default and raised AttributeError. Resource now defaults _other_types
   to [].

2. required_field()/optional_field()/exclusive_field() always wrote a
   'relation' key into field metadata, even when the caller didn't pass one
   (defaulting to None) - and core.py/exporters.py treat a present-but-None
   'relation' key as "explicitly no relation", not "please infer". That
   meant relation inference from _valid_relations was unreachable through
   these constructors. Fixed via an explicit infer_relation=True flag rather
   than making inference the default for omitted relation=, because
   relation=None is *also* a real, intentional state (see
   examples/s223_framework_demo.py's SpaceWithWindowNoMainRelation: a field
   reachable only via an inter-field relation must not also get a direct
   relation from the main entity) - so it can't be reinterpreted as
   "infer" without breaking that case.
"""
import pytest
from rdflib import Namespace

from semantic_objects.core import Node, Predicate, Resource, semantic_object
from semantic_objects.fields import required_field

NS = Namespace("urn:test-bare-resource#")


@semantic_object
class hasPoint(Predicate):
    _ns = NS


@semantic_object
class BareNode(Node):
    _ns = NS
    abstract = True


# Relation inference for the whole family, declared once (mirrors
# _valid_relations on the ontology-generated classes) - fields below just
# need infer_relation=True instead of relation=hasPoint spelled out per field.
BareNode._valid_relations = [(hasPoint, BareNode)]


@semantic_object
class Deadband(BareNode):
    pass


@semantic_object
class Thermostat(BareNode):
    deadband: Deadband = required_field(infer_relation=True)


@semantic_object
class StagedThermostat(Thermostat):
    stage_count: Deadband = required_field(infer_relation=True)


def test_bare_resource_has_default_other_types():
    assert Resource._other_types == []


def test_generate_rdf_class_definition_on_bare_subclass():
    # Previously raised AttributeError: 'Thermostat' object has no attribute '_other_types'
    shacl = Thermostat.generate_rdf_class_definition()
    assert 'NodeShape' in shacl


def test_inheritance_extends_fields_without_a_template_dsl():
    base_fields = set(Thermostat.__dataclass_fields__)
    staged_fields = set(StagedThermostat.__dataclass_fields__)
    assert base_fields < staged_fields
    assert staged_fields - base_fields == {'stage_count'}


def test_to_yaml_reflects_inherited_and_added_fields():
    base_yaml = Thermostat.to_yaml()
    staged_yaml = StagedThermostat.to_yaml()
    assert 'deadband' in base_yaml
    assert 'deadband' in staged_yaml
    assert 'stage_count' not in base_yaml
    assert 'stage_count' in staged_yaml


def test_relation_inferred_with_infer_relation_true():
    relation_by_field = {field_name: relation for relation, field_name in StagedThermostat.get_relations()}
    assert relation_by_field['deadband'] is hasPoint
    assert relation_by_field['stage_count'] is hasPoint


def test_relation_none_by_default_means_no_relation_not_inference():
    # relation=None (the default, with infer_relation left False) must keep
    # meaning "no relation", not silently start inferring one - this is what
    # SpaceWithWindowNoMainRelation in examples/s223_framework_demo.py relies
    # on for a field that's only reachable via an inter-field relation.
    @semantic_object
    class NoRelationField(BareNode):
        deadband: Deadband = required_field(relation=None)

    relations = dict((field_name, relation) for relation, field_name in NoRelationField.get_relations())
    assert 'deadband' not in relations


def test_infer_relation_true_without_a_matching_valid_relations_entry_raises():
    @semantic_object
    class NoNamespace(Node):
        abstract = True

    @semantic_object
    class Orphan(NoNamespace):
        pass

    @semantic_object
    class Unmatched(NoNamespace):
        # No _valid_relations anywhere in NoNamespace/Unmatched's MRO that
        # mentions Orphan - inference has nothing to find.
        orphan: Orphan = required_field(infer_relation=True)

    with pytest.raises(ValueError, match="No relation found"):
        Unmatched.get_relations()
