"""Functionality to hash the function body."""

from __future__ import annotations

import tempfile
from pathlib import Path
from types import BuiltinFunctionType, FunctionType
from typing import TYPE_CHECKING, Any

from pycodehash.hashing import hash_string
from pycodehash.python_function import (
    DocstringStripper,
    FunctionStripper,
    ProjectSourceProcessor,
    RuffProcessor,
    RuffProjectProcessor,
    SourceProcessor,
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
        source_preprocessors: list of transformations to be applied to the source representation before
            the AST processors
        source_postprocessors: list of transformations to be applied to the source representation after
            the AST processors
        func_ir_store: container that store the intermediate representations of functions
    """

    func_store: FunctionStore
    module_store: ModuleStore
    project_store: ProjectStore
    source_preprocessors: list[ProjectSourceProcessor]
    ast_transformers: list[NodeTransformer]
    source_postprocessors: list[SourceProcessor]
    func_ir_store: FunctionStore
    use_tempdir: bool
    _data_path: Path | None

    def __init__(
        self,
        packages: list[str] | None = None,
        source_preprocessors: list[ProjectSourceProcessor] | None = None,
        ast_transformers: list[NodeTransformer] | None = None,
        source_postprocessors: list[SourceProcessor] | None = None,
        use_tempdir: bool = True,
    ):
        """Initialise the class.

        Args:
            packages: list of packages to trace.
                By default we only trace within the first-party library, aka for a function `liba.foo`
                we trace and hash all calls to functions in `liba`.
            ast_transformers: set of transformers to be applied to function's AST representation.
                They are ran before the `lines_transformers` and should inherit from `ast.NodeTransformer`
                By default these are: `DocstringStripper`, `FunctionStore`, `TypeHintStripper`
            source_preprocessors: list of transformations to be applied to the source representation after
                the AST processors. By default this is: `[RuffPathProcessor()]`
            source_postprocessors: list of transformations to be applied to the source representation after
                the AST processors. By default this is: `[WhitespaceNormalizer()]`
            use_tempdir: if True, copies project files to a temporary directory before processing (default: True)

        """
        if use_tempdir:
            temp_dir = tempfile.TemporaryDirectory()
            self._temp_dir = temp_dir
            self._data_path = Path(temp_dir.name)
        else:
            self._data_path = None

        self.func_store = FunctionStore()
        self.module_store = ModuleStore()
        self.source_preprocessors = source_preprocessors or [RuffProjectProcessor()]

        self.project_store = ProjectStore(self._data_path, self.source_preprocessors)
        if packages is not None:
            for pkg in packages:
                self.project_store.add_project(pkg)
        self.ast_transformers = ast_transformers or [FunctionStripper(), DocstringStripper(), TypeHintStripper()]
        self.source_postprocessors = source_postprocessors or [RuffProcessor(), WhitespaceNormalizer()]
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

        # postprocessing of the lines
        for source_postprocessor in self.source_postprocessors:
            prc_src = source_postprocessor.transform(prc_src)

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

    def __enter__(self):
        pass

    def __exit__(self, _: Any, __: Any, ___: Any) -> None:
        if self._data_path is not None:
            self._temp_dir.cleanup()
