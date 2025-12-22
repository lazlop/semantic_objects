from buildingmotif import BuildingMOTIF
from typing import Any, Dict, Mapping
from buildingmotif.dataclasses import Library, Model, Template
from rdflib import Graph, Namespace


class BMotifSession():
    
    def __init__(self, ns = 'test'):
        self.bm = BuildingMOTIF("sqlite://")
        self.lib = Library.create("semantic_objects")
        self.building_ns = Namespace(f"urn:{ns}#")
        self.model = Model.create(self.building_ns)
        self.graph = self.model.graph
        self.templates = {}

    def load_class_templates(self, klass):
        related_classes = klass.get_related_classes(klass)
        
        add_dependency_templates = []
        for lst in related_classes:    
            for obj in lst:
                if obj.__name__ in self.templates:
                    continue
                self.templates[obj.__name__] = self.lib.create_template(obj.__name__)
                self.templates[obj.__name__].body.parse(data=obj.generate_turtle_body(), format='turtle')
                add_dependency_templates.append(obj)

        for obj in add_dependency_templates:
            for dependency in obj.get_dependencies():
                self.templates[obj.__name__].add_dependency(self.templates[dependency['template'].__name__], dependency['args'])

    def evaluate(self, obj):
        self.load_class_templates(obj)
        eval_dict = obj.get_field_values(recursive = True)

        def flatten_dict(
            d: Mapping[str, Any],
            parent_key: str = "",
            sep: str = "-",
            out: Dict[str, Any] | None = None,
        ) -> Dict[str, Any]:
            """
            Recursively flatten a nested mapping.

            * keys from inner dictionaries are concatenated to the outer key
            with ``sep`` (default “-”).
            * non‑mapping values are copied unchanged.
            * the function works for arbitrarily deep nesting.
            """
            if out is None:
                out = {}

            for k, v in d.items():
                # ----- special handling for "_name" ---------------------------------
                if k == "_name":
                    if parent_key == "":          # top level
                        out["name"] = self.building_ns[v]
                    else:                         # deeper level → use the parent key itself
                        out[parent_key] = self.building_ns[v]
                    continue                     # nothing else to do for this entry
                # ---------------------------------------------------------------------

                # Build the new composite key
                new_key = f"{parent_key}{sep}{k}" if parent_key else k

                # Recurse for nested mappings, otherwise store the value
                if isinstance(v, Mapping):
                    flatten_dict(v, new_key, sep=sep, out=out)
                else:
                    out[new_key] = v

            return out

        eval_dict = flatten_dict(eval_dict)
        print(eval_dict)
        entity_graph = self.templates[obj.__class__.__name__].evaluate(eval_dict)
        self.model.add_graph(entity_graph)



        