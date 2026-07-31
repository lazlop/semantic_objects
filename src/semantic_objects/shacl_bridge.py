"""Prototype: make the live vendored SHACL graph authoritative for SPARQL/SHACL
generation, instead of re-deriving them from dataclass field metadata (the
lossy path `query.py`/`exporters.py` use today - see the architecture
investigation this resumes, `.claude/plans/i-d-like-to-push-shimmying-lecun.md`).

Deliberately independent of BuildingMOTIF: an earlier pass tried wrapping
BuildingMOTIF's `ShapeCollection`/`shape_to_query` machinery and found it
doesn't fit this ontology's authoring conventions (dual `sh:class`+`sh:node`
on one qualifiedValueShape, shape-IRI-is-class-IRI instead of a separate
`sh:targetClass`, a confirmed cardinality bug wrapping mandatory nested
constraints in `OPTIONAL`). This module walks the SHACL graph directly with
plain `rdflib` instead.

Additive and read-only with respect to the rest of the package: nothing in
`core.py`/`query.py`/`exporters.py`/`build_model.py`/`ingest/` is imported or
modified here.
"""
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Tuple

from rdflib import Graph, URIRef
from rdflib.term import Node as RDFNode

from .namespaces import RDF, RDFS, SH, bind_prefixes

ONTOLOGIES_DIR = Path(__file__).parent / "ontologies"

# Which vendored ontology source a generated class's shape lives in, keyed by
# the top-level package name under `semantic_objects` (`cls.__module__.split('.')[1]`).
# A prototype-scoped registry - a real rollout would derive this from each
# ontology's own `_generated/_meta.py::SOURCE_FILE` instead of hardcoding it here.
ONTOLOGY_SOURCES = {
    "s223": ONTOLOGIES_DIR / "s223" / "223p.ttl",
    "watr": ONTOLOGIES_DIR / "watr" / "water.ttl",
}


@lru_cache(maxsize=None)
def get_shape_graph(source_path: Path) -> Graph:
    """Load+cache a vendored ontology .ttl as an rdflib Graph, keyed by path."""
    g = Graph()
    bind_prefixes(g)
    g.parse(str(source_path), format="turtle")
    return g


def source_path_for_class(cls) -> Path:
    # Respect the same _semantic_type escape hatch shape_iri() does: an
    # extension class (e.g. a test-local or notebook-local subclass) may not
    # live under a registered ontology package's module path at all - resolve
    # the source ontology from whichever class actually owns the shape.
    semantic_type = getattr(cls, "_semantic_type", None)
    source = semantic_type if semantic_type is not None else cls
    module_parts = source.__module__.split(".")
    top_package = module_parts[1] if len(module_parts) > 1 else None
    if top_package not in ONTOLOGY_SOURCES:
        raise ValueError(
            f"No vendored ontology source registered for package {top_package!r} "
            f"(class {cls.__name__}) - add it to shacl_bridge.ONTOLOGY_SOURCES"
        )
    return ONTOLOGY_SOURCES[top_package]


def shape_iri(cls) -> URIRef:
    """Resolve the IRI of the SHACL shape that describes `cls`.

    Respects the `_semantic_type` escape hatch: a hand-written class that pins
    fields to fixed values purely as a Python-level convenience (not a real
    ontology class of its own, e.g. `properties.Area`) sets `_semantic_type` to
    the real ontology class whose shape should be resolved instead. This is the
    actual fix for the class of crash `exporters.py` hits on fields like
    `QuantifiableObservableProperty.value: float` (`_get_iri()` called on a
    bare Python type) - `shacl_bridge` never calls `_get_iri()` on a field's
    Python type at all, since it never looks at dataclass fields to build SHACL.
    """
    semantic_type = getattr(cls, "_semantic_type", None)
    source = semantic_type if semantic_type is not None else cls
    return source._get_iri()


