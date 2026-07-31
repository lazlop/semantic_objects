"""Hand-written overrides on top of the ontology-generated g36 entities.

See _generated/entities.py (regenerated via
`python -m semantic_objects.ingest.cli --ontology g36`) for the classes derived
from the vendored ontology's g36: SHACL shapes. Nothing needs hand customization
here currently - add __post_init__ coercion, _inter_field_relations, or other
non-derivable behavior on a subclass here as needed.
"""
from ._generated.entities import *
