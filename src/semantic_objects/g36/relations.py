"""Hand-written overrides on top of the ontology-generated g36 relations.

g36: declares no relations of its own - every g36 field is declared with an s223:
relation (hasProperty, hasDomain, connectedTo, ...), re-exported here via
_generated/relations.py. See _generated/relations.py (regenerated via
`python -m semantic_objects.ingest.cli --ontology g36`).
"""
from ._generated.relations import *
