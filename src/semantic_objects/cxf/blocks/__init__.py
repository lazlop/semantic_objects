"""Hand-written overrides on top of the ontology-generated blocks.

See _generated/blocks/** (regenerated via
`python -m semantic_objects.ingest.cli --ontology cxf`) for the full nested
package tree mirroring the CXF folder hierarchy. Unlike s223's entities (which
need per-class __post_init__ business logic), CXF blocks are pure I/O
signatures, so there's nothing to hand-customize yet - this is a blanket
passthrough. Add a same-named submodule here (mirroring the generated
package path) the day a specific block needs one.
"""
from .._generated.blocks import *
from .._generated.blocks import __all__
