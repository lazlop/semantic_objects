from abc import ABC, abstractmethod
from typing import Optional

from rdflib import Graph, Namespace, URIRef


class OntologyAdapter(ABC):
    """Ontology-specific categorization rules for the generic ingestion walker.

    Each ontology publishes its own meta-vocabulary for "this is a class" /
    "this is a relation" on top of common SHACL/RDFS constructs. Only these
    categorization questions are ontology-specific; the parser, SHACL shape
    classifier, and emitter are shared across all ontologies.
    """

    namespace: Namespace

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
