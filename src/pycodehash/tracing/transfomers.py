"""Visitors used in call tracing."""
from __future__ import annotations

import ast
from ast import NodeTransformer

from rope.base.libutils import path_to_resource
from rope.contrib.findit import Location

from pycodehash.tracing.stores import ModuleView, ProjectStore
from pycodehash.tracing.utils import get_func_call_location


class HashCallNameTransformer(NodeTransformer):
    """Replace the function names in a call with the hash of that call"""

    def __init__(self, hasher, location: Location):
        self._calls = []
        self.hasher = hasher
        self.project_store: ProjectStore = hasher.project_store
        for project in self.project_store.get_projects():
            module = project.get_pymodule(location.resource)
            if module is not None:
                break
        self.module: ModuleView = self.hasher.module_store.get_from_module(module)
        self.hash_repr = None

    def find_definition(self, node, project) -> Location | None:
        loc = get_func_call_location(node, project, self.module)
        if isinstance(loc, Location) and loc.resource is None:
            loc.resource = path_to_resource(project, self.module.path)
        return loc

    def visit_Call(self, node: ast.Call):
        """Find the hash each call"""
        # iterate over the projects until we find the location.
        # the first project is the one to which the module belongs.
        for project in self.project_store.get_projects(self.module):
            location = self.find_definition(node, project)
            if isinstance(location, Location):
                # here we recurse into the hashing function
                self.hash_repr = self.hasher.hash_location(location, project)
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
