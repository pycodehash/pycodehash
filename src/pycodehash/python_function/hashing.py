"""Functionality to hash the function body."""
from __future__ import annotations

from types import BuiltinFunctionType, FunctionType
from typing import TYPE_CHECKING

from pycodehash.hashing import hash_string
from pycodehash.python_function import (
    DocstringStripper,
    FunctionStripper,
    LinesTransformer,
    TypeHintStripper,
    WhitespaceNormalizer,
)
from pycodehash.python_function.stores import FunctionCallStore, FunctionStore, ModuleStore, ProjectStore
from pycodehash.python_function.tracing import get_func_def_location, get_func_node_from_location
from pycodehash.python_function.transfomers import HashCallNameTransformer
from pycodehash.python_function.unparse import _unparse
from pycodehash.python_function.utils import get_func_name

if TYPE_CHECKING:
    from ast import NodeTransformer

    from rope.base.project import Project
    from rope.contrib.findit import Location


class FunctionHasher:
    """Function hashing algorithm.

    Main entry point for hashing functions.
    It provides a deterministic hash that reflects changes to the function itself
    but also to functions that are called and in scope.
    The scope is the first-party library by default but more packages can be set.

    Attributes:
        func_store: container that caches hashed functions
        module_store: container that caches the AST representations of the modules
        project_store: container that caches analyzed packages
        ast_transformers: NodeTransformer for the `ast` module to be applied to function's AST representation
        lines_transformers: set of functions to be applied to the textual representation
        func_ir_store: container that store the intermediate representations of functions
    """

    func_store: FunctionStore
    module_store: ModuleStore
    project_store: ProjectStore
    ast_transformers: list[NodeTransformer]
    lines_transformers: list[LinesTransformer]
    func_ir_store: FunctionStore

    def __init__(
        self,
        packages: list[str] | None = None,
        ast_transformers: list | None = None,
        lines_transformers: list | None = None,
    ):
        """Initialise the class.

        Args:
            packages: list of packages to trace.
                By default we only trace within the first-party library, aka for a function `liba.foo`
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
        self.ast_transformers = ast_transformers or [FunctionStripper(), DocstringStripper(), TypeHintStripper()]
        self.lines_transformers = lines_transformers or [WhitespaceNormalizer()]
        # Function store is re-used to store the intermediate representation (IR)
        # of the function that is hashed. Not strictly needed but does make debugging
        # or evaluation a lot easier.
        self.func_ir_store = FunctionStore()
        # stores the location(s) of the calls in a given function definition
        self.func_call_store = FunctionCallStore()

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
            return self.func_store[location]

        # get the code for the function
        src_node = get_func_node_from_location(location, project)

        # replace names of _tracked_ calls
        src_node = HashCallNameTransformer(self, location).visit(src_node)

        # preprocessing of AST
        for ast_transformer in self.ast_transformers:
            src_node = ast_transformer.visit(src_node)

        prc_src = _unparse(src_node)

        # preprocessing of the lines
        for line_transformer in self.lines_transformers:
            prc_src = line_transformer.transform(prc_src)

        function_hash = hash_string(prc_src)
        self.func_ir_store[location] = prc_src
        self.func_store[location] = function_hash
        return function_hash

    def _get_location_and_project(self, func: FunctionType) -> tuple[Location, Project]:
        """Hash a Python function.

        Args:
            func: the Python function

        Raises:
            TypeError: when `func` is a `BuiltinFunctionType` as these do not have accessible source code
            ValueError: when the source code for `func` cannot be found but it is not a `BuiltinFunctionType`

        Returns:
            location, project: the location of the function definition and the project it belongs to

        """
        # exit path for when we cannot hash the source
        if isinstance(func, BuiltinFunctionType):
            msg = f"builtin function `{get_func_name(func)}` cannot be hashed as there is no Python source code."
            raise TypeError(msg)

        project = self.project_store.get_or_create_for_func(func)

        # get the location (~text range) from the function using the project
        location = get_func_def_location(func, project)
        if location is None:
            msg = f"Source code for function `{get_func_name(func)}` could not be found or does not exist."
            raise ValueError(msg)

        return location, project

    def hash_func(self, func: FunctionType) -> str:
        """Hash a Python function.

        Args:
            func: the Python function

        Raises:
            TypeError: when `func` is a `BuiltinFunctionType` as these do not have accessible source code
            ValueError: when the source code for `func` cannot be found but it is not a `BuiltinFunctionType`

        Returns:
            The hash of the function

        """
        return self.hash_location(*self._get_location_and_project(func))

    def get_func_location(self, func: FunctionType) -> Location | None:
        """Get the rope.Location of a function.

        The location can be used to access the function and ir function store.

        Args:
            func: the Python function

        Raises:
            TypeError: when `func` is a `BuiltinFunctionType` as these do not have accessible source code
            ValueError: when the source code for `func` cannot be found but it is not a `BuiltinFunctionType`

        Returns:
            location: location of the function definition if found otherwise None
        """
        location, _ = self._get_location_and_project(func)
        return location