def _ancestor_shape_iris(g: Graph, iri: URIRef) -> List[URIRef]:
    """`iri` plus everything reachable via rdfs:subClassOf*, nearest-first.
    223p.ttl/water.ttl use "the class IRI is the shape IRI" - no separate
    sh:targetClass - so a plain rdfs:subClassOf walk on the class node finds
    every ancestor shape directly, without BuildingMOTIF's `get_shapes_about_class`
    (which assumes a separate sh:targetClass and doesn't match this convention).
    """
    seen = [iri]
    frontier = [iri]
    while frontier:
        node = frontier.pop(0)
        for parent in g.objects(node, RDFS.subClassOf):
            if isinstance(parent, URIRef) and parent not in seen:
                seen.append(parent)
                frontier.append(parent)
    return seen


def own_and_inherited_shape_graph(cls, include_hierarchy: bool = False) -> Graph:
    """The concise bounded description (own triples + reachable blank-node
    subgraph) of cls's shape, optionally unioned with every ancestor's."""
    source_graph = get_shape_graph(source_path_for_class(cls))
    iri = shape_iri(cls)
    iris = _ancestor_shape_iris(source_graph, iri) if include_hierarchy else [iri]

    out = Graph()
    bind_prefixes(out)
    for shape_iri_ in iris:
        out += source_graph.cbd(shape_iri_)
    return out


def shacl_definition_for(cls, include_hierarchy: bool = False) -> str:
    """Serialize the live SHACL shape for cls - no re-derivation, so nested and
    inherited constraints are never lost, and nothing here can hit the
    `field_obj.type._get_iri()`-on-a-bare-type crash `exporters.py` has,
    because no dataclass field is ever consulted."""
    g = own_and_inherited_shape_graph(cls, include_hierarchy=include_hierarchy)
    return g.serialize(format="turtle")


# --------------------------------------------------------------------------
# Hand-rolled SHACL -> SPARQL. Scoped to the constructs actually present in
# the prototype targets (s223:Pump, watr:Reactor/Tank) rather than a general
# SHACL-to-SPARQL compiler: sh:class/sh:datatype (plain shapes),
# sh:qualifiedValueShape (with sh:class, optionally wrapped in sh:node or with
# sh:property/sh:not directly on it), nested sh:hasValue/sh:in/sh:or/sh:class,
# and sh:sparql/other-unrecognized shapes are skipped (not representable as
# triple patterns, same as ingest/shacl.py's ComplexConstraintIR treatment).
# --------------------------------------------------------------------------


class _VarMinter:
    """Mint readable, unique SPARQL variable names, disambiguating multiple
    property shapes that share one path (e.g. watr:Tank has *four* separate
    qualifiedValueShapes all on hasConnectionPoint - drain outlet, plain
    outlet, overflow outlet, inlet) by the qualified target class and then,
    if still colliding, by a fingerprint of the nested constraints."""

    def __init__(self):
        self._used = set()

    def mint(self, *parts: str) -> str:
        base = "_".join(p for p in parts if p)
        name = base
        i = 2
        while name in self._used:
            name = f"{base}_{i}"
            i += 1
        self._used.add(name)
        return f"?{name}"


def _local_name(term: RDFNode) -> str:
    s = str(term)
    return s.rsplit("#", 1)[-1].rsplit("/", 1)[-1]


