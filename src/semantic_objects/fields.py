
from dataclasses import field

# a relation that is optional, and will be templatized (optional in bmotif template, used to query semantic data into objects)
def optional_field(relation= None, label=None, comment=None):
    return field(
        default=None,
        init=True,
        metadata={
            'relation': relation,
            'label': label,
            'comment': comment,
            'optional': True
        }
    )

# a field that is required (A SHACL qualified value shape requirement)
# TODO: Consider how to handle qualified vs nonqualified constraints
def required_field(relation = None, min = 1, max = None, qualified = True, label=None, comment=None, value=None, exact_values=None):
    # If the relation is none, it will use a default relation from the types of each thing.
    # The 'value' parameter allows specifying a target field name for inter-field relations
    # The 'exact_values' parameter specifies that the semantic model must have exactly these values (not at least)
    metadata = {
        'min': min,
        'max': max,
        'qualified': qualified,
        'label': label,
        'comment': comment,
        'value': value,  # New parameter for inter-field relations
        'exact_values': exact_values  # New parameter for exact value matching
    }
    
    # Only include relation in metadata if it's not None
    if relation is not None:
        metadata['relation'] = relation
    
    return field(metadata=metadata)

# TODO: consider an alternative way of defining the maximum and minimum 
def exclusive_field(relation = None, min = 1, max = 1, qualified = True, label=None, comment=None):
    # If the relation is none, it will use a default relation from the types of each thing.
    return field(
        metadata={
            'relation': relation,
            'min': min,
            'max': max,
            'qualified': qualified,
            'label': label,
            'comment': comment
        }
    )

def inter_field_relation(source_field: str, relation, target_field: str, min=1, max=None, qualified=True, label=None, comment=None):
    """
    Define a relation between two fields in a class.
    
    Args:
        source_field: Name of the source field
        relation: The relation/predicate to use
        target_field: Name of the target field
        min: Minimum cardinality
        max: Maximum cardinality
        qualified: Whether to use qualified value shapes
        label: Optional label for the relation
        comment: Optional comment for the relation
    
    Returns:
        A dictionary describing the inter-field relation
    """
    return {
        'source_field': source_field,
        'relation': relation,
        'target_field': target_field,
        'min': min,
        'max': max,
        'qualified': qualified,
        'label': label,
        'comment': comment
    }
