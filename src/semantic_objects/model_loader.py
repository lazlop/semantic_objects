"""
Model Loader - Load semantic data from RDF graphs into Python objects

This module provides functionality to query RDF graphs and instantiate
Python objects based on Resource class definitions. It replaces the old
LoadModel class with a modern approach using the Resource class system.
"""

import os
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Type, get_origin, get_args
from pathlib import Path
from dataclasses import fields, is_dataclass, MISSING

from rdflib import Graph, Literal, Namespace, URIRef
from buildingmotif import BuildingMOTIF, get_building_motif
from buildingmotif.dataclasses import Library, Model

from .namespaces import *
from .core import Resource, Node, NamedNode
from .query import SparqlQueryBuilder


def query_to_df(query: str, graph: Graph, prefixed: bool = False) -> pd.DataFrame:
    """
    Execute a SPARQL query and return results as a pandas DataFrame.
    
    Args:
        query: SPARQL query string
        graph: RDF graph to query
        prefixed: If True, keep prefixed notation; if False, use full URIs
        
    Returns:
        DataFrame with query results
    """
    results = graph.query(query)
    
    # Convert results to list of dictionaries
    rows = []
    for row in results:
        row_dict = {}
        for var in results.vars:
            value = row[var]
            if value is not None:
                if prefixed:
                    row_dict[str(var)] = value
                else:
                    # Convert to string representation
                    row_dict[str(var)] = str(value) if not isinstance(value, Literal) else value
            else:
                row_dict[str(var)] = None
        rows.append(row_dict)
    
    return pd.DataFrame(rows)