class _Prefixer:
    """Tracks which namespaces were actually used, so the generated query only
    declares the PREFIX lines it needs (mirrors query.py's existing pattern)."""

    def __init__(self, g: Graph):
        self.g = g
        self.used = set()

    def __call__(self, term: RDFNode) -> str:
        if not isinstance(term, URIRef):
            return term.n3()
        try:
            prefix, ns, local = self.g.compute_qname(term)
            self.used.add(ns)
            return f"{prefix}:{local}"
        except Exception:
            return f"<{term}>"

    def prefix_block(self) -> str:
        lines = []
        for prefix, ns in self.g.namespaces():
            if ns in self.used:
                lines.append(f"PREFIX {prefix}: <{ns}>")
        return "\n".join(lines)

    def type_triple(self, var: str, class_term: RDFNode) -> str:
        """`sh:class`/`sh:or` alternatives describe "is-a", which real (non-
        reasoned) RDF data satisfies two different ways depending on the kind
        of value: a genuine instance has a separate `rdf:type` triple to a
        (possibly more specific) class, e.g. an `OutletConnectionPoint` has no
        separate `a s223:ConnectionPoint` triple unless a reasoner added one -
        so matching a superclass needs `rdf:type/rdfs:subClassOf*`. But this
        ontology's EnumerationKind values (e.g. `s223:Fluid-Water`) are used
        directly as individuals with *no* rdf:type triple at all - the class
        IRI doubles as the instance (confirmed against real vendored data, not
        just the ontology's own text) - so matching those needs
        `rdfs:subClassOf*` applied to the value itself, skipping rdf:type.
        `rdf:type?/rdfs:subClassOf*` (optional rdf:type hop, then zero-or-more
        subClassOf hops) covers both in one path, without a UNION."""
        self.used.add(RDFS)
        self.used.add(RDF)
        target = class_term if class_term.startswith("?") else self(class_term)
        return f"{var} rdf:type?/rdfs:subClassOf* {target} ."


def _is_mandatory(g: Graph, bn, count_predicate) -> bool:
    count = g.value(bn, count_predicate)
    if count is None or int(count) < 1:
        return False
    # A shape with non-default severity (sh:Warning/sh:Info) is advisory - the
    # ontology is stating "should have" not "must have", so a query for
    # candidate instances shouldn't filter out instances that omit it. This is
    # a deliberate, principled choice (unlike BuildingMOTIF ShapeCollection's
    # confirmed bug of *always* wrapping qualified shapes in OPTIONAL regardless
    # of what the ontology actually says).
    severity = g.value(bn, SH.severity)
    if severity is not None and severity != SH.Violation:
        return False
    return True


def _emit_nested_property(g: Graph, prefixed, subject_var: str, nested_bn, minter: _VarMinter) -> Tuple[List[str], List[str]]:
    """Translate one nested `sh:property` shape (hasValue/in/class/or) rooted
    at `subject_var` into (triples, filters)."""
    path = g.value(nested_bn, SH.path)
    if path is None or not isinstance(path, URIRef):
        return [], []
    ppath = prefixed(path)

    has_value = g.value(nested_bn, SH.hasValue)
    if has_value is not None:
        return [f"{subject_var} {ppath} {prefixed(has_value)} ."], []

    in_list = g.value(nested_bn, SH["in"])
    if in_list is not None:
        var = minter.mint(subject_var.lstrip("?"), _local_name(path))
        values = [prefixed(v) for v in g.items(in_list)]
        return (
            [f"{subject_var} {ppath} {var} ."],
            [f"FILTER({var} IN ({', '.join(values)}))"],
        )

    or_list = g.value(nested_bn, SH["or"])
    if or_list is not None:
        alt_classes = [prefixed(g.value(alt, SH["class"])) for alt in g.items(or_list)
                        if g.value(alt, SH["class"]) is not None]
        if alt_classes:
            var = minter.mint(subject_var.lstrip("?"), _local_name(path))
            type_var = f"{var}_type"
            return (
                [f"{subject_var} {ppath} {var} .", prefixed.type_triple(var, type_var)],
                [f"FILTER({type_var} IN ({', '.join(alt_classes)}))"],
            )
        return [], []

    direct_class = g.value(nested_bn, SH["class"])
    if direct_class is not None:
        var = minter.mint(subject_var.lstrip("?"), _local_name(path))
        return [f"{subject_var} {ppath} {var} .", prefixed.type_triple(var, direct_class)], []

    return [], []


