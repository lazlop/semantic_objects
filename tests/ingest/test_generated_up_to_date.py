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
