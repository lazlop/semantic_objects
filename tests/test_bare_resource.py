"""
Test that Resource/Node can be hand-subclassed directly, with no ontology
package (s223/watr/cxf) involved.

Regression test for a bug found while prototyping hand-authored templates:
RdfExporter.generate_rdf_class_definition() reads cls._other_types
unconditionally, but only ontology packages set it on their own shared base
(s223/core.py, watr/core.py) - a bare Resource/Node subclass had no default
and raised AttributeError. Resource now defaults _other_types to [].
"""
from rdflib import Namespace

from semantic_objects.core import Node, Predicate, Resource, semantic_object
from semantic_objects.fields import required_field

NS = Namespace("urn:test-bare-resource#")


@semantic_object
class BareNode(Node):
    _ns = NS
    abstract = True


@semantic_object
class hasPoint(Predicate):
    _ns = NS


@semantic_object
class Deadband(BareNode):
    pass


@semantic_object
class Thermostat(BareNode):
    deadband: Deadband = required_field(relation=hasPoint)


@semantic_object
class StagedThermostat(Thermostat):
    stage_count: Deadband = required_field(relation=hasPoint)


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