def _emit_qualified_shape(g: Graph, prefixed, path: URIRef, bn, minter: _VarMinter) -> Optional[str]:
    qvs = g.value(bn, SH.qualifiedValueShape)
    qvs_class = g.value(qvs, SH["class"])
    if qvs_class is None:
        return None  # nested-node with no class anchor - can't safely bind a type, skip (matches ir.py)

    triples = []
    filters = []

    var = minter.mint(_local_name(path), _local_name(qvs_class))
    triples.append(f"?name {prefixed(path)} {var} .")
    triples.append(prefixed.type_triple(var, qvs_class))

    # Some qualifiedValueShapes put nested sh:property directly on the shape
    # (watr:Tank/Reactor); others wrap it in sh:node (s223:Pump) - handle both.
    nested_source = g.value(qvs, SH.node)
    for source in filter(None, [nested_source, qvs]):
        for nested_bn in g.objects(source, SH.property):
            t, f = _emit_nested_property(g, prefixed, var, nested_bn, minter)
            triples.extend(t)
            filters.extend(f)

    # sh:not wraps a shape (typically itself a sh:property) to state "must NOT
    # match this" (e.g. watr:Tank's plain outlet excludes the drain role) -
    # translate to FILTER NOT EXISTS over that inner shape's own triples.
    for not_shape in g.objects(qvs, SH["not"]):
        for nested_bn in g.objects(not_shape, SH.property):
            t, _f = _emit_nested_property(g, prefixed, var, nested_bn, minter)
            if t:
                filters.append(f"FILTER NOT EXISTS {{ {' '.join(t)} }}")

    fragment = "\n".join(triples + filters)
    mandatory = _is_mandatory(g, bn, SH.qualifiedMinCount)
    return fragment if mandatory else f"OPTIONAL {{ {fragment} }}"


def _emit_plain_shape(g: Graph, prefixed, path: URIRef, bn, minter: _VarMinter) -> str:
    var = minter.mint(_local_name(path))
    triples = [f"?name {prefixed(path)} {var} ."]
    direct_class = g.value(bn, SH["class"])
    if direct_class is not None:
        triples.append(prefixed.type_triple(var, direct_class))
    fragment = "\n".join(triples)
    return fragment if _is_mandatory(g, bn, SH.minCount) else f"OPTIONAL {{ {fragment} }}"


def sparql_query_for(cls) -> str:
    """Generate a SPARQL query for instances of `cls` by walking the live
    SHACL shape graph directly - always includes inherited constraints
    (matching how a Python subclass's `__dataclass_fields__` already
    accumulates its parents' fields today)."""
    g = own_and_inherited_shape_graph(cls, include_hierarchy=True)
    prefixed = _Prefixer(g)
    minter = _VarMinter()
    minter._used.add("name")

    fragments = [f"?name a {prefixed(shape_iri(cls))} ."]

    for ancestor_iri in _ancestor_shape_iris(g, shape_iri(cls)):
        for bn in g.objects(ancestor_iri, SH.property):
            path = g.value(bn, SH.path)
            if path is None or not isinstance(path, URIRef):
                continue  # inverse-path expression - not representable, skip (matches ir.py)
            if (bn, SH.sparql, None) in g:
                continue  # sh:sparql constraint - not a triple pattern, skip
            max_count = g.value(bn, SH.maxCount)
            if max_count is not None and int(max_count) == 0:
                continue  # forbidden-property shape - nothing to bind, skip

            if g.value(bn, SH.qualifiedValueShape) is not None:
                fragment = _emit_qualified_shape(g, prefixed, path, bn, minter)
                if fragment:
                    fragments.append(fragment)
            elif g.value(bn, SH["class"]) is not None or g.value(bn, SH.datatype) is not None:
                fragments.append(_emit_plain_shape(g, prefixed, path, bn, minter))
            # else: unrecognized shape shape (e.g. sh:or at the top level with
            # no qualifiedValueShape) - not representable, skip.

    where = "\n".join(fragments)
    return f"{prefixed.prefix_block()}\nSELECT DISTINCT * WHERE {{\n{where}\n}}"
