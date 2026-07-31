from typing import Optional

from rdflib import Graph, URIRef
from rdflib.namespace import RDF

from ...namespaces import G36, S223, SH
from .base import OntologyAdapter
from .s223 import META_EXCLUDE, S223Adapter


class G36Adapter(OntologyAdapter):
    """ASHRAE Guideline 36 extension classes, vendored in the same 223p.ttl file
    as the core s223: ontology under the g36: prefix. g36: classes are typed
    exactly like s223: classes (`a s223:Class, sh:NodeShape`) and subclass an
    s223: class, adding extra `sh:property` constraints - see
    tutorial/g36-extension-tutorial.ipynb for the ontology-level walkthrough.

    g36: introduces no relations or property/enumeration-kind classes of its own;
    it only reuses s223:'s (hasProperty, hasDomain, ...) and s223:'s Property/
    EnumerationKind hierarchy, so this adapter delegates class-vs-relation
    categorization to a private S223Adapter wherever it needs to recognize
    something from *outside* the g36: namespace as already available rather than
    generating it a second time.
    """

    namespace = G36

    def __init__(self):
        self._s223 = S223Adapter()

    def in_scope(self, iri: URIRef) -> bool:
        return str(iri).startswith(str(G36))

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
        # g36 defines no relations of its own - every field on a g36 class is
        # declared via an s223: relation, surfaced instead through
        # external_relation_local_names() below.
        return None

    def get_inverse(self, g: Graph, subject: URIRef) -> Optional[URIRef]:
        return None

    def bucket_for(self, g: Graph, class_iri: URIRef, ancestry_local_names: set) -> str:
        return self._s223.bucket_for(g, class_iri, ancestry_local_names)

    def scaffold_parent_local_names(self) -> dict:
        # g36 classes all subclass a real s223: entity or property class; none
        # need the bare Node/EnumerationKind/ExternalReference core.py roots.
        s223_entities = 'semantic_objects.s223.entities'
        s223_properties = 'semantic_objects.s223.properties'
        return {
            # entity parents (g36:X subClassOf s223:X)
            'Zone': s223_entities,
            'Fan': s223_entities,
            'Damper': s223_entities,
            'Valve': s223_entities,
            'CoolingCoil': s223_entities,
            'HeatingCoil': s223_entities,
            'ElectricResistanceElement': s223_entities,
            # property-class field targets (qualifiedValueShape sh:class)
            'EnumeratedActuatableProperty': s223_properties,
            'EnumeratedObservableProperty': s223_properties,
            'QuantifiableActuatableProperty': s223_properties,
            'QuantifiableObservableProperty': s223_properties,
        }

    def external_relation_local_names(self, g: Graph) -> set:
        from ..naming import local_name
        return {
            local_name(s) for s in g.subjects()
            if isinstance(s, URIRef) and self._s223.is_relation(g, s) is not None
        }
