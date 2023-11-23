"""Functionality to hash the function body."""
from __future__ import annotations

import hashlib
import inspect
import logging
from typing import Callable

from rope.base.project import Project
from rope.contrib.findit import Location

from pycodehash.tracing.stores import FunctionStore, ModuleStore, ProjectStore
from pycodehash.tracing.transfomers import HashCallNameTransformer
from pycodehash.utils import get_func_def_location, get_func_node_from_location
from pycodehash.unparse import _unparse


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
        self.ast_transformers = ast_transformers or []
        self.lines_transformers = lines_transformers or []

    def hash_location(self, location: Location, project: Project) -> str:
        """Hash a location (~text range) of Python code

        Args:
            location: rope Location
            project: rope Project

        Returns:
            Hash string based on the location
        """
        # check if the location was already hashed, if so return
        if location in self.func_store.store:
            return self.func_store[location]

        # get the code for the function
        src_node = get_func_node_from_location(location, project)

        # replace names of _tracked_ calls
        src_node = HashCallNameTransformer(self).visit(src_node)

        # Preprocessing of AST
        for transformer in self.ast_transformers:
            src_node = transformer.visit(src_node)

        prc_src = _unparse(src_node)

        for transformer in self.lines_transformers:
            prc_src = transformer.transform(prc_src)

        logger.debug(f"lines-preprocessed source `{prc_src}`")

        function_hash = hash_string(prc_src)
        self.func_store[location] = function_hash
        return function_hash

    def hash_func(self, func: Callable) -> str:
        """Hash a Python function

        Args:
            func: the Python function

        Returns:
            The hash of the function
        """
        logger.debug(f"Hashing `{func.__name__}`")

        # get the module from the function
        module = inspect.getmodule(func)
        # get module view from module store
        mview = self.module_store.get(module)
        # get projects from project store
        project = self.project_store.get(mview.pkg)

        location = get_func_def_location(func, project)
        return self.hash_location(location, project)
