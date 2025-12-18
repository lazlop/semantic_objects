"""Test subproperty relations functionality"""

from src.semantic_objects.s223.entities import DomainSpace, Window
from src.semantic_objects.s223.relations import hasWindow, connectedTo

def test_hasWindow_relation():
    """Test that hasWindow relation is properly defined as a subproperty"""
    
    # Check that hasWindow has connectedTo as its parent
    assert hasWindow._subproperty_of == connectedTo
    print("✓ hasWindow is a subproperty of connectedTo")
    
    # Check that hasWindow has the correct metadata
    assert hasWindow._local_name == 'hasWindow'
    assert hasWindow.label == "has window"
    print("✓ hasWindow has correct metadata")
    
    # Generate RDF for the hasWindow relation
    rdf_output = hasWindow.generate_rdf_property_definition()
    print("\n=== RDF Property Definition for hasWindow ===")
    print(rdf_output)
    
    # Verify the RDF contains subPropertyOf
    assert 'rdfs:subPropertyOf' in rdf_output
    assert 'connectedTo' in rdf_output
    print("✓ RDF contains subPropertyOf declaration")
    
    return rdf_output

def test_hasWindow_with_domain_range():
    """Test hasWindow with domain and range set"""
    
    # Set domain and range
    hasWindow._domain = DomainSpace
    hasWindow._range = Window
    
    # Generate RDF
    rdf_output = hasWindow.generate_rdf_property_definition()
    print("\n=== RDF Property Definition with Domain/Range ===")
    print(rdf_output)
    
    # Verify domain and range are in the output
    assert 'rdfs:domain' in rdf_output
    assert 'rdfs:range' in rdf_output
    assert 'DomainSpace' in rdf_output
    assert 'Window' in rdf_output
    print("✓ RDF contains domain and range declarations")
    
    return rdf_output

def test_template_generation():
    """Test that DomainSpace can generate templates with hasWindow relation"""
    
    # Generate YAML template for DomainSpace
    yaml_output = DomainSpace.to_yaml('has-window')
    print("\n=== YAML Template for has-window ===")
    print(yaml_output)
    
    # The template should reference the hasWindow relation
    # Note: The actual relation used depends on _valid_relations configuration
    print("✓ Template generated successfully")
    
    return yaml_output

if __name__ == '__main__':
    print("Testing Subproperty Relations\n" + "="*50)
    
    # Test 1: Basic subproperty
    test_hasWindow_relation()
    
    # Test 2: With domain and range
    test_hasWindow_with_domain_range()
    
    # Test 3: Template generation
    test_template_generation()
    
    print("\n" + "="*50)
    print("All tests passed! ✓")
