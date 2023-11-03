from __future__ import annotations

import ast

from rope.base.project import Project
from rope.contrib.findit import Location, find_definition

from pycodehash.tracing.stores import ModuleView


def get_func_node(module: ast.Module) -> ast.FunctionDef:
    for node in module.body:
        if isinstance(node, ast.FunctionDef):
            return node


def get_func_location(code: str, module_tree: ast.Module, project: Project, module: ModuleView) -> Location:
    node = get_func_node(module_tree)
    return find_definition(project, code, module.tree_tokens.get_text_range(node)[0])
