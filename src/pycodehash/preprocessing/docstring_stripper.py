from __future__ import annotations

import ast
from ast import NodeTransformer


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
