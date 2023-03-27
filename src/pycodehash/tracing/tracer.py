# Functionality to trace calls, i.e. AST visitors
from __future__ import annotations

import ast
import logging
from typing import Any


logger = logging.getLogger(__name__)


class Tracer(ast.NodeVisitor):
    def __init__(self):
        self.import_bindings = {}

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Assign(self, node: ast.Assign) -> Any:
        if isinstance(node.value, ast.Name) and node.value.id in self.import_bindings:
            # Simple alias, e.g. `foo = bar`
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                self.import_bindings[node.targets[0].id] = self.import_bindings[node.value.id]
            else:
                raise NotImplementedError(f"Import '{node.value.id}' is overwritten by '{node.targets}'")

    def _visit_import(self, node: ast.Import | ast.ImportFrom):
        for name in node.names:
            key = name.asname or name.name
            if hasattr(node, "module"):
                if node.module is None:
                    raise NotImplementedError("Relative imports not supported")

                self.import_bindings[key] = f"{node.module}.{name.name}"
            else:
                self.import_bindings[key] = name.name

            if name.name == "*":
                raise NotImplementedError("Star imports are not supported")

    def visit_Import(self, node: ast.Import) -> Any:
        self._visit_import(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        self._visit_import(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        mod = "__main__"
        self.import_bindings[node.name] = f"{mod}.{node.name}"
