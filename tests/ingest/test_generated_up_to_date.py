"""Low-priority staleness check: catches "ontology vendored file updated but
`python -m semantic_objects.ingest.cli --ontology s223` wasn't re-run"."""
import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_PATH = REPO_ROOT / "src" / "semantic_objects" / "ontologies" / "s223" / "223p.ttl"


def test_generated_meta_matches_vendored_ontology():
    from semantic_objects.s223._generated import _meta

    actual_sha256 = hashlib.sha256(ONTOLOGY_PATH.read_bytes()).hexdigest()
    assert _meta.SOURCE_SHA256 == actual_sha256, (
        "s223/_generated/ is stale relative to the vendored ontology - re-run "
        "`python -m semantic_objects.ingest.cli --ontology s223`"
    )


def test_g36_generated_meta_matches_vendored_ontology():
    # g36 is vendored in the same 223p.ttl file, under the g36: prefix.
    from semantic_objects.g36._generated import _meta

    actual_sha256 = hashlib.sha256(ONTOLOGY_PATH.read_bytes()).hexdigest()
    assert _meta.SOURCE_SHA256 == actual_sha256, (
        "g36/_generated/ is stale relative to the vendored ontology - re-run "
        "`python -m semantic_objects.ingest.cli --ontology g36`"
    )
