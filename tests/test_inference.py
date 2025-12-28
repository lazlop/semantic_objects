"""
Test the inference module for generating annotation rules and running inference.
"""

from rdflib import Graph, Literal, URIRef
from semantic_objects.s223 import entities, properties
from semantic_objects.inference import (
    generate_annotation_rules,
    infer_types,
    AnnotationRuleGenerator,
    InferenceEngine
)
from semantic_objects.namespaces import RDF, S223, HPFS, bind_prefixes


def test_generate_annotation_rules_from_modules():
    """Test generating annotation rules from module imports"""
    print("\n=== Testing Annotation Rule Generation from Modules ===")
    
    # Generate rules from the entities and properties modules
    rules = generate_annotation_rules([entities, properties])
    
    # Check that rules were generated
    assert len(rules) > 0, "No rules were generated"
    
    # Print some statistics
    print(f"Generated {len(rules)} triples in annotation rules graph")
    
    # Check for specific annotation shapes
    annotation_shapes = list(rules.subjects(RDF.type, URIRef("http://www.w3.org/ns/shacl#NodeShape")))
    print(f"Found {len(annotation_shapes)} annotation shapes")
    
    # Save to file for inspection
    rules.serialize('tests/output/annotation_rules.ttl', format='turtle')
    print("Saved annotation rules to tests/output/annotation_rules.ttl")
    
    return rules


def test_generate_annotation_rules_from_classes():
    """Test generating annotation rules from specific classes"""
    print("\n=== Testing Annotation Rule Generation from Classes ===")
    
    # Generate rules for specific classes
    from semantic_objects.s223.entities import Space, Window
    from semantic_objects.s223.properties import Area, Azimuth
    
    rules = generate_annotation_rules([Space, Window, Area, Azimuth])
    
    assert len(rules) > 0, "No rules were generated"
    print(f"Generated {len(rules)} triples for specific classes")
    
    return rules


def test_annotation_rule_structure():
    """Test that annotation rules have the correct structure"""
    print("\n=== Testing Annotation Rule Structure ===")
    
    from semantic_objects.s223.entities import Space
    
    generator = AnnotationRuleGenerator()
    rules = generator.generate_annotation_rules(Space)
    
    # Check for Space annotation shape
    space_annotation = HPFS["SpaceAnnotation"]
    assert (space_annotation, RDF.type, URIRef("http://www.w3.org/ns/shacl#NodeShape")) in rules
    
    # Check for annotation rule
    space_rule = HPFS["SpaceAnnotationRule"]
    assert (space_annotation, URIRef("http://www.w3.org/ns/shacl#rule"), space_rule) in rules
    assert (space_rule, RDF.type, URIRef("http://www.w3.org/ns/shacl#TripleRule")) in rules
    
    # Check rule structure (subject, predicate, object)
    assert (space_rule, URIRef("http://www.w3.org/ns/shacl#subject"), URIRef("http://www.w3.org/ns/shacl#this")) in rules
    assert (space_rule, URIRef("http://www.w3.org/ns/shacl#predicate"), RDF.type) in rules
    
    print("Annotation rule structure is correct")
    
    return rules


def test_create_sample_data():
    """Create sample RDF data for testing inference"""
    print("\n=== Creating Sample Data ===")
    
    data = Graph()
    bind_prefixes(data)
    
    # Create a space instance with area property
    space1 = URIRef("http://example.org/Space1")
    area1 = URIRef("http://example.org/Area1")
    
    # Add triples that match the Space pattern
    data.add((space1, RDF.type, S223.DomainSpace))
    data.add((space1, S223.hasProperty, area1))
    
    # Add area property details
    data.add((area1, RDF.type, S223.QuantifiableObservableProperty))
    data.add((area1, URIRef("http://qudt.org/schema/qudt/hasQuantityKind"), 
              URIRef("http://qudt.org/vocab/quantitykind/Area")))
    data.add((area1, URIRef("http://qudt.org/schema/qudt/hasValue"), Literal(100.0)))
    
    print(f"Created sample data with {len(data)} triples")
    data.serialize('tests/output/sample_data.ttl', format='turtle')
    print("Saved sample data to tests/output/sample_data.ttl")
    
    return data


def test_inference_without_tq_shacl():
    """Test inference without TopQuadrant SHACL (using pyshacl)"""
    print("\n=== Testing Inference without TQ SHACL ===")
    
    # Create sample data
    data = test_create_sample_data()
    
    # Generate annotation rules
    rules = generate_annotation_rules([entities, properties])
    
    # Try inference without TQ SHACL
    try:
        inferred_data = infer_types(data, annotation_rules=rules, use_tq_shacl=False)
        print("Inference completed (pyshacl mode)")
        print(f"Data graph now has {len(inferred_data)} triples")
    except ImportError as e:
        print(f"Skipping pyshacl test: {e}")
    
    return data


def test_save_and_load_rules():
    """Test saving and loading annotation rules"""
    print("\n=== Testing Save and Load Rules ===")
    
    # Generate rules
    generator = AnnotationRuleGenerator()
    rules = generator.generate_annotation_rules([entities, properties])
    
    # Save to file
    generator.save_shapes('tests/output/saved_rules.ttl', format='turtle')
    print("Saved rules to tests/output/saved_rules.ttl")
    
    # Load from file
    loaded_rules = Graph()
    loaded_rules.parse('tests/output/saved_rules.ttl', format='turtle')
    
    assert len(loaded_rules) == len(rules), "Loaded rules don't match saved rules"
    print(f"Successfully loaded {len(loaded_rules)} triples")
    
    return loaded_rules


def main():
    """Run all tests"""
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs('tests/output', exist_ok=True)
    
    print("=" * 60)
    print("INFERENCE MODULE TESTS")
    print("=" * 60)
    
    try:
        # Test annotation rule generation
        test_generate_annotation_rules_from_modules()
        test_generate_annotation_rules_from_classes()
        test_annotation_rule_structure()
        
        # Test data creation and inference
        test_create_sample_data()
        test_inference_without_tq_shacl()
        
        # Test save/load
        test_save_and_load_rules()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n!!! TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
