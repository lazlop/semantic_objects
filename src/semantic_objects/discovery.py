from typing import List, Dict, Tuple, Type, Union, Optional, get_origin, get_args, Self
from .core import Resource

def get_related_classes(dclass: Union[Type, List[Type]], get_recursive = True):
    """
    Module-level convenience function for getting related classes.
    Delegates to the Resource.get_related_classes() class method.
    """
    if isinstance(dclass, list):
        return _get_related_classes_lst(dclass, get_recursive)
    else:
        # Delegate to the class method
        if not isinstance(dclass, type) or not issubclass(dclass, Resource):
            return [], []
        return dclass.get_related_classes(get_recursive=get_recursive)

def _get_related_classes_lst(dclass_lst: List[Type], get_recursive = True):
    """Helper function to get related classes from a list of classes."""
    predicate_lst, entity_lst, value_lst = [], [], []
    for dclass in dclass_lst:
        if not isinstance(dclass, type) or not issubclass(dclass, Resource):
            continue
        class_lsts = dclass.get_related_classes(get_recursive=get_recursive)
        for lst, new_klasses in zip([predicate_lst, entity_lst, value_lst], class_lsts): 
            for klass in new_klasses: 
                if klass not in lst:
                    lst.append(klass)
    return predicate_lst, entity_lst, value_lst        

def get_module_classes(module_lst):
    """Get all Resource classes from a list of modules."""
    predicate_lst, entity_lst, value_lst = [], [], []
    for module in module_lst:
        for k, v in module.__dict__.items():
            if not isinstance(v, type):
                continue
            if not issubclass(v, Resource):
                continue
            class_lsts = v.get_related_classes()
            for lst, new_klasses in zip([predicate_lst, entity_lst, value_lst], class_lsts): 
                for klass in new_klasses: 
                    if klass not in lst:
                        lst.append(klass)
    return predicate_lst, entity_lst, value_lst