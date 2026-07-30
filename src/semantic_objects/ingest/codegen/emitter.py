import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from pprint import pformat
from typing import Dict, List, Optional, Tuple

from ..adapters.base import OntologyAdapter
from ..ir import ClassIR, ComplexConstraintIR, OntologyIR, PropertyShapeIR
from .templates import GENERATED_HEADER

DATATYPE_MAP = {
    'boolean': 'bool', 'string': 'str', 'integer': 'int', 'int': 'int',
    'decimal': 'float', 'double': 'float', 'float': 'float',
    'dateTime': 'str', 'date': 'str', 'anyURI': 'str',
}

# Non-s223 classes with a hand-authored home elsewhere in the package.
QUDT_KNOWN = {'Unit': 'Unit', 'QuantityKind': 'QuantityKind'}

BUCKET_ORDER = ['enumerationkinds', 'properties', 'entities']
BUCKET_ROOT = {'enumerationkinds': 'EnumerationKind', 'properties': 'Node', 'entities': 'Node'}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _same_bucket_deps(cls: ClassIR, by_local: dict) -> List[str]:
    """Same-bucket classes that must be defined before cls: parent classes, plus
    any field/_valid_relations target type referenced from this bucket (field type
    annotations are evaluated immediately, not deferred, so definition order matters)."""
    deps = [p for p in cls.parent_local_names if p in by_local]
    for shape in cls.property_shapes:
        if shape.target_class_local and shape.target_class_local in by_local:
            deps.append(shape.target_class_local)
    return deps


def _topo_order(classes_in_bucket: List[ClassIR]) -> List[ClassIR]:
    """Cycle-safe DFS post-order. A genuine circular same-bucket dependency (rare)
    has its back-edge dropped so the sort still terminates; the emitter separately
    verifies each reference lands at an earlier position and drops any that don't,
    rather than emitting a NameError-causing forward reference."""
    by_local = {c.local_name: c for c in classes_in_bucket}
    state: Dict[str, str] = {}
    order: List[str] = []

    def visit(local: str):
        if state.get(local) in ('visiting', 'done'):
            return
        state[local] = 'visiting'
        for dep_local in _same_bucket_deps(by_local[local], by_local):
            visit(dep_local)
        state[local] = 'done'
        order.append(local)

    for local in sorted(by_local.keys()):
        visit(local)
    return [by_local[local] for local in order]


