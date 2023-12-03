"""Collect module imports from the Python AST"""
import ast
from ast import NodeVisitor


class ImportVisitor(NodeVisitor):
    def __init__(self):
        self.imports = []

    def visit_Import(self, node: ast.Import):
        for value in node.names:
            self.imports.append(value.name)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        for value in node.names:
            if node.module is None:
                msg = "Relative imports not yet supported"
                raise NotImplementedError(msg)
            if value.name == "*":
                msg = "Star imports not yet supported"
                raise NotImplementedError(msg)

            self.imports.append(f"{node.module}.{value.name}")
