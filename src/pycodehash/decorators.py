# TODO: move to utilipy?
"""Decorators."""
import inspect

from pycodehash.hashing import hash_func_params


def cache(func):
    """Attach a cache to the function.

    The cache assumes that the function is:
    - entirely deterministic given the input parameters
    - the input parameters are json serializable

    Args:
        func: the function to be wrapped

    Returns:
        udf_cacher: wrapped func that is cache enabled
    """
    # this function differs from functools.cache in that it can handle
    # all json serializable parameters (i.e. including dicts) which
    # functools.cache does not

    def udf_cacher(*args, **kwargs):
        key = hash_func_params(udf_cacher.keywords, args, kwargs)
        if key not in udf_cacher.cache:
            udf_cacher.cache[key] = udf_cacher.func(*args, **kwargs)
        return udf_cacher.cache[key]

    signature = inspect.signature(func)
    udf_cacher.func = func
    udf_cacher.cache = {}
    udf_cacher.keywords = list(signature.parameters.keys())
    udf_cacher.__module__ = func.__module__
    udf_cacher.__name__ = func.__name__
    udf_cacher.__qualname__ = func.__qualname__
    udf_cacher.__doc__ = func.__doc__ or f"signature: {func}{signature.__str__()}"

    return udf_cacher
