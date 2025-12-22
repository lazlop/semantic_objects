"""
Test and demonstrate the ModelLoader functionality.

This file shows how to use the new ModelLoader to query RDF graphs
and instantiate Python objects based on Resource class definitions.
"""

from rdflib import Graph, Namespace, Literal, URIRef
from semantic_objects.model_loader import ModelLoader
from semantic_objects.s223.entities import Space, Window
from semantic_objects.s223.properties import Area, Azimuth, Tilt
from semantic_objects.namespaces import S223, QUDT, UNIT, bind_prefixes


def create_sample_graph():
    """Create a sample RDF graph with spaces and windows for testing."""
    g = Graph()
    bind_prefixes(g)
    
    # Define a namespace for our test data
    EX = Namespace("http://example.org/building#")
    g.bind("ex", EX)
    
    # Create a Space with an Area property
    space1 = EX["Space1"]
    g.add((space1, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), S223["Space"]))
    
    # Create Area property for the space
    area1 = EX["Space1_Area"]
    g.add((area1, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), S223["QuantifiableObservableProperty"]))
    g.add((area1, QUDT["hasQuantityKind"], URIRef("http://qudt.org/vocab/quantitykind/Area")))
    g.add((area1, S223["hasValue"], Literal(100.0)))
    g.add((area1, QUDT["hasUnit"], UNIT["FT2"]))
    g.add((space1, S223["hasProperty"], area1))
    
    # Create another Space
    space2 = EX["Space2"]
    g.add((space2, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), S223["Space"]))
    
    area2 = EX["Space2_Area"]
    g.add((area2, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), S223["QuantifiableObservableProperty"]))
    g.add((area2, QUDT["hasQuantityKind"], URIRef("http://qudt.org/vocab/quantitykind/Area")))
    g.add((area2, S223["hasValue"], Literal(150.0)))
    g.add((area2, QUDT["hasUnit"], UNIT["M2"]))
    g.add((space2, S223["hasProperty"], area2))
    
    # Create a Window with multiple properties
    window1 = EX["Window1"]
    g.add((window1, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), S223["Window"]))
    
    # Window area
    window_area = EX["Window1_Area"]
    g.add((window_area, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), S223["QuantifiableObservableProperty"]))
    g.add((window_area, QUDT["hasQuantityKind"], URIRef("http://qudt.org/vocab/quantitykind/Area")))
    g.add((window_area, S223["hasValue"], Literal(10.0)))
    g.add((window_area, QUDT["hasUnit"], UNIT["FT2"]))
    g.add((window1, S223["hasProperty"], window_area))
    
    # Window azimuth
    window_azimuth = EX["Window1_Azimuth"]
    g.add((window_azimuth, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), S223["QuantifiableObservableProperty"]))
    g.add((window_azimuth, QUDT["hasQuantityKind"], URIRef("http://qudt.org/vocab/quantitykind/Azimuth")))
    g.add((window_azimuth, S223["hasValue"], Literal(180.0)))
    g.add((window_azimuth, QUDT["hasUnit"], UNIT["DEG"]))
    g.add((window1, S223["hasProperty"], window_azimuth))
    
    # Window tilt
    window_tilt = EX["Window1_Tilt"]
    g.add((window_tilt, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), S223["QuantifiableObservableProperty"]))
    g.add((window_tilt, QUDT["hasQuantityKind"], URIRef("http://qudt.org/vocab/quantitykind/Tilt")))
    g.add((window_tilt, S223["hasValue"], Literal(90.0)))
    g.add((window_tilt, QUDT["hasUnit"], UNIT["DEG"]))
    g.add((window1, S223["hasProperty"], window_tilt))
    
    return g


def test_query_generation():
    """Test SPARQL query generation from Resource classes."""
    print("=" * 80)
    print("TEST: SPARQL Query Generation")
    print("=" * 80)
    
    # Generate query for Space class
    space_query = Space.get_sparql_query(ontology='s223')
    print("\nGenerated SPARQL query for Space class:")
    print(space_query)
    
    # Generate query for Window class
    window_query = Window.get_sparql_query(ontology='s223')
    print("\nGenerated SPARQL query for Window class:")
    print(window_query)
    print()


def test_load_instances():
    """Test loading instances from an RDF graph."""
    print("=" * 80)
    print("TEST: Loading Instances from RDF Graph")
    print("=" * 80)
    
    # Create sample graph
    g = create_sample_graph()
    
    # Initialize ModelLoader
    loader = ModelLoader(source=g)
    
    # Query for Space instances
    print("\nQuerying for Space instances...")
    space_df = loader.query_class(Space, ontology='s223')
    print(f"Found {len(space_df)} Space instances")
    print("\nDataFrame columns:", space_df.columns.tolist())
    if not space_df.empty:
        print("\nFirst few rows:")
        print(space_df.head())
    
    # Load Space instances as objects
    print("\n" + "-" * 80)
    print("Loading Space instances as Python objects...")
    spaces = loader.load_instances(Space, ontology='s223')
    print(f"Loaded {len(spaces)} Space objects")
    
    for space in spaces:
        print(f"\nSpace: {space._name}")
        if hasattr(space, 'area'):
            print(f"  Area: {space.area}")
    
    # Query for Window instances
    print("\n" + "-" * 80)
    print("Querying for Window instances...")
    window_df = loader.query_class(Window, ontology='s223')
    print(f"Found {len(window_df)} Window instances")
    
    # Load Window instances as objects
    print("\nLoading Window instances as Python objects...")
    windows = loader.load_instances(Window, ontology='s223')
    print(f"Loaded {len(windows)} Window objects")
    
    for window in windows:
        print(f"\nWindow: {window._name}")
        if hasattr(window, 'area'):
            print(f"  Area: {window.area}")
        if hasattr(window, 'azimuth'):
            print(f"  Azimuth: {window.azimuth}")
        if hasattr(window, 'tilt'):
            print(f"  Tilt: {window.tilt}")
    print()


def test_load_multiple_classes():
    """Test loading multiple classes at once."""
    print("=" * 80)
    print("TEST: Loading Multiple Classes")
    print("=" * 80)
    
    # Create sample graph
    g = create_sample_graph()
    
    # Initialize ModelLoader
    loader = ModelLoader(source=g)
    
    # Load multiple classes
    print("\nLoading multiple classes...")
    results = loader.load_multiple_classes(
        {
            'spaces': Space,
            'windows': Window
        },
        ontology='s223'
    )
    
    print(f"\nResults:")
    for key, instances in results.items():
        print(f"  {key}: {len(instances)} instances")
        for instance in instances:
            print(f"    - {instance._name}")
    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("MODEL LOADER TESTS")
    print("=" * 80 + "\n")
    
    try:
        test_query_generation()
        test_load_instances()
        test_load_multiple_classes()
        
        print("=" * 80)
        print("ALL TESTS COMPLETED")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
