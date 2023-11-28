"""Functionality to hash the function body."""
from __future__ import annotations

import hashlib
from typing import Callable

from rope.base.project import Project
from rope.contrib.findit import Location

from pycodehash.preprocessing import (
    DocstringStripper,
    FunctionStripper,
    TypeHintStripper,
    WhitespaceNormalizer,
)
from pycodehash.stores import FunctionStore, ModuleStore, ProjectStore
from pycodehash.transfomers import HashCallNameTransformer
from pycodehash.unparse import _unparse
from pycodehash.utils import get_func_def_location, get_func_node_from_location


def hash_string(input_string: str) -> str:
    """Compute SHA256 hash of input string.

    Args:
        input_string: the string to hash

    Returns:
        SHA256 hashed string
    """
    return hashlib.sha256(input_string.encode("utf-8")).hexdigest()


class FunctionHasher:
    """Function hashing algorithm.

    Main entry point for hashing functions.
    It provides a deterministic hash that reflects changes to the funtion itself
    but also to functions that are called and in scope.
    The scope is the first-party library by default but more packages can be set.

    Attributes:
        func_store (FunctionStore): container that caches hashed functions
        module_store (ModuleStore): container that caches ast representations of the mdoules
        project_store (ProjectStore): container that caches analyzed packages
        ast_transformers (list): set of ast.Transformers to be applied to function's AST representation
        lines_transformers (list): set of functions to be applied to the textual representation
        func_ir_store (FunctionStore): container that store the intermediate representations of functions
    """

    def __init__(
        self,
        packages: list[str] | None = None,
        ast_transformers: list | None = None,
        lines_transformers: list | None = None,
    ):
        """Initialise the class.

        Args:
            packages: list of packages to trace.
                By default we only trace within the first-party libary, aka for a function `liba.foo`
                we trace and hash all calls to functions in `liba`.
            ast_transformers: set of transformers to be applied to function's AST representation.
                They are ran before the `lines_transformers` and should inherit from `ast.NodeTransformer`
                By default these are: `DocstringStripper`, `FunctionStore`, `TypeHintStripper`
            lines_transformers: list of functions that transform the textual representation.
                By default this is: `WhitespaceNormalizer`

        """
        self.func_store = FunctionStore()
        self.module_store = ModuleStore()
        self.project_store = ProjectStore()
        if packages is not None:
            for pkg in packages:
                self.project_store.add_project(pkg)
        self.ast_transformers = ast_transformers or [
            FunctionStripper(),
            DocstringStripper(),
            TypeHintStripper(),
        ]
        self.lines_transformers = lines_transformers or [
            WhitespaceNormalizer(),
        ]
        # Function store is re-used to store the intermediate representation (IR)
        # of the function that is hashed. Not strictly needed but does make debugging
        # or evaluation a lot easier.
        self.func_ir_store = FunctionStore()

    def add_package_to_trace(self, pkg: str):
        """Analyze package s.t. functions in it can be traced.

        Args:
            pkg: the name of the package, must be importable
        """
        self.project_store.add_project(pkg)

    def hash_location(self, location: Location, project: Project) -> str:
        """Hash a location (~text range) of Python code

        Args:
            location: rope Location
            project: rope Project

        Returns:
            function_hash: hash string based on the location
        """
        # check if the location was already hashed, if so return
        if location in self.func_store:
            function_hash = self.func_store[location]
            return function_hash

        # get the code for the function
        src_node = get_func_node_from_location(location, project)

        # replace names of _tracked_ calls
        src_node = HashCallNameTransformer(self, location).visit(src_node)

        # preprocessing of AST
        for transformer in self.ast_transformers:
            src_node = transformer.visit(src_node)

        prc_src = _unparse(src_node)

        # preprocessing of the lines
        for transformer in self.lines_transformers:
            prc_src = transformer.transform(prc_src)

        function_hash = hash_string(prc_src)
        self.func_ir_store[location] = prc_src
        self.func_store[location] = function_hash
        return function_hash

    def _get_location_and_project(self, func: Callable) -> tuple[Location, Project]:
        project = self.project_store.get_from_func(func)
        # get the location (~text range) from the function using the project
        location = get_func_def_location(func, project)
        return location, project

    def hash_func(self, func: Callable) -> str:
        """Hash a Python function

        Args:
            func: the Python function

        Returns:
            The hash of the function
        """
        # compute the hash
        return self.hash_location(*self._get_location_and_project(func))

    def get_func_location(self, func: Callable) -> Location | None:
        """Get the rope.Location of a function.

        The location is can be used to access the function and ir function store.

        Args:
            func: the Python function

        Returns:
            location: location of the function definition if found otherwise None
        """
        location, _ = self._get_location_and_project(func)
        return location
