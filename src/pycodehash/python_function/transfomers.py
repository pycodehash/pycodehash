"""Visitors used in call tracing."""
from __future__ import annotations

import ast
from ast import NodeTransformer
from itertools import chain
from typing import TYPE_CHECKING

from rope.contrib.findit import Location

if TYPE_CHECKING:
    from pycodehash.python_function.hashing import FunctionHasher
    from pycodehash.python_function.stores import ModuleView, ProjectStore
from pycodehash.python_function.tracing import find_call_definition
from pycodehash.python_function.utils import contains_call


class HashCallNameTransformer(NodeTransformer):
    """Replace the function names in a call with the hash of that call"""

    def __init__(self, hasher: FunctionHasher, location: Location):
        self.hasher = hasher
        self.project_store: ProjectStore = hasher.project_store
        self.def_location = location

        for project in self.project_store:
            module = project.get_pymodule(location.resource)
            if module is not None:
                self.project = project
                break
        self.module: ModuleView = self.hasher.module_store[module]
        self.hash_repr: str | None = None

    def visit_Call(self, node: ast.Call):
        """Find the hash each call"""
        # iterate over the projects until we find the location.
        # the first project is the one to which the module belongs.
        projects = chain([self.project], (project for project in self.project_store if project != self.project))
        for project in projects:
            location = find_call_definition(node, self.module, project)

            if isinstance(location, Location):
                # store the calls
                self.hasher.func_call_store[self.def_location] = location
                # here we recurse into the hashing function
                self.hash_repr = self.hasher.hash_location(location, project)
                if isinstance(node.func, ast.Attribute) and not contains_call(node.func):
                    # here we assume that we are looking at chained attributes
                    node = ast.Call(
                        func=ast.Name(id=self.hash_repr, ctx=node.func.ctx), args=node.args, keywords=node.keywords
                    )
                    self.hash_repr = None
                    # we don't need to traverse down this node as we just created it and know what it contains...
                    return node
                break

        # here we make use of the fact that `NodeTransformer` perform a depth-first traversal
        # the first Name node should be the name of the call.
        super().generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name):
        """Replace the name of a call with the source hash"""
        if self.hash_repr is not None:
            node.id = self.hash_repr
            self.hash_repr = None
        return node
