from __future__ import annotations

import ast

from rope.base import worder
from rope.base.project import Project
from rope.base.pynamesdef import AssignedName, ImportedModule, ImportedName
from rope.base.resources import Resource
from rope.contrib import fixsyntax
from rope.contrib.findit import Location
from rope.refactor import occurrences

from pycodehash.stores import ModuleView


def _get_text_range(node: ast.expr, tokens):
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


def check_func_definition(occurrence):
    return occurrence.is_defined()


def robust_find_definition(
    node: ast.Call,
    mview: ModuleView,
    project: Project,
    resource: Resource | None = None,
    maxfixes: int = 1,
):
    """Return the definition location of the function being called.

    A `Location` object is returned if the definition location can be
    determined, otherwise `None` is returned.
    """
    code = mview.code
    offset_start, offset_end = mview.tree_tokens.get_text_range(node)
    if offset_end == 0:
        # try slower workaround when tree tokens seem to be out of date
        # TODO[RU]: figure out why this needed.
        offset_start, offset_end = _get_text_range(node, mview.tree_tokens.tokens)
    if offset_end == 0:
        return None

    fixer = fixsyntax.FixSyntax(project, code, resource, maxfixes)
    pyname = fixer.pyname_at(offset_start)
    if pyname is not None:
        # TODO[RU] Check if we can whitelist rather than blacklist this case
        if isinstance(pyname, AssignedName):
            return None
        module, lineno = pyname.get_definition_location()
        name = worder.Worder(code).get_word_at(offset_start)
        if lineno is not None:
            start = module.lines.get_line_start(lineno)

            def check_offset(occurrence):
                if occurrence.offset < start:
                    return False

            pyname_filter = occurrences.PyNameFilter(pyname)
            finder = occurrences.Finder(project, name, [check_offset, pyname_filter])
            for occurrence in finder.find_occurrences(pymodule=module):
                return Location(occurrence)

    # handle imports which are not properly traced by rope
    if isinstance(pyname, (ImportedName, ImportedModule)):
        if isinstance(pyname, ImportedModule):
            # we assume that as this is an ImportedModule that the node has an ast.Attribute
            # as func rather than an ast.Name
            name = node.func.attr
        else:
            name = pyname.imported_name
        finder = occurrences.Finder(project, name, [check_func_definition])
        for occurrence in finder.find_occurrences(pymodule=module):
            return Location(occurrence)
