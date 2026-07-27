from typing import List, Optional, Tuple

from rdflib import BNode, Graph, URIRef
from rdflib.namespace import RDF, RDFS

from ..namespaces import SH
from .ir import ComplexConstraintIR, PropertyShapeIR
from .naming import field_name_for_path, field_name_for_qualified, local_name


def _literal_str(g: Graph, subject, predicate) -> Optional[str]:
    val = g.value(subject, predicate)
    return str(val) if val is not None else None


def _literal_int(g: Graph, subject, predicate) -> Optional[int]:
    val = g.value(subject, predicate)
    return int(val) if val is not None else None


def _dump_subgraph(g: Graph, bn) -> str:
    """Best-effort serialization of a blank node's reachable subgraph, for the raw_shapes sidecar."""
    sub = Graph()
    seen = set()
    frontier = [bn]
    while frontier:
        node = frontier.pop()
        if node in seen:
            continue
        seen.add(node)
        for p, o in g.predicate_objects(node):
            sub.add((node, p, o))
            if isinstance(o, BNode) and o not in seen:
                frontier.append(o)
    try:
        return sub.serialize(format='turtle')
    except Exception:
        return ''


def extract_property_shapes(
    g: Graph, class_iri: URIRef
) -> Tuple[List[PropertyShapeIR], List[ComplexConstraintIR]]:
    """Walk a class's directly-declared sh:property shapes.

    Splits them into field-generating shapes (plain sh:class/sh:datatype, or a
    qualifiedValueShape anchored by sh:class) and non-field-generating complex
    constraints (sh:sparql, top-level sh:or, forbidden maxCount=0, compound paths).
    Extra content nested inside an otherwise field-generating qualified shape is kept
    as a supplementary_note on that field rather than discarding the field.
    """
    plain_shapes: List[PropertyShapeIR] = []
    complex_constraints: List[ComplexConstraintIR] = []
    # path_local -> list of ComplexConstraintIR sharing that path (e.g. sparql
    # constraints riding along a plain shape's path), attached in a second pass.
    path_scoped_complex: dict = {}

    for bn in g.objects(class_iri, SH.property):
        path_obj = g.value(bn, SH.path)
        comment = _literal_str(g, bn, RDFS.comment)
        message = _literal_str(g, bn, SH.message)
        severity = _literal_str(g, bn, SH.severity)

        if path_obj is None or isinstance(path_obj, BNode):
            complex_constraints.append(ComplexConstraintIR(
                path_local=None, kind='inverse-path', comment=comment,
                message=message, severity=severity, raw_turtle=_dump_subgraph(g, bn),
            ))
            continue

        path_local = local_name(path_obj)
        has_sparql = (bn, SH.sparql, None) in g
        has_or = (bn, SH['or'], None) in g
        max_count = _literal_int(g, bn, SH.maxCount)
        min_count = _literal_int(g, bn, SH.minCount)

        if has_sparql or has_or:
            kind = 'sparql' if has_sparql else 'or'
            cc = ComplexConstraintIR(
                path_local=path_local, kind=kind, comment=comment, message=message,
                severity=severity, raw_turtle=_dump_subgraph(g, bn),
            )
            complex_constraints.append(cc)
            path_scoped_complex.setdefault(path_local, []).append(cc)
            continue

        if max_count == 0:
            complex_constraints.append(ComplexConstraintIR(
                path_local=path_local, kind='forbidden', comment=comment,
                message=message, severity=severity, raw_turtle=_dump_subgraph(g, bn),
            ))
            continue

        direct_class = g.value(bn, SH['class'])
        datatype = g.value(bn, SH.datatype)

        if direct_class is not None or datatype is not None:
            plain_shapes.append(PropertyShapeIR(
                path_local=path_local,
                field_name=field_name_for_path(path_local),
                target_class_local=local_name(direct_class) if direct_class is not None else None,
                datatype_local=local_name(datatype) if datatype is not None else None,
                min_count=min_count, max_count=max_count, qualified=False,
                comment=comment, message=message,
            ))
            continue

        qvs = g.value(bn, SH.qualifiedValueShape)
        if qvs is not None:
            qvs_class = g.value(qvs, SH['class'])
            if qvs_class is None:
                complex_constraints.append(ComplexConstraintIR(
                    path_local=path_local, kind='nested-node', comment=comment,
                    message=message, severity=severity, raw_turtle=_dump_subgraph(g, bn),
                ))
                continue
            qmin = _literal_int(g, bn, SH.qualifiedMinCount)
            target_local = local_name(qvs_class)
            shape = PropertyShapeIR(
                path_local=path_local,
                field_name=field_name_for_qualified(target_local),
                target_class_local=target_local, datatype_local=None,
                min_count=qmin, max_count=None, qualified=True,
                comment=comment, message=message,
            )
            extra_preds = {p for p, _ in g.predicate_objects(qvs)} - {SH['class']}
            if extra_preds:
                shape.supplementary_notes.append(ComplexConstraintIR(
                    path_local=path_local, kind='nested-node',
                    comment="Additional constraints on the qualified value beyond its class "
                            "(medium, sub-shape, etc.) - see raw_turtle.",
                    message=message, severity=severity, raw_turtle=_dump_subgraph(g, qvs),
                ))
            plain_shapes.append(shape)
            continue

        complex_constraints.append(ComplexConstraintIR(
            path_local=path_local, kind='other', comment=comment, message=message,
            severity=severity, raw_turtle=_dump_subgraph(g, bn),
        ))

    # Attach path-scoped complex constraints (e.g. sparql riding a plain shape's path)
    # as supplementary notes, and drop them from the standalone complex list so they
    # aren't double-reported.
    standalone_complex: List[ComplexConstraintIR] = []
    attached_ids = set()
    for shape in plain_shapes:
        for cc in path_scoped_complex.get(shape.path_local, []):
            shape.supplementary_notes.append(cc)
            attached_ids.add(id(cc))
    for cc in complex_constraints:
        if id(cc) not in attached_ids:
            standalone_complex.append(cc)

    # Disambiguate field names that collided (rare: two plain shapes on the same
    # path with no qualifiedValueShape, or two qualified shapes with the same target).
    seen_names = set()
    for shape in plain_shapes:
        if shape.field_name in seen_names:
            i = 2
            base = shape.field_name
            while f"{base}_{i}" in seen_names:
                i += 1
            shape.field_name = f"{base}_{i}"
        seen_names.add(shape.field_name)

    return plain_shapes, standalone_complex
