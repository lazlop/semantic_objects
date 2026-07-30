"""Hand-written overrides on top of the ontology-generated properties.

See _generated/properties.py (regenerated via
`python -m semantic_objects.ingest.cli --ontology watr`) for anything derived from
the vendored WATR ontology's SHACL shapes. Nothing needs hand customization here
currently.
"""
from ._generated.properties import *
