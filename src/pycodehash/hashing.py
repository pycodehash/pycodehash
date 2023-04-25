# Functionality to hash the function body
from __future__ import annotations

from ast import NodeVisitor, FunctionDef
import hashlib

from pycodehash.unparse import _unparse
from pycodehash.preprocessing import (
    FunctionStripper,
    DocstringStripper,
    TypeHintStripper,
    WhitespaceNormalizer,
)


def hash_string(input_string: str) -> str:
    """SHA256 hash of input string

    Args:
        input_string: the string to hash

    Returns:
        SHA256 hashed string
    """
    return hashlib.sha256(input_string.encode("utf-8")).hexdigest()


class FuncNodeHasher(NodeVisitor):
    """
    Create SHA256 hash of all function nodes.

    A sequence of preprocessing steps is applied to the code
    to ensure that equivalent code generates identical hashes.

    The following preprocessing steps are taken:
    - set function name to "_" (see FunctionStripper)
    - remove docstring (see DocstringStripper)
    - remove type annotations (see TypehintStripper)
    - strip whitespace (See WhitespaceNormalizer)
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
