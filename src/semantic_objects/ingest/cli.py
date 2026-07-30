import argparse
from pathlib import Path

from .adapters.s223 import S223Adapter
from .adapters.watr import WatrAdapter
from .codegen.emitter import Emitter
from .config import IngestConfig
from .cxf.emitter import CxfEmitter
from .cxf.parser import CxfParser
from .parser import OntologyParser

REPO_ROOT = Path(__file__).resolve().parents[3]

ADAPTERS = {
    's223': (S223Adapter, REPO_ROOT / 'src' / 'semantic_objects' / 'ontologies' / 's223' / '223p.ttl',
             REPO_ROOT / 'src' / 'semantic_objects' / 's223' / '_generated'),
    'watr': (WatrAdapter, REPO_ROOT / 'src' / 'semantic_objects' / 'ontologies' / 'watr' / 'water.ttl',
             REPO_ROOT / 'src' / 'semantic_objects' / 'watr' / '_generated'),
}

# CXF isn't a SHACL/RDF ontology (no rdfs:subClassOf hierarchy, no sh:property
# shapes) - it's ~45 JSON-LD files describing Modelica control-block
# signatures (named inputs/outputs/parameters, optionally composed of named
# sub-blocks). It gets its own parser/emitter rather than an OntologyAdapter;
# see tutorial/cxf-ingestion-tutorial.ipynb for the source shape.
CXF_SOURCE_DIR = (REPO_ROOT / 'src' / 'semantic_objects' / 'ontologies' / 'cxf'
                   / 'Buildings' / 'Controls' / 'OBC' / 'ASHRAE' / 'G36')
CXF_OUTPUT_DIR = REPO_ROOT / 'src' / 'semantic_objects' / 'cxf' / '_generated'

ONTOLOGY_CHOICES = sorted(set(ADAPTERS) | {'cxf'})


def main(argv=None):
    parser = argparse.ArgumentParser(description="Ingest an ontology into generated Python classes.")
    parser.add_argument('--ontology', required=True, choices=ONTOLOGY_CHOICES)
    args = parser.parse_args(argv)

    if args.ontology == 'cxf':
        _run_cxf()
        return

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


def _run_cxf():
    parser = CxfParser(CXF_SOURCE_DIR)
    ir = parser.parse()
    emitter = CxfEmitter(ir, CXF_SOURCE_DIR, CXF_OUTPUT_DIR)
    emitter.emit()

    print(f"Generated {len(ir.blocks)} blocks and {len(ir.enum_types)} enumeration kinds "
          f"into {CXF_OUTPUT_DIR}")
    if parser.warnings:
        print(f"{len(parser.warnings)} warning(s):")
        for w in parser.warnings:
            print(f"  {w}")
    print(f"{len(ir.quantitykinds_referenced)} quantity kind(s) and {len(ir.units_referenced)} unit(s) "
          f"referenced - see _generated/_meta.py")


if __name__ == '__main__':
    main()
