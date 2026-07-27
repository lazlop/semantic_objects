from .model_loader import ModelLoader, query_to_df


def __getattr__(name):
    # Lazy so that `semantic_objects.ingest` (which regenerates s223/_generated/)
    # can be imported/run even when _generated/ doesn't exist yet - eagerly
    # importing s223 here would otherwise create a bootstrap cycle, since s223's
    # hand-written modules import from _generated/.
    if name in ('s223', 'qudt', 'watr'):
        import importlib
        module = importlib.import_module(f'.{name}', __name__)
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")