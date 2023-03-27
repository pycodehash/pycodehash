# Input class

from __future__ import annotations
import inspect

from typing import Callable


class Node:
    """

    Args:
        qualname : the fully qualified name of the func
        module : the fully qualified name of the module
        func : the callable being stored
    """

    def __init__(
        self,
        func: Callable,
        qualname: str | None,
        module: str | None,
    ):
        if not callable(func):
            raise TypeError("func should be callable")
        self.func = func
        if qualname is not None:
            self.qualname = qualname
        elif hasattr(func, "__qualname__"):
            self.qualname = func.__qualname__
        else:
            raise TypeError(
                "`func` must have attribute __qualname__ or `qualname` must not be None"
            )
        if module is not None:
            self.module = module
        elif hasattr(func, "__module__"):
            self.module = func.__module__
        else:
            raise TypeError(
                "`func` must have attribute __module__ or `module` must not be None"
            )
        self.source: str = inspect.getsource(func)
