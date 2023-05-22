"""Get source code based on fully qualified names"""
from __future__ import annotations

import importlib
import inspect
from types import ModuleType, FunctionType, MethodType


def get_module_by_name(module_name: str) -> ModuleType | None:
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


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


def get_module_source(module_name: str) -> str:
    module = get_module_by_name(module_name)
    if module is None:
        return ""
    return inspect.getsource(module)


def get_function_source(function_name: str, module_name: str) -> str:
    function = get_function_by_name(function_name, module_name)
    if function is None:
        return ""
    return inspect.getsource(function)


def _deindent(src: str) -> str:
    """Remove one level of indentation (assumes four spaces)

    Args:
        src: source code

    Returns:
        source code
    """
    assert src[0:4] == "    "
    return "\n".join([line[4:] for line in src.splitlines()])


def get_method_source(method_name: str, class_name: str, module_name: str) -> str:
    method = get_method_by_name(method_name, class_name, module_name)
    if method is None:
        return ""
    src = inspect.getsource(method)
    news = _deindent(src)
    return news
