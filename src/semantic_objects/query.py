from .namespaces import * 
from rdflib import Graph, URIRef, Literal, RDF
from typing import Type, get_origin, get_args
from dataclasses import _MISSING_TYPE, field

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
            
            where.append(f"{qs} {qp} {qo} .")
        
        where += list(filters.values())
        where = "\n".join(where)
        prefixes = self.get_prefixes()
        query = f"""{prefixes}\nSELECT DISTINCT * WHERE {{ {where} }}"""
        return query
    
    def _add_exact_values_filter(self, graph, subject_node, relation_uri, exact_values):
        """
        Add SPARQL filter for exact value matching.
        
        This ensures the semantic model has exactly the specified values,
        not just at least those values.
        
        Args:
            graph: The RDF graph being queried
            subject_node: The subject node (e.g., PARAM['name'])
            relation_uri: The relation URI (e.g., S223['hasAspect'])
            exact_values: List of exact values that must match
            
        Returns:
            Tuple of (where_clause, filter_clause) to add to the query
        """
        qs = self._get_var_name(graph, subject_node)
        
        if len(exact_values) > 0:
            # Convert exact values to their query names
            exact_value_names = [self._get_var_name(graph, v._get_iri()) for v in exact_values]
            var_name = qs + '_exact_values'
            where_clause = f"{qs} <{str(relation_uri)}> {var_name} ."
            filter_clause = f"FILTER({var_name} IN ({','.join(exact_value_names)}) ) "
            return where_clause, filter_clause
        else:
            # No values means there should be no such relation
            var_name = qs + '_exact_values'
            filter_clause = f"FILTER NOT EXISTS {{ {qs} <{str(relation_uri)}> {var_name} }}"
            return None, filter_clause
    
    def get_sparql_query(self, ontology=None):
        """
        Generate a SPARQL query from the resource class definition.
        
        Args:
            ontology: Optional ontology identifier (e.g., 's223') for special handling
            
        Returns:
            A SPARQL query string that can be used to query for instances of this class
        """
        seen_fields = set()
        exact_value_constraints = []  # Track fields with exact_values metadata
        
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
                    
                    # Check for exact_values metadata
                    exact_values = field_obj.metadata.get('exact_values')
                    if exact_values is not None:
                        # Store for later processing
                        exact_value_constraints.append((field_name, relation, exact_values))
                        continue  # Don't add regular triple for exact_values fields
                    
                    if not isinstance(field_obj.default, _MISSING_TYPE) and field_obj.default is not None:
                        self.graph.add((PARAM['name'], relation._get_iri(), field_obj.default._get_iri()))
                    elif isinstance(field_obj.default, _MISSING_TYPE):
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
                            # Use the actual field type for the RDF type triple instead of _semantic_type
                            self.graph.add((PARAM[field_name], RDF.type, field_type._get_iri()))
                                
                            # Add triples for any class-level fields (fields with init=False and a non-missing default)
                            if hasattr(field_type, '__dataclass_fields__'):
                                for class_field_name, class_field_obj in field_type.__dataclass_fields__.items():
                                    # Check if this is a class-level field (init=False with a default value)
                                    if (not class_field_obj.init and 
                                        not isinstance(class_field_obj.default, _MISSING_TYPE) and
                                        class_field_obj.default is not None):
                                        # Infer the relation for this class-level field
                                        try:
                                            class_field_relation = field_type._infer_relation_for_field(class_field_name, class_field_obj)
                                            # Get the value - it should be a class attribute
                                            class_field_value = getattr(field_type, class_field_name)
                                            # Add triple for this class-level constraint
                                            if hasattr(class_field_value, '_get_iri'):
                                                self.graph.add((PARAM[field_name], class_field_relation._get_iri(), class_field_value._get_iri()))
                                        except (ValueError, AttributeError):
                                            # If we can't infer the relation or get the value, skip it
                                                pass
                            else:
                                # Add type triple for this dependency using the field type itself
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
        
        # Generate the base query
        query = self._get_query(self.graph, ontology)
        
        # Add exact_values constraints if any
        if exact_value_constraints:
            # Parse the query to insert the exact value filters
            query = self._add_exact_values_to_query(query, exact_value_constraints)
        
        return query
    
    def _add_exact_values_to_query(self, query, exact_value_constraints):
        """
        Add exact value constraints to an existing SPARQL query.
        
        Args:
            query: The base SPARQL query string
            exact_value_constraints: List of (field_name, relation, exact_values) tuples
            
        Returns:
            Modified query string with exact value filters
        """
        # Split query into parts
        parts = query.split('WHERE {')
        if len(parts) != 2:
            return query
        
        prefix_part = parts[0]
        where_part = parts[1].rstrip(' }')
        
        # Add exact value patterns and filters
        additional_where = []
        additional_filters = []
        
        for field_name, relation, exact_values in exact_value_constraints:
            where_clause, filter_clause = self._add_exact_values_filter(
                self.graph, PARAM['name'], relation._get_iri(), exact_values
            )
            if where_clause:
                additional_where.append(where_clause)
            if filter_clause:
                additional_filters.append(filter_clause)
        
        # Reconstruct query
        new_where = where_part
        if additional_where:
            new_where += '\n' + '\n'.join(additional_where)
        if additional_filters:
            new_where += '\n' + '\n'.join(additional_filters)
        
        return f"{prefix_part}WHERE {{ {new_where} }}"
