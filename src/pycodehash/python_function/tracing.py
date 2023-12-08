from __future__ import annotations

import ast
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from rope.base import worder
from rope.base.project import NoProject, Project
from rope.base.pynamesdef import DefinedName, ImportedModule, ImportedName
from rope.base.resources import File
from rope.contrib import fixsyntax
from rope.contrib.findit import Location
from rope.refactor import occurrences

from pycodehash.python_function.utils import contains_call

if TYPE_CHECKING:
    from asttokens.util import Token
    from rope.refactor.occurrences import Occurrence

    from pycodehash.python_function.stores import ModuleView


def _get_text_range(node: ast.expr, tokens: list[Token]):
    """Get string offset from ast Node
    This is a workaround since `asttoken.get_text_range` needs to be an "EnhancedAST" node...

    Args:
        node: ast Node
        tokens: asttoken tokens

    Returns:
        Offset tuple. Returns 0,0 if not found
    """
    start = end = None
    for token in tokens:
        if token.start == (node.lineno, node.col_offset):
            start = token.startpos
        if token.end == (node.end_lineno, node.end_col_offset):
            end = token.endpos
    if start is not None and end is not None:
        return start, end

    return 0, 0


def check_func_definition(occurrence: Occurrence):
    return occurrence.is_defined()


def robust_extract_name(node: ast.Call, code: str, offset: int) -> str:
    """Extract correct name by accounting for chained calls.

    We extract the first call name of the first encountered attribute.
    """
    if not contains_call(node.func):
        return worder.Worder(code).get_word_at(offset)
    for child in ast.walk(node.func):
        if isinstance(child, ast.Attribute):
            return child.attr
    return ""


def get_func_call_location(node: ast.Call, project: Project, mview: ModuleView) -> Location | None:
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
    code = mview.code
    offset_start, offset_end = mview.tree_tokens.get_text_range(node)
    if offset_end == 0:
        # TODO(RU): figure out why this needed.
        # try slower workaround when tree tokens seem to be out of date
        offset_start, offset_end = _get_text_range(node, mview.tree_tokens.tokens)
    if offset_end == 0:
        return None

    fixer = fixsyntax.FixSyntax(project, code, resource=None)
    pyname = fixer.pyname_at(offset_start)
    if pyname is None or not isinstance(pyname, (DefinedName, ImportedModule, ImportedName)):
        return None

    module, lineno = pyname.get_definition_location()
    # restrict tracing to first party modules
    project_path = Path(project.address)
    module_resource = module.get_resource()
    if module_resource is not None and project_path not in module_resource.pathlib.parents:
        return None

    # handle name selection when there are chained calls
    name = robust_extract_name(node, code, offset_start)

    # -- default rope tracing block
    if lineno is not None:
        start = module.lines.get_line_start(lineno)

        def check_offset(occurrence: Occurrence):
            if occurrence.offset < start:
                return False
            return None

        pyname_filter = occurrences.PyNameFilter(pyname)
        finder = occurrences.Finder(project, name, [check_offset, pyname_filter])
        for occurrence in finder.find_occurrences(pymodule=module):
            location = Location(occurrence)
            if location.resource is None or project_path in location.resource.pathlib.parents:
                return location

    # handle imports which are not properly traced by rope
    if isinstance(pyname, (ImportedName, ImportedModule)):
        # we assume that as this is an ImportedModule that the node has an ast.Attribute
        # as func rather than an ast.Name
        name = node.func.attr if isinstance(pyname, ImportedModule) else pyname.imported_name  # type: ignore[attr-defined]
        finder = occurrences.Finder(project, name, [check_func_definition])
        for occurrence in finder.find_occurrences(pymodule=module):
            location = Location(occurrence)
            if location.resource is None or project_path in location.resource.pathlib.parents:
                return location
    return None


def get_func_node_from_location(location: Location, project: Project) -> ast.FunctionDef:
    """Get func node from rope Location."""
    module = project.get_pymodule(location.resource)
    src = location.resource.read()
    fname = src[location.region[0] : location.region[1]]
    func = module.get_attribute(fname).get_object()
    return func.ast_node


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
        location = Location(occurrence)
        if location.resource is None or Path(project.address) in location.resource.pathlib.parents:
            return location
    return None


def find_call_definition(node: ast.Call, module: ModuleView, project: Project) -> Location | None:
    loc = get_func_call_location(node, project, module)
    if loc is None:
        return None

    # Use current module is location resource is empty
    if isinstance(loc, Location) and loc.resource is None:
        # Important to be consistent with found Location objects!
        loc.resource = File(project=NoProject(), name=str(module.path))

    return loc
