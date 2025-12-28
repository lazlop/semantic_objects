"""
Test the _semantic_type generalization for class hierarchies.

This test verifies that the _semantic_type attribute allows classes to specify
which parent type should be used in the semantic model, replacing the hardcoded
QuantifiableObservableProperty checks.
"""

from src.semantic_objects.s223.properties import Area, Azimuth, QuantifiableObservableProperty
from src.semantic_objects.query import SparqlQueryBuilder
from rdflib import Graph, RDF


def test_semantic_type_attribute():
    """Test that Area has _semantic_type set to QuantifiableObservableProperty"""
    assert hasattr(Area, '_semantic_type')
    assert Area._semantic_type == QuantifiableObservableProperty
    assert hasattr(Azimuth, '_semantic_type')
    assert Azimuth._semantic_type == QuantifiableObservableProperty


def test_query_uses_semantic_type():
    """Test that SPARQL query generation uses _semantic_type instead of the subclass"""
    from src.semantic_objects.s223.entities import Space
    
    # Generate query for Space which has an Area field
    query = Space.get_sparql_query()
    
    # The query should reference QuantifiableObservableProperty, not Area
    assert 'QuantifiableObservableProperty' in query
    
    # It should also include the hasQuantityKind constraint for the qk field
    assert 'hasQuantityKind' in query
    assert 'Area' in query  # The quantity kind Area should be in the query


def test_semantic_type_in_query_builder():
    """Test that SparqlQueryBuilder correctly handles _semantic_type"""
    from src.semantic_objects.s223.entities import Space
    
    builder = SparqlQueryBuilder(Space)
    
    # Build the query
    query = builder.get_sparql_query()
    
    # Check that the graph contains the right triples
    # The area field should be typed as QuantifiableObservableProperty
    found_qop_type = False
    found_qk_constraint = False
    
    for s, p, o in builder.graph:
        if p == RDF.type and 'QuantifiableObservableProperty' in str(o):
            found_qop_type = True
        if 'hasQuantityKind' in str(p):
            found_qk_constraint = True
    
    assert found_qop_type, "Should find QuantifiableObservableProperty type triple"
    assert found_qk_constraint, "Should find hasQuantityKind constraint"


def test_class_level_field_detection():
    """Test that class-level fields (init=False with default) are detected correctly"""
    # Area has qk as a class-level field
    assert hasattr(Area, '__dataclass_fields__')
    
    qk_field = Area.__dataclass_fields__['qk']
    assert qk_field.init == False, "qk should have init=False"
    assert qk_field.default is not None, "qk should have a default value"
    
    # The qk value should be accessible as a class attribute
    from src.semantic_objects.qudt import quantitykinds
    assert Area.qk == quantitykinds.Area


def test_instance_level_fields():
    """Test that instance-level fields are correctly identified"""
    # value and unit are instance-level fields
    value_field = Area.__dataclass_fields__['value']
    assert value_field.init == True, "value should have init=True"
    
    unit_field = Area.__dataclass_fields__['unit']
    assert unit_field.init == True, "unit should have init=True"


if __name__ == '__main__':
    test_semantic_type_attribute()
    test_query_uses_semantic_type()
    test_semantic_type_in_query_builder()
    test_class_level_field_detection()
    test_instance_level_fields()
    print("All tests passed!")
