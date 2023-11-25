"""Functionality to hash the function body."""
from __future__ import annotations

import hashlib
from typing import Callable

from rope.base.project import Project
from rope.contrib.findit import Location

from pycodehash.preprocessing import DocstringStripper, FunctionStripper, TypeHintStripper, WhitespaceNormalizer
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
    def __init__(
        self,
        ast_transformers: list | None = None,
        lines_transformers: list | None = None,
        func_store: FunctionStore | None = None,
        module_store: ModuleStore | None = None,
        project_store: ProjectStore | None = None,
    ):
        self.func_store = func_store or FunctionStore()
        self.module_store = module_store or ModuleStore()
        self.project_store = project_store or ProjectStore()
        self.ast_transformers = ast_transformers or [
            FunctionStripper(),
            DocstringStripper(),
            TypeHintStripper(),
        ]
        self.lines_transformers = lines_transformers or [
            WhitespaceNormalizer(),
        ]
        self.func_ir_store = FunctionStore()

    def hash_location(self, location: Location, project: Project) -> str:
        """Hash a location (~text range) of Python code

        Args:
            location: rope Location
            project: rope Project

        Returns:
            Hash string based on the location
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
        """

        Args:
            func: the Python function

        Returns:
            The hash of the function
        """
        location, _ = self._get_location_and_project(func)
        return location
