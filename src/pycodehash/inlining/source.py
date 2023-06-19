"""Get source code based on fully qualified names"""
from __future__ import annotations

import inspect
from types import FunctionType, MethodType

from pycodehash.inlining.fqn import get_module_by_name


def _get_source(o) -> str | None:
    try:
        source = inspect.getsource(o)
    except OSError:
        # no source code available for `o`
        return None

    return source


def get_function_by_name(function_name: str, module_name: str) -> FunctionType | None:
    module = get_module_by_name(module_name)
    if module is None:
        return None
    return getattr(module, function_name)


def get_method_by_name(method_name: str, class_name: str, module_name: str) -> MethodType | None:
    function = get_function_by_name(class_name, module_name)
    if function is None:
        return None
    return getattr(function, method_name)


def get_module_source(module_name: str) -> str | None:
    module = get_module_by_name(module_name)
    if module is None:
        return None

    return _get_source(module)


def get_function_source(function_name: str, module_name: str) -> str | None:
    function = get_function_by_name(function_name, module_name)
    if function is None:
        return None
    src = _get_source(function)
    if src is None:
        return None
    if len(src) > 4 and src[0:4] == "    ":
        # decorated
        return _deindent(src)
    return src


# TODO: remove, do via AST
def _deindent(src: str) -> str:
    """Remove one level of indentation (assumes four spaces)

    Args:
        src: source code

    Returns:
        source code
    """
    assert src[0:4] == "    "
    return "\n".join([line[4:] for line in src.splitlines()]) + "\n"


def get_method_source(method_name: str, class_name: str, module_name: str) -> str | None:
    method = get_method_by_name(method_name, class_name, module_name)
    if method is None:
        return None
    src = _get_source(method)
    if src is None:
        return None
    news = _deindent(src)
    return news
