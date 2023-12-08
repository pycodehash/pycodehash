from __future__ import annotations

import ast
from ast import NodeTransformer


class FunctionStripper(NodeTransformer):
    """Removes docstring node from function and class definitions."""

    def visit_FunctionDef(self, node: ast.FunctionDef):
        node.name = "_"
        return node
