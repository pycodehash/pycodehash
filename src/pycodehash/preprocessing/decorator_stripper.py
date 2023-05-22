from __future__ import annotations

import ast
from ast import NodeTransformer

from pycodehash.unparse import _unparse


def get_decorator_name(decorator: ast.expr):
    if isinstance(decorator, ast.Name):
        return decorator.id
    if isinstance(decorator, ast.Call):
        return get_decorator_name(decorator.func)
    if isinstance(decorator, ast.Attribute):
        return get_decorator_name(decorator.value) + "." + decorator.attr

    raise NotImplementedError


class FunctionStripper(NodeTransformer):
    """Removes specific decorators from functions."""
    def __init__(self, decorators: list[str]):
        self.decorators = decorators

    def visit_FunctionDef(self, node: ast.FunctionDef):
        node.decorator_list = [
            decorator
            for decorator in node.decorator_list
            if get_decorator_name(decorator) not in self.decorators
        ]
        return node


if __name__ == "__main__":
    src = """import functools
from functools import lru_cache

def hello(x):
    return x
    
@hello()
@hello
@functools.lru_cache()
@functools.lru_cache
@lru_cache()
@lru_cache
def world():
    pass
"""
    src = ast.parse(src)
    a = FunctionStripper(decorators=["functools.lru_cache"])
    x = a.visit(src)
    print(_unparse(x))
