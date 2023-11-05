from __future__ import annotations

import ast

from rope.base.project import Project
from rope.contrib.findit import Location, find_definition

from pycodehash.tracing.stores import ModuleView


def get_func_node(module: ast.Module) -> ast.FunctionDef:
    """Get function from module (`rope` always wraps functions)"""
    for node in module.body:
        if isinstance(node, ast.FunctionDef):
            return node


def get_func_location(code: str, module_tree: ast.Module, project: Project, module: ModuleView) -> Location:
    node = get_func_node(module_tree)
    location = module.tree_tokens.get_text_range(node)
    offset, _ = location

    # TODO(SB): incomplete, offset needs to be the identifier, not function definition. Now manually increase by "def "
    return find_definition(project, code, offset + 4)
