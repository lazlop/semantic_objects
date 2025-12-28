"""
Module for generating SHACL annotation rules and running inference on RDF graphs.

This module provides functionality to:
1. Generate SHACL annotation rules from semantic object classes
2. Run SHACL inference to add type annotations to RDF graphs
"""

from typing import List, Type, Optional, Union
from rdflib import Graph, Literal, URIRef, Namespace
from warnings import warn

from .core import Resource, Node, Predicate
from .namespaces import RDF, RDFS, SH, PARAM, HPFS, bind_prefixes
from .discovery import get_related_classes, get_module_classes

try:
    from brick_tq_shacl.topquadrant_shacl import infer
    HAS_TQ_SHACL = True
except ImportError:
    HAS_TQ_SHACL = False
    warn("brick_tq_shacl not available. Inference functionality will be limited.")


class AnnotationRuleGenerator:
    """
    Generates SHACL annotation rules from semantic object classes.
    
    Annotation rules use SHACL TripleRule to infer RDF types based on
    the structure of instances in the data graph.
    """
    
    def __init__(self):
        """Initialize the annotation rule generator."""
        self.shapes_graph = Graph()
        bind_prefixes(self.shapes_graph)
    
    def generate_annotation_rules(
        self, 
        classes: Union[Type[Resource], List[Type[Resource]], List]
    ) -> Graph:
        """
        Generate SHACL annotation rules for the given classes.
        
        Args:
            classes: A single class, list of classes, or list of modules containing classes
            
        Returns:
            Graph containing SHACL annotation rules
        """
        # Normalize input to list of classes
        if isinstance(classes, type) and issubclass(classes, Resource):
            class_list = [classes]
        elif isinstance(classes, list):
            # Check if it's a list of modules or classes
            if classes and hasattr(classes[0], '__dict__') and not isinstance(classes[0], type):
                # It's a list of modules
                _, entity_list, _ = get_module_classes(classes)
                class_list = entity_list
            else:
                # It's a list of classes
                class_list = classes
        else:
            raise ValueError("classes must be a Resource class, list of classes, or list of modules")
        
        # Generate rules for each class
        for cls in class_list:
            if not isinstance(cls, type) or not issubclass(cls, Resource):
                continue
            
            # Skip abstract classes
            if hasattr(cls, 'abstract') and cls.abstract:
                continue
            
            # Only generate rules for Node subclasses (entities)
            if not issubclass(cls, Node):
                continue
            
            self._generate_class_annotation_rule(cls)
        
        return self.shapes_graph
    
    def _generate_class_annotation_rule(self, cls: Type[Node]) -> None:
        """
        Generate a SHACL annotation rule for a single class.
        
        The rule uses TripleRule to add an rdf:type triple when an instance
        matches the class's structure (defined by its SHACL shape).
        
        Args:
            cls: The class to generate an annotation rule for
        """
        class_name = cls.__name__
        
        # Skip classes without _ns attribute (like NamedNode)
        if not hasattr(cls, '_ns'):
            return
        
        try:
            class_iri = cls._get_iri()
        except Exception:
            # Skip classes that can't generate an IRI
            return
        
        # Create the annotation shape
        annotation_shape = HPFS[f"{class_name}Annotation"]
        self.shapes_graph.add((annotation_shape, RDF.type, SH.NodeShape))
        
        # Get the main RDF type(s) for this class
        # This is typically the ontology class it represents
        main_types = self._get_class_types(cls)
        
        if not main_types:
            warn(f"No RDF types found for {class_name}, skipping annotation rule")
            return
        
        # Use the first type as the target class for the annotation
        main_type = main_types[0]
        self.shapes_graph.add((annotation_shape, SH.targetClass, main_type))
        
        # Create the annotation rule
        rule_iri = HPFS[f"{class_name}AnnotationRule"]
        self.shapes_graph.add((annotation_shape, SH.rule, rule_iri))
        self.shapes_graph.add((rule_iri, RDF.type, SH.TripleRule))
        
        # The rule adds: ?this rdf:type <ClassIRI>
        self.shapes_graph.add((rule_iri, SH.subject, SH.this))
        self.shapes_graph.add((rule_iri, SH.predicate, RDF.type))
        self.shapes_graph.add((rule_iri, SH.object, class_iri))
        
        # The condition is that the instance conforms to the class's shape
        self.shapes_graph.add((rule_iri, SH.condition, class_iri))
    
    def _get_class_types(self, cls: Type[Resource]) -> List[URIRef]:
        """
        Get the RDF types that instances of this class should have.
        
        This looks for explicit type declarations in the class or infers
        them from the class hierarchy.
        
        Args:
            cls: The class to get types for
            
        Returns:
            List of URIRef representing RDF types
        """
        types = []
        
        # Check if the class has an explicit _rdf_type attribute
        if hasattr(cls, '_rdf_type'):
            rdf_type = cls._rdf_type
            if isinstance(rdf_type, (URIRef, str)):
                types.append(URIRef(rdf_type) if isinstance(rdf_type, str) else rdf_type)
            elif isinstance(rdf_type, list):
                types.extend([URIRef(t) if isinstance(t, str) else t for t in rdf_type])
        
        # If no explicit type, try to infer from namespace and class name
        if not types and hasattr(cls, '_ns'):
            types.append(cls._ns[cls.__name__])
        
        return types
    
    def save_shapes(self, filename: str, format: str = "turtle") -> None:
        """
        Save the annotation rules graph to a file.
        
        Args:
            filename: Output file path
            format: RDF serialization format (default: "turtle")
        """
        self.shapes_graph.serialize(filename, format=format)


