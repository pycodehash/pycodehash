from __future__ import annotations

import importlib
from dataclasses import dataclass
from types import FunctionType, ModuleType


@dataclass
class FQN:
    module_name: str


@dataclass
class FunctionFQN(FQN):
    function_name: str


@dataclass
class MethodFQN(FQN):
    class_name: str
    method_name: str


def get_module_by_name(module_name: str) -> ModuleType | None:
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


def get_fqn(prefx):
    if len(prefx) >= 2:
        m = get_module_by_name(prefx[0])
        if m is not None:
            if hasattr(m, prefx[1]):
                o = getattr(m, prefx[1])
                if isinstance(o, ModuleType):
                    prefx = tuple([".".join(prefx)])
                elif isinstance(o, FunctionType):
                    # this is what we like
                    pass
                else:
                    print(prefx, "is of type", type(o))
                    # print(prefx, "is a module!")
    return prefx
