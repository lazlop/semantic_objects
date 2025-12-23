from typing import List, Dict, Tuple, Type, Union, Optional, get_origin, get_args, Self
from dataclasses import dataclass, field, fields, _MISSING_TYPE
from .namespaces import PARAM, RDF, RDFS, SH, bind_prefixes
from .query import SparqlQueryBuilder
import yaml
import sys
from pathlib import Path
from rdflib import Graph, Literal, BNode, URIRef

def export_templates(dclass_lst: List[Type], dir_path_str: str, overwrite = True):
    class_lsts = get_related_classes(dclass_lst)
    dir = Path(dir_path_str)
    dir.mkdir(parents=True, exist_ok=True)
    # TODO: After addressing in semantic_mpc_interface, values will become properties
    files =  [dir / 'relations.yml', dir / 'entities.yml', dir / 'values.yml']
    for file, lst in zip(files, class_lsts):
        if file.exists() and not overwrite:
            continue
        if file.exists():
            file.unlink()
        for klass in lst:
            klass.to_yaml(file_path = file)

# Define a custom class for folded style text
class FoldedString(str):
    pass

# Create a custom representer for the folded style
def folded_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

# Register the representer
yaml.add_representer(FoldedString, folded_str_representer)