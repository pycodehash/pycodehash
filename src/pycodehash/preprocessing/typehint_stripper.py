from __future__ import annotations

import ast
from ast import NodeTransformer


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