class Emitter:
    """OntologyIR -> deterministic, header-stamped .py source under s223/_generated/."""

    def __init__(self, ir: OntologyIR, scaffold_names: dict, source_path: Path, output_dir: Path,
                 ontology_name: str, adapter: Optional[OntologyAdapter] = None):
        self.ir = ir
        self.scaffold_names = scaffold_names
        self.source_path = source_path
        self.output_dir = output_dir
        self.ontology_name = ontology_name
        self.adapter = adapter
        self.unresolved_notes: Dict[str, List[dict]] = {}
        self.raw_shapes: Dict[str, List[dict]] = {}
        self._bucket_positions: Dict[str, Dict[str, int]] = {}

    # -- cross-ontology reference helpers ------------------------------------------

    def _relation_ref(self, path_local: str) -> Optional[str]:
        """`relations.X` for a relation defined by this ontology, or an adapter-supplied
        external expression (e.g. `s223.hasConnectionPoint`) for one reused from an
        already-generated base ontology. None if path_local isn't a known relation."""
        if path_local in self.ir.relations:
            return f"relations.{path_local}"
        if self.adapter is not None:
            return self.adapter.external_relation_ref(path_local)
        return None

    def _external_class_ref(self, local: str) -> Optional[str]:
        if self.adapter is None:
            return None
        return self.adapter.external_class_ref(local)

    # -- type/relation resolution -------------------------------------------------

    def _resolve_type_ref(self, shape: PropertyShapeIR, current_bucket: str,
                           current_local: str, prior_buckets: List[str]) -> Optional[Tuple[str, bool]]:
        if shape.datatype_local is not None:
            return DATATYPE_MAP.get(shape.datatype_local, 'str'), False
        target = shape.target_class_local
        if target is None:
            return None
        if target == current_local:
            return 'Self', True  # resolved at use-time by _infer_relation_for_field, not import-time
        if target in self.scaffold_names:
            return target, True
        if target in self.ir.classes:
            cls = self.ir.classes[target]
            if cls.bucket == current_bucket:
                positions = self._bucket_positions.get(current_bucket, {})
                if positions.get(target, -1) >= positions.get(current_local, -1):
                    return None  # would be a forward reference within the same file
                return cls.class_name, True
            if cls.bucket in prior_buckets:
                return f"{cls.bucket}.{cls.class_name}", True
            return None  # forward reference to a not-yet-loaded bucket
        if target in QUDT_KNOWN:
            return QUDT_KNOWN[target], True
        ext = self._external_class_ref(target)
        if ext is not None:
            return ext, True
        return None

    def _transitive_ancestor_locals(self, local: str, _seen: Optional[set] = None) -> set:
        """Ancestor local names reachable by walking parent_local_names within this
        ontology's own IR. External/base-ontology parents are leaves here (we don't
        have their hierarchy loaded) - that's fine, this only needs to detect
        same-ontology redundant multi-parent declarations, e.g. `Thickener`
        subclassing both `s223:Equipment` and `watr:UnitProcess` directly even
        though `UnitProcess` already subclasses `Equipment`."""
        if _seen is None:
            _seen = set()
        cls = self.ir.classes.get(local)
        if cls is None or local in _seen:
            return set()
        _seen.add(local)
        ancestors = set(cls.parent_local_names)
        for p in cls.parent_local_names:
            ancestors |= self._transitive_ancestor_locals(p, _seen)
        return ancestors

    def _ordered_parent_locals(self, cls: ClassIR) -> List[str]:
        """Direct parents, most-derived first. A class can declare a parent *and*
        one of that parent's own ancestors directly (redundant but valid RDFS,
        e.g. `Thickener rdfs:subClassOf s223:Equipment, watr:UnitProcess` where
        UnitProcess already subclasses Equipment) - Python's C3 linearization
        rejects that ordering unless the more-derived parent is listed first."""
        remaining = list(dict.fromkeys(cls.parent_local_names))
        ancestors_of = {p: self._transitive_ancestor_locals(p) for p in remaining}
        ordered = []
        while remaining:
            for p in remaining:
                if not any(p in ancestors_of[q] for q in remaining if q != p):
                    ordered.append(p)
                    remaining.remove(p)
                    break
            else:
                ordered.extend(remaining)  # cycle - shouldn't happen for a DAG
                break
        return ordered

    def _note_unresolved(self, class_name: str, shape_or_cc, reason: str):
        self.unresolved_notes.setdefault(class_name, []).append({
            'reason': reason,
            'path': getattr(shape_or_cc, 'path_local', None),
            'field_name': getattr(shape_or_cc, 'field_name', None),
            'target_class_local': getattr(shape_or_cc, 'target_class_local', None),
        })

    # -- per-class rendering --------------------------------------------------

    def _render_class(self, cls: ClassIR, prior_buckets: List[str]) -> str:
        parents = []
        for p_local in self._ordered_parent_locals(cls):
            # A parent local_name identical to cls's own local_name is never a
            # genuine self-inheritance edge - it's a same-named external class an
            # extension ontology reuses (e.g. watr's own "Valve" taxonomy leaf
            # subclassing s223:Valve). Route it to the external adapter instead of
            # the ir.classes lookup below, which would otherwise resolve back to
            # cls itself since ir.classes is keyed by local_name, not IRI.
            if p_local != cls.local_name and p_local in self.scaffold_names:
                parents.append(p_local)
            elif p_local != cls.local_name and p_local in self.ir.classes:
                p_cls = self.ir.classes[p_local]
                if p_cls.bucket == cls.bucket:
                    parents.append(p_cls.class_name)
                elif p_cls.bucket in prior_buckets:
                    parents.append(f"{p_cls.bucket}.{p_cls.class_name}")
            else:
                ext = self._external_class_ref(p_local)
                if ext is not None:
                    parents.append(ext)
        if not parents:
            parents = [BUCKET_ROOT[cls.bucket]]

        lines = [f"@semantic_object", f"class {cls.class_name}({', '.join(parents)}):"]
        body_lines = []
        if cls.label:
            body_lines.append(f"    label = {cls.label!r}")
        if cls.comment:
            body_lines.append(f"    comment = {cls.comment!r}")
        if cls.is_abstract:
            body_lines.append("    abstract = True")
        if cls.local_name != cls.class_name:
            body_lines.append(f"    _name = {cls.local_name!r}")

        field_shapes: List[PropertyShapeIR] = []
        valid_relation_entries: List[str] = []
        raw_entries: List[dict] = []

        for shape in cls.property_shapes:
            relation_ref = self._relation_ref(shape.path_local)
            relation_available = relation_ref is not None
            ref = (self._resolve_type_ref(shape, cls.bucket, cls.local_name, prior_buckets)
                   if relation_available else None)
            if ref is None:
                reason = 'relation-out-of-scope' if not relation_available else 'unresolved-target'
                self._note_unresolved(cls.class_name, shape, reason)
                raw_entries.append({
                    'field_name': shape.field_name, 'path': shape.path_local, 'kind': reason,
                    'target_class_local': shape.target_class_local, 'datatype_local': shape.datatype_local,
                    'qualified': shape.qualified, 'min_count': shape.min_count, 'max_count': shape.max_count,
                    'comment': shape.comment,
                })
                continue

            is_dedicated_field = shape.qualified or (shape.min_count is not None and shape.min_count >= 1)
            if is_dedicated_field:
                field_shapes.append(shape)
            else:
                type_str, _ = ref
                valid_relation_entries.append(f"({relation_ref}, {type_str})")

            for note in shape.supplementary_notes:
                raw_entries.append({
                    'field_name': shape.field_name, 'path': note.path_local, 'kind': note.kind,
                    'comment': note.comment, 'message': note.message, 'raw_turtle': note.raw_turtle,
                })

        for cc in cls.complex_constraints:
            raw_entries.append({
                'field_name': None, 'path': cc.path_local, 'kind': cc.kind,
                'comment': cc.comment, 'message': cc.message, 'raw_turtle': cc.raw_turtle,
            })

        if raw_entries:
            self.raw_shapes[cls.class_name] = raw_entries
            body_lines.append(
                f"    # {len(raw_entries)} SHACL constraint(s) not represented above - "
                f"see _raw_shapes.RAW_SHAPES[{cls.class_name!r}]"
            )

        for shape in field_shapes:
            type_str, _ = self._resolve_type_ref(shape, cls.bucket, cls.local_name, prior_buckets)
            relation_ref = self._relation_ref(shape.path_local)
            min_ = shape.min_count if shape.min_count is not None else 0
            max_repr = repr(shape.max_count)
            body_lines.append(
                f"    {shape.field_name}: {type_str} = required_field("
                f"relation={relation_ref}, min={min_}, max={max_repr}, "
                f"qualified={shape.qualified!r})"
            )

        if valid_relation_entries:
            body_lines.append(f"    _valid_relations = [{', '.join(valid_relation_entries)}]")

        if not body_lines:
            body_lines.append("    pass")

        lines.extend(body_lines)
        return "\n".join(lines) + "\n\n"

    # -- module rendering -------------------------------------------------------

    def _header(self) -> str:
        return GENERATED_HEADER.format(
            source_path=str(self.source_path),
            sha256=_sha256(self.source_path),
            generated_at=datetime.now(timezone.utc).isoformat(),
            ontology_name=self.ontology_name,
        )

    def _render_bucket(self, bucket: str, prior_buckets: List[str]) -> str:
        classes = _topo_order([c for c in self.ir.classes.values() if c.bucket == bucket])
        self._bucket_positions[bucket] = {c.local_name: i for i, c in enumerate(classes)}
        needed_imports = {b for c in classes for p in c.parent_local_names
                           if p in self.ir.classes and self.ir.classes[p].bucket in prior_buckets}
        for c in classes:
            for shape in c.property_shapes:
                if shape.target_class_local and shape.target_class_local in self.ir.classes:
                    tb = self.ir.classes[shape.target_class_local].bucket
                    if tb in prior_buckets:
                        needed_imports.add(tb)

        parts = [self._header()]
        parts.append("from typing import Self")
        parts.append("from ...core import *")
        parts.append("from ..core import Node, EnumerationKind, ExternalReference")
        parts.append("from . import relations")
        for b in prior_buckets:
            if b in needed_imports:
                parts.append(f"from . import {b}")
        if bucket == 'properties':
            parts.append("from ...qudt import Unit, QuantityKind")
        if self.adapter is not None:
            parts.extend(self.adapter.external_import_lines())
        # Restrict `from X import *` to the classes actually defined here - without
        # this, the cross-bucket `from . import {b}` lines above (needed so field
        # types can reference e.g. properties.SomeClass) would themselves leak into
        # any `import *` of this module, shadowing same-named submodules in whatever
        # re-exports it (e.g. clobbering s223.properties with _generated.properties).
        parts.append("__all__ = " + repr([c.class_name for c in classes]))
        parts.append("\n")

        for c in classes:
            parts.append(self._render_class(c, prior_buckets))

        return "\n".join(parts)

    def _render_relations(self) -> str:
        ns_name = getattr(self.adapter, 'namespace_import_name', None) or 'S223'
        parts = [self._header()]
        parts.append("from ...core import semantic_object, Predicate as _CorePredicate")
        parts.append(f"from ...namespaces import {ns_name}")
        parts.append("__all__ = " + repr(['Predicate'] + sorted(r.class_name for r in self.ir.relations.values())))
        parts.append("\n@semantic_object")
        parts.append("class Predicate(_CorePredicate):")
        parts.append(f"    _ns = {ns_name}\n")

        for local in sorted(self.ir.relations.keys()):
            rel = self.ir.relations[local]
            parts.append("@semantic_object")
            parts.append(f"class {rel.class_name}(Predicate):")
            body = []
            if rel.label:
                body.append(f"    label = {rel.label!r}")
            if rel.comment:
                body.append(f"    comment = {rel.comment!r}")
            if rel.inverse_of_local:
                body.append(f"    # inverse of {self.ontology_name}:{rel.inverse_of_local}")
            if not body:
                body.append("    pass")
            parts.append("\n".join(body) + "\n")
        return "\n".join(parts)

    def _render_meta(self) -> str:
        parts = [self._header()]
        parts.append(f"SOURCE_FILE = {str(self.source_path)!r}")
        parts.append(f"SOURCE_SHA256 = {_sha256(self.source_path)!r}")
        parts.append(f"GENERATED_AT = {datetime.now(timezone.utc).isoformat()!r}")
        parts.append(f"CLASS_COUNT = {len(self.ir.classes)}")
        parts.append(f"RELATION_COUNT = {len(self.ir.relations)}")
        parts.append(
            "QUANTITYKINDS_REFERENCED = "
            + pformat(sorted(self.ir.quantitykinds_referenced), width=88)
        )
        parts.append("\n# Shapes that could not be resolved into a field or _valid_relations entry")
        parts.append("# (out-of-scope relation namespace, or a forward/external type reference).")
        parts.append("UNRESOLVED_NOTES = " + pformat(self.unresolved_notes, width=100))
        return "\n\n".join(parts) + "\n"

    def _render_raw_shapes(self) -> str:
        parts = [self._header()]
        parts.append(
            "# Complex SHACL constraints (sh:sparql, sh:or, inverse paths, forbidden "
            "properties)\n# and supplementary notes on qualified fields, keyed by generated "
            "Python class name.\n# Preserved for fidelity - not enforced by the framework. "
            "See docs/exact_values_generalization.md\n# and the ingestion plan for how to "
            "hand-implement any of these as real validators."
        )
        parts.append("RAW_SHAPES = " + pformat(self.raw_shapes, width=100))
        return "\n\n".join(parts) + "\n"

    def _render_init(self) -> str:
        parts = [self._header()]
        parts.append("from . import relations")
        parts.append("from . import enumerationkinds")
        parts.append("from . import properties")
        parts.append("from . import entities")
        parts.append("from .relations import *")
        parts.append("from .enumerationkinds import *")
        parts.append("from .properties import *")
        parts.append("from .entities import *")
        return "\n".join(parts) + "\n"

    # -- top-level entry point --------------------------------------------------

    def emit(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)

        relations_src = self._render_relations()
        enum_src = self._render_bucket('enumerationkinds', [])
        properties_src = self._render_bucket('properties', ['enumerationkinds'])
        entities_src = self._render_bucket('entities', ['enumerationkinds', 'properties'])
        # raw_shapes/meta depend on unresolved_notes/raw_shapes populated during the
        # three _render_bucket calls above, so render them last.
        raw_shapes_src = self._render_raw_shapes()
        meta_src = self._render_meta()
        init_src = self._render_init()

        (self.output_dir / 'relations.py').write_text(relations_src)
        (self.output_dir / 'enumerationkinds.py').write_text(enum_src)
        (self.output_dir / 'properties.py').write_text(properties_src)
        (self.output_dir / 'entities.py').write_text(entities_src)
        (self.output_dir / '_raw_shapes.py').write_text(raw_shapes_src)
        (self.output_dir / '_meta.py').write_text(meta_src)
        (self.output_dir / '__init__.py').write_text(init_src)
