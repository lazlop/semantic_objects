from abc import ABC, abstractmethod
from typing import List, Optional

from rdflib import Graph, Namespace, URIRef

from ..ir import ClassIR, OntologyIR


class OntologyAdapter(ABC):
    """Ontology-specific categorization rules for the generic ingestion walker.

    Each ontology publishes its own meta-vocabulary for "this is a class" /
    "this is a relation" on top of common SHACL/RDFS constructs. Only these
    categorization questions are ontology-specific; the parser, SHACL shape
    classifier, and emitter are shared across all ontologies.
    """

    namespace: Namespace
    # Name this ontology's namespace is imported under from semantic_objects.namespaces
    # (e.g. 'S223', 'WATR') - used to generate `from ...namespaces import {name}` and
    # `_ns = {name}` in the generated relations module.
    namespace_import_name: str = 'S223'

    @abstractmethod
    def in_scope(self, iri: URIRef) -> bool:
        """Whether this IRI belongs to the ontology this adapter targets."""

    @abstractmethod
    def is_class(self, g: Graph, subject: URIRef) -> bool:
        """Whether subject should become a generated Node/Property/EnumerationKind class."""

    @abstractmethod
    def is_abstract(self, g: Graph, subject: URIRef) -> bool:
        """Whether subject should be generated with abstract = True."""

    @abstractmethod
    def is_relation(self, g: Graph, subject: URIRef) -> Optional[str]:
        """Return the relation kind ('Relation'/'RelationWithInverse'/'SymmetricRelation')
        if subject should become a generated Predicate class, else None."""

    @abstractmethod
    def get_inverse(self, g: Graph, subject: URIRef) -> Optional[URIRef]:
        """The inverse relation IRI, if any."""

    @abstractmethod
    def bucket_for(self, g: Graph, class_iri: URIRef, ancestry_local_names: set) -> str:
        """Which generated module ('entities'/'properties'/'enumerationkinds') a class belongs in."""

    @abstractmethod
    def scaffold_parent_local_names(self) -> dict:
        """Map of local_name -> True for classes already hand-defined in the domain's
        core.py scaffold (e.g. Node, EnumerationKind, ExternalReference) that the
        generator should reference but never redefine."""

    def external_class_ref(self, local_name: str) -> Optional[str]:
        """Python expression for a class defined by another, already-generated
        ontology package (e.g. an extension ontology subclassing or referencing a
        base ontology's class as a field/relation target), or None if `local_name`
        isn't such a reference. Only needed by extension-ontology adapters."""
        return None

    def external_relation_ref(self, local_name: str) -> Optional[str]:
        """Python expression for a Predicate defined by another, already-generated
        ontology package (e.g. an extension ontology reusing a base ontology's
        relation), or None if `local_name` isn't such a reference. Only needed by
        extension-ontology adapters."""
        return None

    def external_import_lines(self) -> List[str]:
        """Import statements needed to make external_class_ref/external_relation_ref
        expressions resolve at module scope, added to every generated bucket file."""
        return []

    def asserted_type_local(self, cls: ClassIR, ir: OntologyIR) -> Optional[str]:
        """local_name to render as the generated class's `_name` (the RDF term
        instances are actually asserted against), overriding the default
        local_name-vs-class_name check. Return None for standard behavior.

        Only needed by adapters whose classes are pure specializations never
        themselves asserted as their own RDF type - e.g. g36, which relies on
        SHACL annotation-property inference to apply its extra constraints to
        plain s223 instances rather than instances typed as the g36 class."""
        return None
