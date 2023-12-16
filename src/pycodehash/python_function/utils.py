from __future__ import annotations

import ast
from functools import singledispatch
from types import FunctionType  # noqa
from typing import Any  # noqa

from rope.contrib.findit import Location  # noqa


@singledispatch
def get_func_name(arg: Any, *args, **kwargs):
    msg = f"type `{type(arg)} is not supported."
    raise NotImplementedError(msg)


@get_func_name.register
def _(loc: Location):
    return loc.resource.read()[loc.region[0] : loc.region[1]]


@get_func_name.register
def _(func: FunctionType, default: str = "<unnamed>") -> str:
    return getattr(func, "__name__", default)


def contains_call(node: ast.expr) -> bool:
    return any(isinstance(child, ast.Call) for child in ast.walk(node))
