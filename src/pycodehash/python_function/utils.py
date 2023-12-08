from __future__ import annotations

import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import FunctionType


def get_func_name(func: FunctionType, default: str = "<unnamed>") -> str:
    return getattr(func, "__name__", default)


def contains_call(node: ast.expr) -> bool:
    return any(isinstance(child, ast.Call) for child in ast.walk(node))
