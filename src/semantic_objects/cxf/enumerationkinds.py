"""Hand-written overrides on top of the ontology-generated enumeration kinds.

See _generated/enumerationkinds.py (regenerated via
`python -m semantic_objects.ingest.cli --ontology cxf`) for the CXF Types/*
enumeration kinds (VentilationStandard, HeatingCoil, ...) derived from the
vendored CXF JSON-LD. Blanket passthrough for now - see blocks/__init__.py.
"""
from ._generated.enumerationkinds import *
from ._generated.enumerationkinds import __all__
