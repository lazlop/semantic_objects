"""Hand-written overrides on top of the ontology-generated relations.

The bulk of s223 relations (60 of them) are mechanically derived from the vendored
ontology - see _generated/relations.py, regenerated via
`python -m semantic_objects.ingest.cli --ontology s223`. This module is where any
relation-level customization that can't be derived from SHACL would go; currently
there is none.
"""
from ._generated.relations import *
