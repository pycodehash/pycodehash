from __future__ import annotations

import ast

from rope.base import worder
from rope.base.project import Project
from rope.base.pynamesdef import ImportedModule, ImportedName
from rope.base.resources import Resource
from rope.contrib import fixsyntax
from rope.contrib.findit import Location
from rope.refactor import occurrences

from pycodehash.stores import ModuleView


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
        return None

    fixer = fixsyntax.FixSyntax(project, code, resource, maxfixes)
    pyname = fixer.pyname_at(offset_start)
    if pyname is not None:
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
