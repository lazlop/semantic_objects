import argparse
from pathlib import Path

from .adapters.s223 import S223Adapter
from .adapters.watr import WatrAdapter
from .codegen.emitter import Emitter
from .config import IngestConfig
from .parser import OntologyParser

REPO_ROOT = Path(__file__).resolve().parents[3]

ADAPTERS = {
    's223': (S223Adapter, REPO_ROOT / 'src' / 'semantic_objects' / 'ontologies' / 's223' / '223p.ttl',
             REPO_ROOT / 'src' / 'semantic_objects' / 's223' / '_generated'),
    'watr': (WatrAdapter, REPO_ROOT / 'src' / 'semantic_objects' / 'ontologies' / 'watr' / 'water.ttl',
             REPO_ROOT / 'src' / 'semantic_objects' / 'watr' / '_generated'),
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Ingest an ontology into generated Python classes.")
    parser.add_argument('--ontology', required=True, choices=sorted(ADAPTERS.keys()))
    args = parser.parse_args(argv)

    adapter_cls, source_path, output_dir = ADAPTERS[args.ontology]
    config = IngestConfig(ontology_name=args.ontology, source_path=source_path, output_dir=output_dir)
    adapter = adapter_cls()

    ir = OntologyParser(config, adapter).parse()
    emitter = Emitter(ir, adapter.scaffold_parent_local_names(), source_path, output_dir, args.ontology,
                       adapter=adapter)
    emitter.emit()

    print(f"Generated {len(ir.classes)} classes and {len(ir.relations)} relations into {output_dir}")
    if emitter.unresolved_notes:
        n = sum(len(v) for v in emitter.unresolved_notes.values())
        print(f"{n} shape(s) across {len(emitter.unresolved_notes)} class(es) could not be resolved "
              f"into a field/_valid_relations entry (out-of-scope relation namespace or forward "
              f"bucket reference) - see _generated/_meta.py::UNRESOLVED_NOTES")
    unmapped = sorted(ir.quantitykinds_referenced)
    print(f"{len(unmapped)} quantity kind(s) referenced by the ontology - see "
          f"_generated/_meta.py::QUANTITYKINDS_REFERENCED")


if __name__ == '__main__':
    main()
