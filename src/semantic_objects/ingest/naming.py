import keyword
import re

_CAMEL_BOUNDARY = re.compile(r'(?<!^)(?=[A-Z])')
_NON_IDENT = re.compile(r'[^0-9a-zA-Z_]')


def _avoid_keyword(name: str) -> str:
    return f"{name}_" if keyword.iskeyword(name) else name


def local_name(iri) -> str:
    """Local name of an IRI: text after the last '#' or '/'."""
    s = str(iri)
    if '#' in s:
        return s.rsplit('#', 1)[-1]
    return s.rstrip('/').rsplit('/', 1)[-1]


def snake_case(name: str) -> str:
    name = name.replace('-', '_')
    name = _CAMEL_BOUNDARY.sub('_', name)
    name = re.sub(r'_+', '_', name)
    return name.lower()


def strip_has_is_prefix(local: str) -> str:
    """hasConnectionPoint -> ConnectionPoint, isDeltaQuantity -> DeltaQuantity."""
    if local.startswith('has') and len(local) > 3 and local[3].isupper():
        return local[3:]
    if local.startswith('is') and len(local) > 2 and local[2].isupper():
        return local[2:]
    return local


def field_name_for_path(path_local: str) -> str:
    return _avoid_keyword(snake_case(strip_has_is_prefix(path_local)))


def field_name_for_qualified(target_local: str) -> str:
    """OutletConnectionPoint -> outlet_connection_point; Fluid-Water -> water."""
    simple = target_local.rsplit('-', 1)[-1] if '-' in target_local else target_local
    return _avoid_keyword(snake_case(simple))


def class_name_for(local: str) -> str:
    """Ontology local name -> Python class name.

    Taxonomy leaves are IRI'd as "Category-Value" (e.g. "Aspect-Setpoint",
    "Fluid-Water"); the trailing segment is the conventional short Python name.
    Ordinary classes have no hyphen and pass through unchanged.
    """
    candidate = local.rsplit('-', 1)[-1] if '-' in local else local
    candidate = _NON_IDENT.sub('_', candidate)
    if not candidate:
        candidate = _NON_IDENT.sub('_', local)
    if candidate[0].isdigit():
        candidate = f"_{candidate}"
    return _avoid_keyword(candidate)


def make_unique(name: str, taken: set) -> str:
    if name not in taken:
        taken.add(name)
        return name
    i = 2
    while f"{name}_{i}" in taken:
        i += 1
    unique = f"{name}_{i}"
    taken.add(unique)
    return unique
