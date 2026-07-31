from pathlib import Path
from typing import List, Optional

from rdflib import Graph, URIRef
from rdflib.namespace import RDF

from ...namespaces import G36, S223, SH
from ..ir import ClassIR, OntologyIR
from .base import OntologyAdapter
from .s223 import META_EXCLUDE, S223Adapter

REPO_ROOT = Path(__file__).resolve().parents[4]
S223_ONTOLOGY_PATH = REPO_ROOT / 'src' / 'semantic_objects' / 'ontologies' / 's223' / '223p.ttl'


def _s223_reference_tables():
    """local_name -> (bucket, generated Python class name) for every already-ingested
    s223 class, plus the set of already-ingested s223 relation local names. g36
    subclasses s223 classes (e.g. Fan subclasses s223:Fan) and reuses s223
    relations (hasProperty, hasDomain, connectedTo, ...) directly rather than
    defining parallel ones - see WatrAdapter's identically-purposed helper."""
    from ..config import IngestConfig
    from ..parser import OntologyParser

    config = IngestConfig(ontology_name='s223', source_path=S223_ONTOLOGY_PATH, output_dir=Path('.'))
    ir = OntologyParser(config, S223Adapter()).parse()
    classes = {local: (cls.bucket, cls.class_name) for local, cls in ir.classes.items()}
    classes.setdefault('EnumerationKind', ('entities', 'EnumerationKind'))
    relation_names = set(ir.relations.keys())
    return classes, relation_names


class G36Adapter(OntologyAdapter):
    """ASHRAE Guideline 36 extension classes, vendored in the same 223p.ttl file
    as the core s223: ontology under the g36: prefix. g36: classes are typed
    exactly like s223: classes (`a s223:Class, sh:NodeShape`) and subclass an
    s223: class, adding extra `sh:property` constraints - see
    tutorial/g36-extension-tutorial.ipynb for the ontology-level walkthrough.

    g36: introduces no relations or property/enumeration-kind classes of its own;
    it only reuses s223:'s (hasProperty, hasDomain, ...) relations and s223:'s
    Property/EnumerationKind hierarchy, so this adapter delegates class-vs-relation
    categorization to a private S223Adapter wherever it needs to recognize
    something from *outside* the g36: namespace as already available rather than
    generating it a second time.
    """

    namespace = G36
    namespace_import_name = 'G36'

    def __init__(self):
        self._s223 = S223Adapter()
        self._s223_classes, self._s223_relations = _s223_reference_tables()

    def in_scope(self, iri: URIRef) -> bool:
        return str(iri).startswith(str(G36))

    def is_class(self, g: Graph, subject: URIRef) -> bool:
        if subject in META_EXCLUDE or not self.in_scope(subject):
            return False
        if (subject, RDF.type, SH.NodeShape) not in g:
            return False
        return (subject, RDF.type, S223.Class) in g or (subject, RDF.type, S223.AbstractClass) in g

    def is_abstract(self, g: Graph, subject: URIRef) -> bool:
        return (subject, RDF.type, S223.AbstractClass) in g

    def is_relation(self, g: Graph, subject: URIRef) -> Optional[str]:
        # g36 defines no relations of its own - every field on a g36 class is
        # declared via an s223: relation, surfaced through external_relation_ref().
        return None

    def get_inverse(self, g: Graph, subject: URIRef) -> Optional[URIRef]:
        return None

    def bucket_for(self, g: Graph, class_iri: URIRef, ancestry_local_names: set) -> str:
        return self._s223.bucket_for(g, class_iri, ancestry_local_names)

    def scaffold_parent_local_names(self) -> dict:
        # Hand-defined in g36/core.py; the generator references, never redefines.
        return {'Node': True, 'EnumerationKind': True, 'ExternalReference': True}

    def external_class_ref(self, local_name: str) -> Optional[str]:
        found = self._s223_classes.get(local_name)
        if found is None:
            return None
        bucket, class_name = found
        # s223/__init__.py flattens entities/properties (and core.py's scaffold) to
        # top-level, but not enumerationkinds - s223.Aspect doesn't exist, only
        # s223.enumerationkinds.Aspect.
        if bucket == 'enumerationkinds':
            return f"s223.enumerationkinds.{class_name}"
        return f"s223.{class_name}"

    def external_relation_ref(self, local_name: str) -> Optional[str]:
        return f"s223.{local_name}" if local_name in self._s223_relations else None

    def external_import_lines(self) -> List[str]:
        return ["from ... import s223"]

    def asserted_type_local(self, cls: ClassIR, ir: OntologyIR) -> Optional[str]:
        # g36 classes are never asserted as their own RDF type - see g36:XAnnotation's
        # SHACL inference rule (tutorial/g36-extension-tutorial.ipynb section 2.3).
        # Walk this class's own ancestry until the first s223 (external) ancestor
        # is found, and use *its* local_name - that's the term instances actually
        # get typed as.
        seen: set = set()

        def walk(local: str) -> Optional[str]:
            if local in seen:
                return None
            seen.add(local)
            current = ir.classes.get(local)
            if current is None:
                return None
            for parent_local in current.parent_local_names:
                if self.external_class_ref(parent_local) is not None:
                    return parent_local
                found = walk(parent_local)
                if found is not None:
                    return found
            return None

        return walk(cls.local_name)
