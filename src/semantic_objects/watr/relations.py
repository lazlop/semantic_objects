"""Hand-written overrides on top of the ontology-generated relations.

WATR's own relations (15 of them, e.g. hasProcess, hasAccuracy) are mechanically
derived from the vendored ontology - see _generated/relations.py, regenerated via
`python -m semantic_objects.ingest.cli --ontology watr`. Relations WATR reuses
directly from s223 (e.g. hasRole, hasConnectionPoint) are referenced from
semantic_objects.s223, not redefined here. This module is where any
relation-level customization that can't be derived from SHACL would go;
currently there is none.
"""
from ._generated.relations import *
