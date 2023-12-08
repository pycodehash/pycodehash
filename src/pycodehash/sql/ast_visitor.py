from __future__ import annotations

from typing import Any


class ASTVisitor:
    # based on Pythons AST visitor:
    # https://github.com/python/cpython/blob/3.12/Lib/ast.py#L383
    def visit(self, key: str, node: dict[str, Any] | list[dict[str, Any]]):
        method = "visit_" + key
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: dict[str, Any] | list[dict[str, Any]]):
        """Called if no explicit visitor function exists for a node."""
        items = node if isinstance(node, list) else [node]

        for item in items:
            for field, value in item.items():
                if isinstance(value, (list, dict)):
                    self.visit(field, value)
