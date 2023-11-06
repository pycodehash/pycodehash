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


def get_func_def_location(node: ast.Call, project: Project, module: ModuleView) -> Location:
    """Get location of function defintion of a ast.Call node.

    Args:
        node: the call node in the source function
        project: the analysed project
        module: the view on the module that contains the function in which `node` is called.

    Returns:
        location: the rope location object
    """
    token_offset = module.tree_tokens.get_text_range(node)
    return find_definition(project, module.code, token_offset)
