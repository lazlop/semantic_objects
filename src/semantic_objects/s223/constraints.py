from .entities import *
from .relations import *


# Define relation constraints
# Format: (source_class, relation, target_class)
RELATION_CONSTRAINTS = [
    # Entity constraints
    (Entity, hasProperty, QuantifiableObervableProperty),
    
    # PhysicalSpace constraints
    (PhysicalSpace, contains, PhysicalSpace),
    (PhysicalSpace, encloses, DomainSpace),
    
    # DomainSpace constraints
    (DomainSpace, hasWindow, Window),
]


def apply_relation_constraints():
    """
    Apply relation constraints to populate _valid_relations on each class.
    This function should be called after all entity classes are defined.
    """
    # Group constraints by source class
    constraints_by_class = {}
    for source_class, relation, target_class in RELATION_CONSTRAINTS:
        if source_class not in constraints_by_class:
            constraints_by_class[source_class] = []
        constraints_by_class[source_class].append((relation, target_class))
    
    # Apply constraints to each class
    for source_class, relations in constraints_by_class.items():
        source_class._valid_relations = relations
    
    # Apply constraints to relations
    for source_class, relation, target_class in RELATION_CONSTRAINTS:
        relation._applies_to = [(source_class, target_class)]

# Apply the constraints
# TODO: Will add inferences to this file. 
apply_relation_constraints()