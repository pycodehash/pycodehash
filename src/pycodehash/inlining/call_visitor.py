# TODO: obviated
# Functionality to detect function/method calls in source code
from __future__ import annotations

import ast
import logging
from ast import NodeVisitor

logger = logging.getLogger(__name__)


class CallVisitor(NodeVisitor):
    def __init__(self):
        self.calls: list[tuple[str, ...]] = []

    def _visit_func(self, node: ast.expr, label: str) -> None:
        if isinstance(node, ast.Name):
            logger.info("%s function: %s", label, node.id)
            self.calls.append((node.id,))
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Call):
                # Chained; currently ignored
                ...
            elif isinstance(node.value, ast.Name):
                logger.info("%s method: %s.%s", label, node.value.id, node.attr)
                self.calls.append((node.value.id, node.attr))
        elif isinstance(node, ast.Call):
            # Chained; currently ignored
            ...
        elif isinstance(node, ast.Subscript):
            # Subscript; currently ignored
            ...
        else:
            raise NotImplementedError

    def visit_Call(self, node: ast.Call):
        self._visit_func(node.func, label="call")
        super().generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                self._visit_func(decorator.func, label="decorator call")
            else:
                self._visit_func(decorator, label="decorator")

        # prevent duplicate call visit
        node.decorator_list = []
        super().generic_visit(node)
