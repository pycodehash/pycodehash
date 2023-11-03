"""Functionality to hash the function body."""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
from ast import FunctionDef, NodeVisitor
from types import FunctionType

from pycodehash.preprocessing import (
    DocstringStripper,
    FunctionStripper,
    TypeHintStripper,
    WhitespaceNormalizer,
)
from pycodehash.tracing.utils import get_func_location
from pycodehash.unparse import _unparse


def hash_string(input_string: str) -> str:
    """Compute SHA256 hash of input string.

    Args:
        input_string: the string to hash

    Returns:
        SHA256 hashed string
    """
    return hashlib.sha256(input_string.encode("utf-8")).hexdigest()


def hash_func_params(keywords: tuple[str], args: tuple[any], kwargs: dict[str, any]) -> str:
    """Hash args and kwargs of a function.

    Note that the params should adhere to the JSON specification.

    Args:
        keywords: function parameter names
        args: arguments passed
        kwargs: keyword arguments passed

    Returns:
        hash representation of input parameters

    """
    params = {keywords[i]: arg for i, arg in enumerate(args)}
    params.update(kwargs)
    return hash_string(json.dumps(params, ensure_ascii=False))


# TODO: replace with new algo
class FuncNodeHasher(NodeVisitor):
    """
    Create SHA256 hash of all function nodes.

    A sequence of preprocessing steps is applied to the code
    to ensure that equivalent code generates identical hashes.

    The following preprocessing steps are taken:
    - set function name to "_" (see FunctionStripper)
    - remove docstring (see DocstringStripper)
    - remove type annotations (see TypehintStripper)
    - strip white-space (See WhitespaceNormalizer)
    - strip line-endings (See WhitespaceNormalizer)
    """

    def __init__(self):
        self.strings: dict[str, str] = {}
        self.hashes: dict[str, str] = {}
        self.ast_transformers = [
            FunctionStripper(),
            DocstringStripper(),
            TypeHintStripper(),
        ]
        self.lines_transformers = [
            WhitespaceNormalizer(),
        ]

    def visit_FunctionDef(self, node: FunctionDef):
        super().generic_visit(node)

        # Save node name before it is stripped
        name = node.name

        # Preprocessing of AST
        for transformer in self.ast_transformers:
            node = transformer.visit(node)

        # Preprocessing of Lines
        src = _unparse(node)
        for transformer in self.lines_transformers:
            src = transformer.transform(src)
        self.strings[name] = src

        # Hashing
        self.hashes[name] = hash_string(self.strings[name])


def hash_function(
    func: FunctionType, func_store, module_store, project_store, ast_transformers, lines_transformers
) -> str:
    src = inspect.getsource(func)
    module = inspect.getmodule(func)
    src_node = ast.parse(src)
    # get module view from module store
    mview = module_store.get(module)
    ...
    # get projects from project store
    project = project_store.get(mview.pkg)

    location = get_func_location(src, src_node, project)
    if location in func_store:
        return func_store[location]

    # replace names of _tracked_ calls
    src_node = HashCallNameTransformer(func_store, module_store, project_store).visit(src_node)
    # Preprocessing of AST
    for transformer in ast_transformers:
        src_node = transformer.visit(src_node)
    prc_src = _unparse(src_node)
    for transformer in lines_transformers:
        prc_src = transformer.transform(prc_src)
    hash = hash_string(prc_src)
    func_store[location] = hash
    return hash