class ModelLoader:
    """
    Load semantic data from RDF graphs into Python objects based on Resource classes.
    
    This class provides functionality similar to the old LoadModel class but uses
    the modern Resource-based architecture.
    """
    
    def __init__(
        self,
        source: Union[str, Graph],
        namespace: Union[str, Namespace] = None,
        template_dir: Optional[str] = None,
        load_ontology: bool = False
    ):
        """
        Initialize the ModelLoader.
        
        Args:
            source: Path to RDF file or RDF Graph object
            namespace: Namespace for the model (default: urn:model#)
            template_dir: Directory containing BuildingMOTIF templates (optional)
            load_ontology: If True, load relevant ontologies (e.g., s223)
        """
        # Load or use the provided graph
        if isinstance(source, str) and os.path.isfile(source):
            self.g = Graph()
            self.g.parse(source)
        elif isinstance(source, Graph):
            self.g = source
        else:
            raise ValueError("Source must be a file path or an RDF graph.")
        
        bind_prefixes(self.g)
        
        # Set up namespace
        if namespace is None:
            self.namespace = Namespace("urn:model#")
        elif isinstance(namespace, str):
            self.namespace = Namespace(namespace)
        else:
            self.namespace = namespace
        
        # Load ontology if requested
        if load_ontology:
            # Try to load s223 ontology
            try:
                self.g.parse("https://open223.info/223p.ttl", format="ttl")
            except Exception as e:
                print(f"Warning: Could not load s223 ontology: {e}")
        
        # Initialize BuildingMOTIF if template_dir is provided
        self.template_dir = template_dir
        self.library = None
        if template_dir:
            try:
                self.bm = get_building_motif()
                self.library = Library.load(db_id=1, overwrite=True)
            except Exception:
                self.bm = BuildingMOTIF("sqlite://")
                self.library = Library.load(directory=str(template_dir), overwrite=True)
    
    def query_class(
        self,
        resource_class: Type[Resource],
        ontology: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Query the graph for instances of a Resource class.
        
        Args:
            resource_class: The Resource class to query for
            ontology: Optional ontology identifier (e.g., 's223') for special handling
            
        Returns:
            DataFrame with query results
        """
        # Generate SPARQL query from the class definition
        query = resource_class.get_sparql_query(ontology=ontology)
        
        # Execute query and return results
        return query_to_df(query, self.g, prefixed=False)
    
    def _get_field_value_from_uri(
        self,
        uri: URIRef,
        field_type: Type,
        field_obj
    ) -> Any:
        """
        Extract a field value from a URI in the graph.
        
        Args:
            uri: The URI to extract value from
            field_type: Expected type of the field
            field_obj: The dataclass field object
            
        Returns:
            The extracted value, properly typed
        """
        # Handle Optional types - extract the actual type
        origin = get_origin(field_type)
        if origin is not None:
            args = get_args(field_type)
            if args:
                field_type = args[0]
        
        # If the field type is a Resource subclass, we'll handle it separately
        if isinstance(field_type, type) and issubclass(field_type, Resource):
            # For now, just return the URI - we'll instantiate later
            return uri
        
        # Check for literal values
        literal_value = self.g.value(uri, S223['hasValue'])
        if literal_value is not None:
            # Try to convert to the expected type
            if field_type == float:
                return float(literal_value)
            elif field_type == int:
                return int(literal_value)
            elif field_type == str:
                return str(literal_value)
            else:
                return literal_value
        
        # Check for unit information
        unit_uri = self.g.value(uri, QUDT['hasUnit'])
        if unit_uri is not None:
            # Return unit information
            return unit_uri
        
        # If no specific value found, return the URI itself
        return uri
    
    def _instantiate_from_row(
        self,
        resource_class: Type[Resource],
        row: pd.Series,
        instances_cache: Dict[str, Any] = None
    ) -> Resource:
        """
        Instantiate a Resource object from a DataFrame row.
        
        Args:
            resource_class: The Resource class to instantiate
            row: DataFrame row with query results
            instances_cache: Cache of already instantiated objects to avoid duplicates
            
        Returns:
            Instantiated Resource object
        """
        if instances_cache is None:
            instances_cache = {}
        
        # Get the main entity URI (should be in 'name' column)
        entity_uri = row.get('name')
        if entity_uri is None:
            raise ValueError("Row must contain 'name' column with entity URI")
        
        # Check if we've already instantiated this entity
        entity_key = str(entity_uri)
        if entity_key in instances_cache:
            return instances_cache[entity_key]
        
        # Prepare kwargs for instantiation
        kwargs = {}
        
        # Get the _name for the instance
        if issubclass(resource_class, Node):
            # Extract local name from URI
            try:
                _, _, local_name = self.g.compute_qname(entity_uri)
                kwargs['_name'] = local_name
            except:
                kwargs['_name'] = str(entity_uri).split('#')[-1].split('/')[-1]
        
        # Process each field
        if hasattr(resource_class, '__dataclass_fields__'):
            for field_name, field_obj in resource_class.__dataclass_fields__.items():
                # Skip _name field as we handled it above
                if field_name == '_name':
                    continue
                
                # Skip fields with init=False
                if not field_obj.init:
                    continue
                
                # Check if this field is in the row
                if field_name in row.index and row[field_name] is not None:
                    field_value_uri = row[field_name]
                    field_type = field_obj.type
                    
                    # Handle Optional types
                    origin = get_origin(field_type)
                    if origin is not None:
                        args = get_args(field_type)
                        if args:
                            field_type = args[0]
                    
                    # If field type is a Resource subclass, recursively instantiate
                    if isinstance(field_type, type) and issubclass(field_type, Resource):
                        # Check if it's a NamedNode (fixed value)
                        if issubclass(field_type, NamedNode):
                            # Just use the class itself
                            kwargs[field_name] = field_type
                        else:
                            # Recursively instantiate the related object
                            # For now, create a simple instance with just the URI
                            if str(field_value_uri) in instances_cache:
                                kwargs[field_name] = instances_cache[str(field_value_uri)]
                            else:
                                # Create a minimal instance
                                try:
                                    _, _, local_name = self.g.compute_qname(field_value_uri)
                                except:
                                    local_name = str(field_value_uri).split('#')[-1].split('/')[-1]
                                
                                # Get value if it's a property
                                value = self.g.value(field_value_uri, S223['hasValue'])
                                unit = self.g.value(field_value_uri, QUDT['hasUnit'])
                                
                                if value is not None:
                                    # It's a property with a value
                                    related_kwargs = {'_name': local_name}
                                    if 'value' in [f.name for f in fields(field_type)]:
                                        related_kwargs['value'] = float(value) if value else None
                                    if 'unit' in [f.name for f in fields(field_type)] and unit:
                                        # Find the Unit class for this unit
                                        try:
                                            _, _, unit_name = self.g.compute_qname(unit)
                                            # Try to import the unit class
                                            from . import units
                                            unit_class = getattr(units, unit_name, None)
                                            if unit_class:
                                                related_kwargs['unit'] = unit_class
                                        except:
                                            pass
                                    
                                    related_instance = field_type(**related_kwargs)
                                else:
                                    # Just create with name
                                    related_instance = field_type(_name=local_name)
                                
                                instances_cache[str(field_value_uri)] = related_instance
                                kwargs[field_name] = related_instance
                    else:
                        # For primitive types, extract the value
                        value = self._get_field_value_from_uri(
                            field_value_uri,
                            field_type,
                            field_obj
                        )
                        kwargs[field_name] = value
        
        # Instantiate the object
        instance = resource_class(**kwargs)
        
        # Cache the instance
        instances_cache[entity_key] = instance
        
        return instance
    
    def load_instances(
        self,
        resource_class: Type[Resource],
        ontology: Optional[str] = None
    ) -> List[Resource]:
        """
        Load instances of a Resource class from the graph.
        
        Args:
            resource_class: The Resource class to load instances for
            ontology: Optional ontology identifier (e.g., 's223') for special handling
            
        Returns:
            List of instantiated Resource objects
        """
        # Query for instances
        df = self.query_class(resource_class, ontology=ontology)
        
        if df.empty:
            return []
        
        # Instantiate objects from results
        instances = []
        instances_cache = {}
        
        for _, row in df.iterrows():
            try:
                instance = self._instantiate_from_row(
                    resource_class,
                    row,
                    instances_cache
                )
                instances.append(instance)
            except Exception as e:
                print(f"Warning: Could not instantiate object from row: {e}")
                continue
        
        return instances
    
    def load_multiple_classes(
        self,
        class_dict: Dict[str, Type[Resource]],
        ontology: Optional[str] = None
    ) -> Dict[str, List[Resource]]:
        """
        Load instances of multiple Resource classes.
        
        Args:
            class_dict: Dictionary mapping result keys to Resource classes
                       e.g., {'spaces': Space, 'windows': Window}
            ontology: Optional ontology identifier (e.g., 's223') for special handling
            
        Returns:
            Dictionary with keys from class_dict and lists of instances as values
        """
        results = {}
        
        for result_key, resource_class in class_dict.items():
            try:
                instances = self.load_instances(resource_class, ontology=ontology)
                results[result_key] = instances
            except Exception as e:
                print(f"Warning: Could not load instances for {resource_class.__name__}: {e}")
                results[result_key] = []
        
        return results
