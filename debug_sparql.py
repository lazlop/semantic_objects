#!/usr/bin/env python3
"""
Debug SPARQL query execution
"""

from rdflib import Graph
from src.semantic_objects.s223.properties import EnvironmentalStation

def debug_sparql_query():
    print("=" * 60)
    print("Debug SPARQL Query Execution")
    print("=" * 60)
    
    # Load the RDF file
    g = Graph()
    g.parse('test_env_station.ttl', format='turtle')
    
    print(f"Loaded {len(g)} triples from RDF file")
    
    # Print all triples for debugging
    print("\nAll triples in the graph:")
    for s, p, o in g:
        print(f"  {s} {p} {o}")
    
    # Get the generated SPARQL query
    sparql_query = EnvironmentalStation.get_sparql_query(ontology='s223')
    print(f"\nGenerated SPARQL query:")
    print(sparql_query)
    
    # Execute the query
    print(f"\nExecuting query...")
    results = g.query(sparql_query)
    
    print(f"Query results: {len(list(results))} rows")
    for row in results:
        print(f"  {row}")
    
    # Try a simpler query to see if the basic structure is there
    simple_query = """
    PREFIX s223: <http://data.ashrae.org/standard223#>
    SELECT ?station WHERE {
        ?station a s223:Environmental_Station .
    }
    """
    
    print(f"\nTrying simple query:")
    print(simple_query)
    simple_results = g.query(simple_query)
    print(f"Simple query results: {len(list(simple_results))} rows")
    for row in simple_results:
        print(f"  {row}")
    
    # Try querying for properties
    prop_query = """
    PREFIX s223: <http://data.ashrae.org/standard223#>
    SELECT ?station ?prop WHERE {
        ?station a s223:Environmental_Station .
        ?station s223:hasProperty ?prop .
    }
    """
    
    print(f"\nTrying property query:")
    print(prop_query)
    prop_results = g.query(prop_query)
    print(f"Property query results: {len(list(prop_results))} rows")
    for row in prop_results:
        print(f"  {row}")

if __name__ == "__main__":
    debug_sparql_query()