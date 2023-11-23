from __future__ import annotations

import ast
import logging
from typing import Callable

from rope.base.project import Project
from rope.base.pyobjectsdef import PyModule
from rope.contrib.findit import Location, find_definition
from rope.refactor import occurrences

from pycodehash.stores import ModuleView


def get_func_node(module: ast.Module) -> ast.FunctionDef:
    """Get function from module (`rope` always wraps functions)"""
    for node in module.body:
        if isinstance(node, ast.FunctionDef):
            return node


def get_func_node_from_location(location: Location, project: Project) -> ast.FunctionDef:
    """Get func node from rope Location."""
    module = project.get_pymodule(location.resource)
    src = location.resource.read()
    fname = src[location.region[0] : location.region[1]]
    func = module.get_attribute(fname).get_object()
    return func.ast_node


def get_func_call_location(node: ast.Call, project: Project, module: ModuleView) -> Location | None:
    """Get location of function definition of an ast.Call node.

    Args:
        node: the call node in the source function
        project: the analysed project
        module: the view on the module that contains the function in which `node` is called.

    Returns:
        location: the rope location object or None if no location could be found
    """
    token_offset = module.tree_tokens.get_text_range(node)
    if token_offset == (0, 0):
        logger.debug("Node not found")
        return None

    definition_location = find_definition(project, module.code, token_offset[0])
    return definition_location


def get_func_def_location(func: Callable, project: Project | ProjectStore) -> Location | None:
    """Get the location of function definition from a FunctionType.

    Args:
        func: the function to obtain the location for
        project: the analysed project or all analysed projects.

    Returns:
        location: the rope location object or None if no location could be found
    """
    if isinstance(project, ProjectStore):
        for proj in project.get_projects():
            module = proj.get_module(func.__module__)
            if isinstance(module, PyModule):
                break
    else:
        module = project.get_module(func.__module__)

    if module is None:
        raise RuntimeError(f"func `{func.__name__}` does not appear to be defined in the project(s).")

    finder = occurrences.Finder(project, func.__name__)
    for occurrence in finder.find_occurrences(pymodule=module):
        return Location(occurrence)
    return None
