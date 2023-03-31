# functionality around pre-processing of the node ast
from __future__ import annotations
import ast

from ast import NodeTransformer

from pycodehash.unparse import _unparse


class DocstringStripper(NodeTransformer):
    """Removes docstring node from function and class definitions."""

    def __init__(self):
        self.parent = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.parent = node
        super().generic_visit(node)
        self.parent = None
        return node

    def visit_Expr(self, node: ast.Expr):
        if (
            isinstance(self.parent, ast.FunctionDef)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            return None
        return node


class TypeHintStripper(NodeTransformer):
    """Removes type hint in the function signature and function body."""

    def visit_FunctionDef(self, node):
        node.returns = None
        super().generic_visit(node)
        return node

    def visit_arg(self, node):
        node.annotation = None
        return node

    def visit_AnnAssign(self, node):
        if node.value is None:
            return None
        return ast.Assign([node.target], node.value, lineno=node.lineno)


def to_normalised_string(src: ast.Module | ast.FunctionDef) -> str:
    """Unparse and create normalised string.

    The leading and trailing whitespace is removed
    and line breaks are replaced with a semicolumn.

    Args:
        src : the ast.Module or node to be unparsed.

    Returns:
        str : the normalised string representation

    """
    return ";".join(s.strip() for s in _unparse(src).splitlines())
