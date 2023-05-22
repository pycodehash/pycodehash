# Functionality to trace calls, i.e. AST visitors
from __future__ import annotations

import ast
from ast import NodeVisitor
import logging
from typing import Any

logger = logging.getLogger(__name__)


def _builtins() -> dict[str, tuple[str, ...]]:
    """Python Builtins

    Returns:
        dictionary of python builtins import bindings

    References:
        https://docs.python.org/3/library/functions.html
    """
    return {
        key: ("__builtins__", key)
        for key in ["abs",
                    "aiter",
                    "all",
                    "any",
                    "anext",
                    "ascii",
                    "bin",
                    "bool",
                    "breakpoint",
                    "bytearray",
                    "bytes",
                    "callable",
                    "chr",
                    "classmethod",
                    "compile",
                    "complex",
                    "delattr",
                    "dict",
                    "dir",
                    "divmod",
                    "enumerate",
                    "eval",
                    "exec",
                    "filter",
                    "float",
                    "format",
                    "frozenset",
                    "getattr",
                    "globals",
                    "hasattr",
                    "hash",
                    "help",
                    "hex",
                    "id",
                    "input",
                    "int",
                    "isinstance",
                    "issubclass",
                    "iter",
                    "len",
                    "list",
                    "locals",
                    "map",
                    "max",
                    "memoryview",
                    "min",
                    "next",
                    "object",
                    "oct",
                    "open",
                    "ord",
                    "pow",
                    "print",
                    "property",
                    "range",
                    "repr",
                    "reversed",
                    "round",
                    "set",
                    "setattr",
                    "slice",
                    "sorted",
                    "staticmethod",
                    "str",
                    "sum",
                    "super",
                    "tuple",
                    "type",
                    "vars",
                    "zip",
                    "_",
                    "__import__"
                    ]
    }


class Tracer(NodeVisitor):
    def __init__(self, mod):
        self.mod = mod
        self.import_bindings = _builtins()

    def visit_Assign(self, node: ast.Assign) -> Any:
        if isinstance(node.value, ast.Name) and node.value.id in self.import_bindings:
            # Simple alias, e.g. `foo = bar`
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                self.import_bindings[node.targets[0].id] = self.import_bindings[node.value.id]
            else:
                pass
                # raise NotImplementedError(f"Import '{node.value.id}' is overwritten by '{node.targets}'")
        super().generic_visit(node)

    def _visit_import(self, node: ast.Import | ast.ImportFrom):
        for name in node.names:
            key = name.asname or name.name
            if hasattr(node, "module"):
                if node.module is None:
                    continue
                    # raise NotImplementedError("Relative imports are not supported")

                self.import_bindings[key] = (node.module, name.name)
            else:
                self.import_bindings[key] = (name.name, )

            if name.name == "*":
                continue
                # raise NotImplementedError("Star imports are not supported")

    def visit_Import(self, node: ast.Import) -> Any:
        self._visit_import(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        self._visit_import(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.import_bindings[node.name] = (self.mod, node.name)

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        self.import_bindings[node.name] = (self.mod, node.name)
        for sub_node in node.body:
            if isinstance(sub_node, ast.FunctionDef):
                self.import_bindings[f"{node.name}.{sub_node.name}"] = (self.mod, node.name, sub_node.name)
