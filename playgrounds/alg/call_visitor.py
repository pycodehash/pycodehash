"""Functionality to detect if there is any function/method calls in source code"""
from __future__ import annotations

import ast
from ast import NodeVisitor


class CallVisitor(NodeVisitor):
    def __init__(self):
        self.found = False

    def _visit_func(self, node: ast.expr) -> None:
        if self.found:
            return

        self.found = True

    def visit_Call(self, node: ast.Call):
        self._visit_func(node.func)
        if self.found:
            return

        super().generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        for decorator in node.decorator_list:
            # `@decorator` and `@decorator()`
            func = decorator.func if isinstance(decorator, ast.Call) else decorator
            self._visit_func(func)
            if self.found:
                return

        # prevent duplicate call visit
        node.decorator_list = []
        super().generic_visit(node)