class InferenceEngine:
    """
    Runs SHACL inference on RDF graphs using annotation rules.
    """
    
    def __init__(self, annotation_rules: Optional[Graph] = None):
        """
        Initialize the inference engine.
        
        Args:
            annotation_rules: Optional graph containing SHACL annotation rules.
                            If None, rules must be provided when calling infer().
        """
        self.annotation_rules = annotation_rules
    
    def infer(
        self, 
        data_graph: Graph, 
        annotation_rules: Optional[Graph] = None,
        use_tq_shacl: bool = True
    ) -> Graph:
        """
        Run SHACL inference on a data graph.
        
        Args:
            data_graph: The RDF graph to run inference on
            annotation_rules: Optional SHACL rules graph. If None, uses the
                            rules provided during initialization.
            use_tq_shacl: If True, use TopQuadrant SHACL engine (requires
                         brick_tq_shacl). If False, use pyshacl (limited support).
        
        Returns:
            The data graph with inferred triples added
            
        Raises:
            ValueError: If no annotation rules are available
            ImportError: If use_tq_shacl=True but brick_tq_shacl is not installed
        """
        rules = annotation_rules or self.annotation_rules
        
        if rules is None:
            raise ValueError(
                "No annotation rules available. Provide rules during initialization "
                "or as a parameter to infer()."
            )
        
        if use_tq_shacl:
            if not HAS_TQ_SHACL:
                raise ImportError(
                    "brick_tq_shacl is required for TopQuadrant SHACL inference. "
                    "Install it with: pip install brick-tq-shacl"
                )
            return infer(data_graph, rules)
        else:
            # Fallback to pyshacl (limited support for SHACL rules)
            warn(
                "pyshacl has limited support for SHACL rules. "
                "Consider installing brick_tq_shacl for full functionality."
            )
            try:
                from pyshacl import validate
                # pyshacl's validate doesn't directly support inference,
                # but we can use it for validation
                conforms, results_graph, results_text = validate(
                    data_graph,
                    shacl_graph=rules,
                    inference='rdfs',
                    abort_on_first=False,
                )
                return data_graph
            except ImportError:
                raise ImportError(
                    "pyshacl is required for SHACL validation. "
                    "Install it with: pip install pyshacl"
                )


def generate_annotation_rules(
    classes: Union[Type[Resource], List[Type[Resource]], List]
) -> Graph:
    """
    Convenience function to generate SHACL annotation rules.
    
    Args:
        classes: A single class, list of classes, or list of modules
        
    Returns:
        Graph containing SHACL annotation rules
        
    Example:
        >>> from semantic_objects.s223 import entities, properties
        >>> rules = generate_annotation_rules([entities, properties])
        >>> rules.serialize('annotation_rules.ttl', format='turtle')
    """
    generator = AnnotationRuleGenerator()
    return generator.generate_annotation_rules(classes)


def infer_types(
    data_graph: Graph,
    classes: Optional[Union[Type[Resource], List[Type[Resource]], List]] = None,
    annotation_rules: Optional[Graph] = None,
    use_tq_shacl: bool = True
) -> Graph:
    """
    Convenience function to run type inference on a data graph.
    
    Args:
        data_graph: The RDF graph to run inference on
        classes: Classes or modules to generate rules from (if annotation_rules not provided)
        annotation_rules: Pre-generated SHACL annotation rules
        use_tq_shacl: Whether to use TopQuadrant SHACL engine
        
    Returns:
        The data graph with inferred types added
        
    Example:
        >>> from semantic_objects.s223 import entities, properties
        >>> from rdflib import Graph
        >>> 
        >>> data = Graph()
        >>> data.parse('building_data.ttl', format='turtle')
        >>> 
        >>> # Infer types based on structure
        >>> inferred_data = infer_types(data, classes=[entities, properties])
    """
    if annotation_rules is None:
        if classes is None:
            raise ValueError(
                "Either 'classes' or 'annotation_rules' must be provided"
            )
        annotation_rules = generate_annotation_rules(classes)
    
    engine = InferenceEngine(annotation_rules)
    return engine.infer(data_graph, use_tq_shacl=use_tq_shacl)
