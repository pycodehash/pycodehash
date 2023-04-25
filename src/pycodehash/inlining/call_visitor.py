# Functionality to inline function bodies of the calls
from __future__ import annotations

import logging
import ast
from ast import NodeVisitor


logger = logging.getLogger(__name__)


class CallVisitor(NodeVisitor):
    def __init__(self):
        self.calls = []

    def _visit_func(self, node: ast.Expr, label: str) -> None:
        if isinstance(node, ast.Name):
            logger.info("%s function: %s", label, node.id)
            self.calls.append((label, node.id))
        elif isinstance(node, ast.Attribute):
            logger.info("%s method: %s.%s", label, node.value.id, node.attr)
            self.calls.append((label, f"{node.value.id}.{node.attr}"))
        else:
            raise NotImplementedError

    def visit_Call(self, node: ast.Call):
        self._visit_func(node.func, label="call")
        super().generic_visit(node)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef):
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                self._visit_func(decorator.func, label="decorator call")
            else:
                self._visit_func(decorator, label="decorator")

        # prevent duplicate call visit
        node.decorator_list = []
        super().generic_visit(node)
        return node
