"""
Test exact_values field metadata functionality.

This test verifies that the generalized exact_values approach works correctly
for querying semantic models that must have exactly the specified values.
"""

from semantic_objects.s223.properties import Area_SP
from semantic_objects.s223.enumerationkinds import Setpoint, Deadband, Occupancy


def test_area_sp_query_generation():
    """Test that Area_SP generates correct SPARQL query with exact aspect values."""
    
    # Generate the SPARQL query
    query = Area_SP.get_sparql_query(ontology='s223')
    
    print("Generated SPARQL Query:")
    print(query)
    print("\n")
    
    # Verify the query contains the expected components
    assert 'FILTER' in query, "Query should contain FILTER clause for exact values"
    assert 'hasAspect' in query or 's223:hasAspect' in query, "Query should reference hasAspect relation"
    
    # Check that all three aspect values are referenced
    # Note: The actual names in the query use the full IRI names
    assert 'Setpoint' in query or 'Aspect-Setpoint' in query, "Query should reference Setpoint"
    assert 'Threshold' in query or 'Aspect-Threshold' in query, "Query should reference Deadband/Threshold"
    assert 'Occupancy' in query or 'Domain-Occupancy' in query, "Query should reference Occupancy"
    
    # Verify it uses IN filter for exact matching
    assert 'IN' in query, "Query should use IN clause for exact value matching"
    
    print("✓ Query generation test passed")


def test_exact_values_metadata():
    """Test that exact_values metadata is properly set on the field."""
    
    # Get the field metadata
    field_obj = Area_SP.__dataclass_fields__['aspects']
    
    # Verify exact_values is in metadata
    assert 'exact_values' in field_obj.metadata, "Field should have exact_values in metadata"
    
    # Verify the exact values are correct
    exact_values = field_obj.metadata['exact_values']
    assert len(exact_values) == 3, "Should have exactly 3 aspect values"
    assert Setpoint in exact_values, "Should include Setpoint"
    assert Deadband in exact_values, "Should include Deadband"
    assert Occupancy in exact_values, "Should include Occupancy"
    
    print("✓ Metadata test passed")


def test_field_relation():
    """Test that the relation is properly set."""
    
    from semantic_objects.s223.relations import hasAspect
    
    field_obj = Area_SP.__dataclass_fields__['aspects']
    
    # Verify relation is in metadata
    assert 'relation' in field_obj.metadata, "Field should have relation in metadata"
    assert field_obj.metadata['relation'] == hasAspect, "Relation should be hasAspect"
    
    print("✓ Relation test passed")


if __name__ == '__main__':
    print("Testing exact_values field metadata functionality...\n")
    
    test_exact_values_metadata()
    test_field_relation()
    test_area_sp_query_generation()
    
    print("\n✅ All tests passed!")
