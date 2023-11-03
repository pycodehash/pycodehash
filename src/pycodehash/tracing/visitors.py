# TODO: obviated
"""Visitors used in call tracing."""
from __future__ import annotations

import ast
from ast import NodeTransformer, NodeVisitor

from rope.base.libutils import path_to_resource
from rope.contrib.findit import Location, find_definition

from pycodehash.hashing import hash_string
from pycodehash.tracing.stores import ModuleView, ProjectStore


class HashCalls(NodeTransformer):
    def find_definition(self, node, project) -> Location | None:
        loc = find_definition(project, self.module.code, self.module.tree_tokens.get_text_range(node)[0])
        if isinstance(loc, Location) and loc.resource is None:
            loc.resource = path_to_resource(project, self.module.path)
        return loc

    def visit_Call(self, node: ast.Call):
        # call a function that hashes the source of the function
        self.hash_repr = hash_string(ast.unparse(node))
        super().generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name):
        if self.hash_repr is not None:
            node.id = self.hash_repr
            self.hash_repr = None
        return node


class CallDefinitionTracer(NodeVisitor):
    """Collect the definitions of all calls in the tree that can be found in the projects.

    Attributes:
        calls (list[rope.contrib.findit.Location]): the found locations
    """

    def __init__(self, projects: ProjectStore, module: ModuleView):
        self.calls: list[tuple[ast.Call, Location]] = []
        self.module = module
        self.projects = projects

    def find_definition(self, node, project) -> Location | None:
        loc = find_definition(project, self.module.code, self.module.tree_tokens.get_text_range(node)[0])
        if isinstance(loc, Location) and loc.resource is None:
            loc.resource = path_to_resource(project, self.module.path)
        return loc

    def visit_Call(self, node: ast.Call):
        # iterate over the projects until we find the location.
        # the first project is the one to which the module belongs.
        for project in self.projects.get_projects(self.module):
            location = self.find_definition(node, project)
            if isinstance(location, Location):
                self.calls.append((node, location))
                break

        super().generic_visit(node)


class ImportCollector(NodeVisitor):
    """Collect fully qualified names of imports.

    Attributes:
        imports: the call name as the key and the fully qualified name as value.
    """

    def __init__(self):
        """Initialise the visitor."""
        self.imports: dict[str, dict[str]] = {}

    def visit_Import(self, node: ast.Import):
        """Visit each name of an Import."""
        for n in node.names:
            self.visit_alias(n)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Visit each name of an ImportFrom."""
        for n in node.names:
            self.visit_alias_with_mod(node, node.module)

    def visit_alias(self, node: ast.alias):
        """Extract name and qualified name from alias."""
        name = node.asname or node.name.split(".")[-1]
        self.imports[name] = node.name

    def visit_alias_with_mod(self, node: ast.alias, module: str):
        """Extract name and qualified name from alias and module name."""
        name = node.asname or node.name.split(".")[-1]
        self.imports[name] = f"{module}.{node.name}"


class LocalImportCollector(NodeVisitor):
    """Collect non-module level imports.

    Attributes:
        imports: the imports per definition (key) where the value is a dict.
            The inner dict has the call name as the key and the fully qualified
            name as value.
    """

    def __init__(self):
        """Initialise the visitor."""
        self.imports: dict[str, dict[str]] = {}
        self._local_imports: dict[str] = {}
        self._collector = ImportCollector()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Collect imports from function definitions."""
        self._collector.visit(node)
        if len(self._collector.imports) > 0:
            self.imports[node.name] = self._collector.imports
            self._collector.imports = {}

    def visit_AsyncFunctionDef(self, node: ast.FunctionDef):
        """Collect imports from async function definitions."""
        self._collector.visit(node)
        if len(self._collector.imports) > 0:
            self.imports[node.name] = self._collector.imports
            self._collector.imports = {}


class ModuleImportCollector(ImportCollector):
    """Collect imports at top level.

    Note this visitor skips nested imports by overwriting
    note types that can have import nodes as descendants.

    Attributes:
        imports: the call name as the key and the fully qualified name as value.
    """

    def visit_FunctionDef(self, node: ast.ClassDef):
        """Block FunctionDef traversal."""
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Block AsyncFunctionDef traversal."""
        return

    def visit_ClassDef(self, node: ast.ClassDef):
        """Block ClassDef traversal."""
        return
