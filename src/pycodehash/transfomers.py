"""Visitors used in call tracing."""
from __future__ import annotations

import ast
from ast import NodeTransformer

from rope.contrib.findit import Location

from pycodehash.stores import ModuleView, ProjectStore
from pycodehash.utils import find_call_definition


def _contains_call(node: ast.Expr):
    return any(isinstance(child, ast.Call) for child in ast.walk(node))


class HashCallNameTransformer(NodeTransformer):
    """Replace the function names in a call with the hash of that call"""

    def __init__(self, hasher, location: Location):
        self.hasher = hasher
        self.project_store: ProjectStore = hasher.project_store

        projects = self.project_store.get_projects()
        for project in projects:
            module = project.get_pymodule(location.resource)
            if module is not None:
                break
        self.module: ModuleView = self.hasher.module_store[module]
        self.hash_repr = None

    def visit_Call(self, node: ast.Call):
        """Find the hash each call"""
        # iterate over the projects until we find the location.
        # the first project is the one to which the module belongs.
        projects = self.project_store.get_projects(self.module)
        for project in projects:
            location = find_call_definition(node, self.module, project)

            if isinstance(location, Location):
                # here we recurse into the hashing function
                self.hash_repr = self.hasher.hash_location(location, project)
                if isinstance(node.func, ast.Attribute) and not _contains_call(node.func):
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
