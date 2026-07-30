"""Low-priority staleness check: catches "ontology vendored file updated but
`python -m semantic_objects.ingest.cli --ontology <name>` wasn't re-run"."""
import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _assert_up_to_date(ontology_name: str, ontology_path: Path, meta_module_name: str):
    import importlib
    meta = importlib.import_module(meta_module_name)
    actual_sha256 = hashlib.sha256(ontology_path.read_bytes()).hexdigest()
    assert meta.SOURCE_SHA256 == actual_sha256, (
        f"{ontology_name}/_generated/ is stale relative to the vendored ontology - re-run "
        f"`python -m semantic_objects.ingest.cli --ontology {ontology_name}`"
    )


def test_s223_generated_meta_matches_vendored_ontology():
    _assert_up_to_date(
        "s223",
        REPO_ROOT / "src" / "semantic_objects" / "ontologies" / "s223" / "223p.ttl",
        "semantic_objects.s223._generated._meta",
    )


def test_watr_generated_meta_matches_vendored_ontology():
    _assert_up_to_date(
        "watr",
        REPO_ROOT / "src" / "semantic_objects" / "ontologies" / "watr" / "water.ttl",
        "semantic_objects.watr._generated._meta",
    )


def test_cxf_generated_meta_matches_vendored_ontology():
    # CXF is ~45 JSON-LD files, not one Turtle file - _meta.SOURCE_SHA256 is a
    # hash over all of them concatenated (see ingest/cxf/emitter.py::_source_hash),
    # so this doesn't fit _assert_up_to_date's single-file signature.
    from semantic_objects.cxf._generated import _meta

    cxf_dir = (REPO_ROOT / "src" / "semantic_objects" / "ontologies" / "cxf"
               / "Buildings" / "Controls" / "OBC" / "ASHRAE" / "G36")
    h = hashlib.sha256()
    for path in sorted(cxf_dir.rglob("*.jsonld")):
        h.update(path.read_bytes())
    assert _meta.SOURCE_SHA256 == h.hexdigest(), (
        "cxf/_generated/ is stale relative to the vendored CXF ontology - re-run "
        "`python -m semantic_objects.ingest.cli --ontology cxf`"
    )
