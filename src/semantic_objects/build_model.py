from buildingmotif import BuildingMOTIF

from buildingmotif.dataclasses import Library, Model, Template
from rdflib import Graph

from semantic_objects.core import get_related_classes

class BMotifSession():
    
    def __init__(self):
        self.bm = BuildingMOTIF("sqlite://")
        self.lib = Library.create("semantic_objects")
        self.templates = {}

    def load_class(self, klass):
        related_classes = get_related_classes(klass)
        for lst in related_classes:
            for obj in lst:
                if obj.__name__ in self.templates:
                    continue
                self.templates[obj.__name__] = self.lib.create_template(obj.__name__)
                self.templates[obj.__name__].body.parse(data=obj.generate_turtle_body(), format='turtle')

        for lst in related_classes:
            for obj in lst:
                if len(obj.get_dependencies()) > 0:
                    continue
                for dependency in obj.get_dependencies():
                    self.templates[obj.__name__].add_dependency(self.templates[dependency['template'].__name__], dependency['args'])


        