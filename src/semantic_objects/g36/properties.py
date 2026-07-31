"""Hand-written overrides on top of the ontology-generated g36 properties.

g36: currently declares no property classes of its own - every g36 field targets
an s223: property class directly (see entities.py). See _generated/properties.py
(regenerated via `python -m semantic_objects.ingest.cli --ontology g36`) if that
changes.
"""
from ._generated.properties import *
