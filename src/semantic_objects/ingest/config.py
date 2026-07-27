from dataclasses import dataclass
from pathlib import Path


@dataclass
class IngestConfig:
    ontology_name: str
    source_path: Path
    output_dir: Path
    include_extension_namespaces: bool = False
