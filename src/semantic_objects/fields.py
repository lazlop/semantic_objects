
from dataclasses import field

# core.py/exporters.py treat a 'relation' key that's present-but-None as
# "explicitly no relation" (skip generating one - used for fields that are
# only reachable via an inter-field relation, e.g. a window field targeted by
# a space->window inter_field_relation shouldn't ALSO get a direct
# main-entity->window relation). An absent key means "infer it from
# _valid_relations" instead. relation=None can't just default to "infer",
# because "no relation" is itself a real, intentional state - so inference
# is opt-in via infer_relation=True.
def _relation_metadata(relation, infer_relation):
    return {} if infer_relation else {'relation': relation}

# a relation that is optional, and will be templatized (optional in bmotif template, used to query semantic data into objects)
def optional_field(relation=None, label=None, comment=None, infer_relation=False):
    # infer_relation=True infers the relation from _valid_relations at
    # generation time instead of requiring (or explicitly omitting) one here.
    return field(
        default=None,
        init=False,
        metadata={
            **_relation_metadata(relation, infer_relation),
            'label': label,
            'comment': comment
        }
    )

# a field that is required (A SHACL qualified value shape requirement)
# TODO: Consider how to handle qualified vs nonqualified constraints
def required_field(relation=None, min=1, max=None, qualified=True, label=None, comment=None, value=None, exact_values=None, infer_relation=False):
    # infer_relation=True infers the relation from _valid_relations at
    # generation time instead of requiring (or explicitly omitting) one here.
    # The 'value' parameter allows specifying a target field name for inter-field relations
    # The 'exact_values' parameter specifies that the semantic model must have exactly these values (not at least)
    return field(
        metadata={
            **_relation_metadata(relation, infer_relation),
            'min': min,
            'max': max,
            'qualified': qualified,
            'label': label,
            'comment': comment,
            'value': value,  # New parameter for inter-field relations
            'exact_values': exact_values  # New parameter for exact value matching
        }
    )

# TODO: consider an alternative way of defining the maximum and minimum
def exclusive_field(relation=None, min=1, max=1, qualified=True, label=None, comment=None, infer_relation=False):
    # infer_relation=True infers the relation from _valid_relations at
    # generation time instead of requiring (or explicitly omitting) one here.
    return field(
        metadata={
            **_relation_metadata(relation, infer_relation),
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
