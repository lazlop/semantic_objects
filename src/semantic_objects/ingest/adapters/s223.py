from typing import Optional

from rdflib import Graph, URIRef
from rdflib.namespace import RDF

from ...namespaces import S223, SH
from .base import OntologyAdapter

# Marker IRIs used as SHACL/OWL-punning meta-types by s223 itself - never generated
# as domain classes even though some are also typed sh:NodeShape.
META_EXCLUDE = {
    S223.Class,
    S223.Concept,
    S223.AbstractClass,
    S223.Relation,
    S223.RelationWithInverse,
    S223.SymmetricRelation,
}

RELATION_KINDS = (S223.RelationWithInverse, S223.SymmetricRelation, S223.Relation)


class S223Adapter(OntologyAdapter):
    namespace = S223

    def in_scope(self, iri: URIRef) -> bool:
        return str(iri).startswith(str(S223))

    def is_class(self, g: Graph, subject: URIRef) -> bool:
        if subject in META_EXCLUDE:
            return False
        if not self.in_scope(subject):
            return False
        if (subject, RDF.type, SH.NodeShape) not in g:
            return False
        return (subject, RDF.type, S223.Class) in g or (subject, RDF.type, S223.AbstractClass) in g

    def is_abstract(self, g: Graph, subject: URIRef) -> bool:
        return (subject, RDF.type, S223.AbstractClass) in g

    def is_relation(self, g: Graph, subject: URIRef) -> Optional[str]:
        if not self.in_scope(subject):
            return None
        if (subject, RDF.type, RDF.Property) not in g:
            return None
        for kind in RELATION_KINDS:
            if (subject, RDF.type, kind) in g:
                return str(kind).rsplit('#', 1)[-1]
        return None

    def get_inverse(self, g: Graph, subject: URIRef) -> Optional[URIRef]:
        return g.value(subject, S223.inverseOf)

    def bucket_for(self, g: Graph, class_iri: URIRef, ancestry_local_names: set) -> str:
        if 'EnumerationKind' in ancestry_local_names:
            return 'enumerationkinds'
        if 'Property' in ancestry_local_names:
            return 'properties'
        return 'entities'

    def scaffold_parent_local_names(self) -> dict:
        # Already hand-defined in s223/core.py; the generator references, never redefines.
        return {'Node': True, 'EnumerationKind': True, 'ExternalReference': True}
