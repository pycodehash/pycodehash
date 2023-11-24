from __future__ import annotations

import ast
from typing import Callable

from rope.base.project import NoProject, Project
from rope.base.resources import File
from rope.contrib.findit import Location
from rope.refactor import occurrences

from pycodehash.stores import ModuleView
from pycodehash.tracing import check_func_definition, robust_find_definition


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

    Raises:
        ValueError: when Call is not found in the AST Tree
    """
    # TODO[RU] decide on how to structure this better
    return robust_find_definition(node, module, project)


def get_func_def_location(func: Callable, project: Project) -> Location | None:
    """Get the location of function definition from a FunctionType.

    Args:
        func: the function to obtain the location for
        project: the analysed project

    Returns:
        location: the rope location object or None if no location could be found
    """
    module = project.get_module(func.__module__)

    finder = occurrences.Finder(project, func.__name__, [check_func_definition])
    for occurrence in finder.find_occurrences(pymodule=module):
        return Location(occurrence)
    return None


def find_call_definition(node: ast.expr, module, project) -> Location | None:
    loc = get_func_call_location(node, project, module)
    if loc is None:
        return None

    # Use current module is location resource is empty
    if isinstance(loc, Location) and loc.resource is None:
        # Important to be consistent with found Location objects!
        loc.resource = File(project=NoProject(), name=str(module.path))

    return loc
