from typing import Dict, List, Set

from rdflib import Graph, URIRef

from ..namespaces import QK, RDFS
from .adapters.base import OntologyAdapter
from .config import IngestConfig
from .ir import ClassIR, OntologyIR, RelationIR
from .naming import class_name_for, local_name, make_unique
from .shacl import extract_property_shapes


class OntologyParser:
    """Ontology-agnostic walker: rdflib graph -> OntologyIR, via an adapter that
    answers the ontology-specific categorization questions (is this a class? a
    relation? abstract? which generated module does it belong in?)."""

    def __init__(self, config: IngestConfig, adapter: OntologyAdapter):
        self.config = config
        self.adapter = adapter

    def parse(self) -> OntologyIR:
        g = Graph()
        g.parse(str(self.config.source_path), format='turtle')

        subjects = {s for s in g.subjects() if isinstance(s, URIRef)}
        if not self.config.include_extension_namespaces:
            subjects = {s for s in subjects if self.adapter.in_scope(s)}

        class_subjects = [s for s in subjects if self.adapter.is_class(g, s)]
        relation_subjects = [s for s in subjects if self.adapter.is_relation(g, s) is not None]

        parent_map: Dict[URIRef, List[URIRef]] = {
            s: [p for p in g.objects(s, RDFS.subClassOf) if isinstance(p, URIRef)]
            for s in class_subjects
        }
        class_local_by_iri = {s: local_name(s) for s in class_subjects}

        def ancestry_local_names(subject: URIRef, _seen=None) -> Set[str]:
            if _seen is None:
                _seen = set()
            if subject in _seen:
                return set()
            _seen.add(subject)
            names = {local_name(subject)}
            # Parents not in parent_map (out-of-scope subjects, e.g. an s223 class an
            # extension ontology subclasses) aren't pre-walked - query the graph
            # directly so ancestry still reaches e.g. a literal `EnumerationKind`
            # root through an external namespace's hierarchy.
            parents = parent_map.get(subject)
            if parents is None:
                parents = [p for p in g.objects(subject, RDFS.subClassOf) if isinstance(p, URIRef)]
            for parent in parents:
                names |= ancestry_local_names(parent, _seen)
            return names

        scaffold_names = self.adapter.scaffold_parent_local_names()
        used_class_names: Dict[str, Set[str]] = {
            'entities': set(), 'properties': set(), 'enumerationkinds': set()
        }
        classes: Dict[str, ClassIR] = {}

        for subject in sorted(class_subjects, key=str):
            local = class_local_by_iri[subject]
            ancestry = ancestry_local_names(subject)
            bucket = self.adapter.bucket_for(g, subject, ancestry)
            python_name = make_unique(class_name_for(local), used_class_names[bucket])

            parent_local_names = []
            for p in parent_map.get(subject, []):
                p_local = local_name(p)
                if (p in class_local_by_iri or p_local in scaffold_names
                        or self.adapter.external_class_ref(p_local) is not None):
                    parent_local_names.append(p_local)
                # else: out-of-scope/meta parent (e.g. s223:Concept) - dropped, the
                # emitter falls back to the class's bucket root.

            is_enum_value = 'EnumerationKind' in ancestry and local != 'EnumerationKind'
            property_shapes, complex_constraints = extract_property_shapes(g, subject)
            label = g.value(subject, RDFS.label)
            comment = g.value(subject, RDFS.comment)

            classes[local] = ClassIR(
                iri=str(subject),
                local_name=local,
                class_name=python_name,
                label=str(label) if label is not None else None,
                comment=str(comment) if comment is not None else None,
                parent_local_names=parent_local_names,
                is_abstract=self.adapter.is_abstract(g, subject),
                is_enumeration_value=is_enum_value,
                bucket=bucket,
                property_shapes=property_shapes,
                complex_constraints=complex_constraints,
            )

        relations: Dict[str, RelationIR] = {}
        for subject in sorted(relation_subjects, key=str):
            local = local_name(subject)
            kind = self.adapter.is_relation(g, subject)
            inverse = self.adapter.get_inverse(g, subject)
            label = g.value(subject, RDFS.label)
            comment = g.value(subject, RDFS.comment)
            relations[local] = RelationIR(
                iri=str(subject),
                local_name=local,
                class_name=local,
                label=str(label) if label is not None else None,
                comment=str(comment) if comment is not None else None,
                kind=kind,
                inverse_of_local=local_name(inverse) if inverse is not None else None,
            )

        qk_prefix = str(QK)
        quantitykinds_referenced = {
            local_name(o) for _, _, o in g
            if isinstance(o, URIRef) and str(o).startswith(qk_prefix)
        }

        return OntologyIR(
            classes=classes,
            relations=relations,
            quantitykinds_referenced=quantitykinds_referenced,
            source_meta={
                'ontology_name': self.config.ontology_name,
                'source_path': str(self.config.source_path),
            },
        )
