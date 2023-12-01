from __future__ import annotations

import ast
from ast import NodeTransformer


def _get_decorator_name(decorator: ast.expr):
    if isinstance(decorator, ast.Name):
        return decorator.id
    if isinstance(decorator, ast.Call):
        return _get_decorator_name(decorator.func)
    if isinstance(decorator, ast.Attribute):
        return _get_decorator_name(decorator.value) + "." + decorator.attr

    raise NotImplementedError


class DecoratorStripper(NodeTransformer):
    """Removes specific decorators from functions."""

    def __init__(self, decorators: list[str]):
        """Initialize the DecoratorStripper

        Args:
            decorators: list of fully qualified function names (e.g. `functools.partial`)
        """
        self.decorators = decorators

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # TODO(SB): import visitor to resolve to FQN
        node.decorator_list = [
            decorator for decorator in node.decorator_list if _get_decorator_name(decorator) not in self.decorators
        ]
        return node
