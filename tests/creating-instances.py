#%%
import os 
import sys

sys.path.append('..')
import yaml
from src.semantic_objects.s223.entities import Space, Space_TwoArea, Window
from src.semantic_objects.build_model import BMotifSession
from src.semantic_objects.s223 import get_related_classes
#%%
bm = BMotifSession()

bm.load_class_templates(Space)
print(bm.templates['Space'].inline_dependencies().all_parameters)
s = Space(100)

# %%
s.get_field_values(recursive=True)
# %%
bm.templates
# %%
bm.evaluate(s)
# %%
