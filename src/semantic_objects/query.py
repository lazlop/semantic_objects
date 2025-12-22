from .namespaces import * 
from rdflib import Graph, URIRef, Literal, RDF
from typing import Type, get_origin, get_args
from dataclasses import _MISSING_TYPE

class SparqlQueryBuilder:
    """
    A class for building SPARQL queries from Resource class definitions.
    
    This separates query generation logic from the Resource class itself,
    making it easier to maintain and extend query generation capabilities.
    """
    
    def __init__(self, resource_class: Type['Resource']):
        """
        Initialize the query builder with a Resource class.
        
        Args:
            resource_class: The Resource class to build queries for
        """
        self.resource_class = resource_class
        self.used_namespaces = []
        self.graph = Graph()
        bind_prefixes(self.graph)
        # Add the class type triple
        self.graph.add((PARAM['name'], RDF.type, self.resource_class._get_iri()))

    def convert_to_prefixed(self, uri):
        """Convert a URI to prefixed notation using the graph's namespace bindings."""
        try:
            prefix, namespace, name = self.graph.compute_qname(uri)
            self.used_namespaces.append(namespace)
            return f"{prefix}:{name}"
        except:
            # If we can't compute a qname, return the full URI in angle brackets
            return f"<{uri}>"

    def get_prefixes(self):
        """Generate SPARQL prefix declarations from graph namespaces."""
        prefixes = []
        for prefix, namespace in self.graph.namespaces():
            if namespace in self.used_namespaces:
                prefixes.append(f"PREFIX {prefix}: <{namespace}>")
        return "\n".join(prefixes)
    
    def _get_var_name(self, graph, node, force_as_variable=False):
        """Generate variable names for SPARQL queries from RDF nodes."""
        if isinstance(node, Literal):
            return node
        pre, ns, local = graph.compute_qname(node)
        if (PARAM == ns) or force_as_variable:
            q_n = f"?{local}".replace('-', '_')
        else:
            q_n = self.convert_to_prefixed(node)
        return q_n
    
    def _get_query(self, graph, ontology=None):
        """Generate WHERE clause for SPARQL query from RDF graph."""
        where = []
        filters = {}
        
        namespaces = []
        for s, p, o in graph.triples((None, None, None)):
            qs = self._get_var_name(graph, s)
            qo = self._get_var_name(graph, o)
            qp = self.convert_to_prefixed(p)
            
            # Special handling for s223 ontology if specified
            if ontology == 's223':
                # Import S223 namespace if available
                try:
                    from semantic_mpc_interface.namespaces import S223, A
                    
                    if p == A and (o == S223['QuantifiableObservableProperty'] or 
                                o == S223['QuantifiableActuatableProperty'] or
                                o == S223['EnumeratedObservableProperty'] or 
                                o == S223['EnumeratedActuatableProperty']) and (s not in filters.keys()):
                        aspects = list(graph.objects(s, S223['hasAspect']))
                        if len(aspects) > 0:
                            aspects = [self._get_var_name(graph, a) for a in aspects]
                            aspect_var = qs + '_aspects_in'
                            where.append(f"{qs} <{str(S223['hasAspect'])}> {aspect_var} .")
                            filters[s] = f"FILTER({aspect_var} IN ({','.join(aspects)}) ) "
                        else:
                            aspect_var = qs + '_aspects_in'
                            filters[s] = f"FILTER NOT EXISTS {{ {qs} <{str(S223['hasAspect'])}> {aspect_var} }}"
                except ImportError:
                    pass  # S223 namespace not available, skip special handling
            
            where.append(f"{qs} {qp} {qo} .")
        
        where += list(filters.values())
        where = "\n".join(where)
        prefixes = self.get_prefixes()
        query = f"""{prefixes}\nSELECT DISTINCT * WHERE {{ {where} }}"""
        return query
    
    def get_sparql_query(self, ontology=None):
        """
        Generate a SPARQL query from the resource class definition.
        
        Args:
            ontology: Optional ontology identifier (e.g., 's223') for special handling
            
        Returns:
            A SPARQL query string that can be used to query for instances of this class
        """
        seen_fields = set()
        for base in self.resource_class.__mro__:
            if hasattr(base, '__dataclass_fields__'):
                for field_name, field_obj in base.__dataclass_fields__.items():
                    # Skip fields with init=False and templatize=False
                    if (field_obj.init == False and 
                        field_obj.metadata.get('templatize', True) == False):
                        continue
                    if field_name in seen_fields:
                        continue
                    seen_fields.add(field_name)
                    
                    relation = self.resource_class._infer_relation_for_field(field_name, field_obj)
                    if not isinstance(field_obj.default, _MISSING_TYPE):
                        self.graph.add((PARAM['name'], relation._get_iri(), field_obj.default._get_iri()))
                    else:
                        self.graph.add((PARAM['name'], relation._get_iri(), PARAM[field_name]))
                        
                        # Add type triple for Resource subclass dependencies
                        field_type = field_obj.type
                        # Handle Optional, List, etc. - extract the actual type
                        origin = get_origin(field_type)
                        if origin is not None:
                            args = get_args(field_type)
                            if args:
                                field_type = args[0]
                        
                        # Check if the field type is a subclass of Resource
                        if (hasattr(field_type, '__mro__') and 
                            any(base.__name__ == 'Resource' for base in field_type.__mro__)):
                            # Add type triple for this dependency
                            self.graph.add((PARAM[field_name], RDF.type, field_type._get_iri()))
        
        # Now bind the prefixes we need by calling convert_to_prefixed on each URI
        # This will cause RDFLib to automatically bind the necessary namespaces
        for s, p, o in self.graph.triples((None, None, None)):
            for node in [s, p, o]:
                if isinstance(node, URIRef):
                    # This call will bind the namespace if needed
                    try:
                        self.graph.compute_qname(node)
                    except:
                        pass
        
        # Generate and return the SPARQL query
        # The graph now has only the namespaces that were actually used
        return self._get_query(self.graph, ontology)
    