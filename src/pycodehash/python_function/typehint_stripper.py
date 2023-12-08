from __future__ import annotations

import ast
from ast import NodeTransformer


class TypeHintStripper(NodeTransformer):
    """Removes the type hints in the function signature and function body."""

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.returns is not None:
            node.returns = None
        super().generic_visit(node)
        return node

    def visit_arg(self, node: ast.arg):
        if node.annotation is not None:
            node.annotation = None
        return node

    def visit_AnnAssign(self, node: ast.AnnAssign):
        return ast.Assign([node.target], node.value, lineno=node.lineno)
