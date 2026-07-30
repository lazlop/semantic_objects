from pathlib import Path
from typing import List, Optional

from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS

from ...namespaces import SH, WATR
from .base import OntologyAdapter
from .s223 import S223Adapter

REPO_ROOT = Path(__file__).resolve().parents[4]
S223_ONTOLOGY_PATH = REPO_ROOT / 'src' / 'semantic_objects' / 'ontologies' / 's223' / '223p.ttl'

# watr:Class is the same modeling-construct marker as s223:Class - a metaclass,
# never generated as a domain class.
META_EXCLUDE = {WATR.Class}


def _s223_reference_tables():
    """local_name -> (bucket, generated Python class name) for every already-ingested
    s223 class, plus the set of already-ingested s223 relation local names. WATR
    subclasses s223 classes (e.g. Boiler subclasses s223:Equipment) and reuses
    s223 relations (e.g. hasRole, hasConnectionPoint) directly, so its adapter
    needs to point at the *same* generated Python objects s223 already produced -
    re-parsing 223p.ttl with the s223 adapter is the simplest way to get an
    accurate local_name -> class_name mapping without duplicating s223's naming
    rules (collisions, taxonomy-leaf renaming, etc.). The bucket matters because
    s223/__init__.py flattens entities/properties/relations to top-level
    (s223.Boiler) but *not* enumerationkinds (s223.enumerationkinds.Aspect only)."""
    from ..config import IngestConfig
    from ..parser import OntologyParser

    config = IngestConfig(ontology_name='s223', source_path=S223_ONTOLOGY_PATH, output_dir=Path('.'))
    ir = OntologyParser(config, S223Adapter()).parse()
    classes = {local: (cls.bucket, cls.class_name) for local, cls in ir.classes.items()}
    # Scaffold classes hand-defined in s223/core.py, not produced by the parser
    # (s223:Class/Concept/AbstractClass are excluded there as meta markers, but
    # EnumerationKind is a real generated-and-referenceable root, flattened to
    # top-level s223.EnumerationKind like the rest of core.py's scaffold).
    classes.setdefault('EnumerationKind', ('entities', 'EnumerationKind'))
    relation_names = set(ir.relations.keys())
    return classes, relation_names


class WatrAdapter(OntologyAdapter):
    """The NAWI water treatment ontology (WATR): a s223 extension that adds
    water-treatment-specific equipment, processes, and enumeration values -
    mostly by subclassing s223 classes and reusing s223 relations directly
    rather than defining parallel ones."""

    namespace = WATR
    namespace_import_name = 'WATR'

    def __init__(self):
        self._s223_classes, self._s223_relations = _s223_reference_tables()

    def in_scope(self, iri: URIRef) -> bool:
        return str(iri).startswith(str(WATR))

    def is_class(self, g: Graph, subject: URIRef) -> bool:
        if subject in META_EXCLUDE or not self.in_scope(subject):
            return False
        # Unlike s223 (every class typed sh:NodeShape), WATR also has pure
        # organizational categories typed only rdfs:Class (e.g. watr:UnitProcess)
        # or only watr:Class (e.g. the Process-* taxonomy, punned as both a class
        # and its own sole instance for sh:hasValue/sh:class constraints).
        return ((subject, RDF.type, WATR.Class) in g
                or (subject, RDF.type, SH.NodeShape) in g
                or (subject, RDF.type, RDFS.Class) in g)

    def is_abstract(self, g: Graph, subject: URIRef) -> bool:
        # No explicit AbstractClass marker in WATR: a class with no sh:NodeShape
        # typing of its own (UnitProcess, Process-* taxonomy nodes) is a pure
        # organizational category, never meant to be directly instantiated.
        return (subject, RDF.type, SH.NodeShape) not in g

    def is_relation(self, g: Graph, subject: URIRef) -> Optional[str]:
        if not self.in_scope(subject):
            return None
        if (subject, RDF.type, RDF.Property) not in g:
            return None
        return 'Relation'  # WATR declares no inverse/symmetric relation kinds

    def get_inverse(self, g: Graph, subject: URIRef) -> Optional[URIRef]:
        return None

    def bucket_for(self, g: Graph, class_iri: URIRef, ancestry_local_names: set) -> str:
        if 'EnumerationKind' in ancestry_local_names:
            return 'enumerationkinds'
        if 'Property' in ancestry_local_names:
            return 'properties'
        # water.ttl references s223 classes by IRI without restating their own
        # parent chain (e.g. watr:Role-Feed subclasses s223:EnumerationKind-Role,
        # but 223p.ttl - where EnumerationKind-Role's own ancestry to the literal
        # EnumerationKind root lives - isn't part of this graph), so ancestry
        # walking stops one hop into s223's namespace. Consult the already-ingested
        # s223 IR for whichever bucket that ancestor landed in there.
        for name in ancestry_local_names:
            found = self._s223_classes.get(name)
            if found is not None:
                return found[0]
        return 'entities'

    def scaffold_parent_local_names(self) -> dict:
        # Hand-defined in watr/core.py; the generator references, never redefines.
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
