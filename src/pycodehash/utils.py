from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import FunctionType


def get_func_name(func: FunctionType, default: str = "<unnamed>") -> str:
    return getattr(func, "__name__", default)
