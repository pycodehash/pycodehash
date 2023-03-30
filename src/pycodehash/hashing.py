# Functionality to hash the function body
from __future__ import annotations
import ast
import hashlib

if hasattr(ast, "unparse"):
    _unparse = ast.unparse
else:
    # when python 3.9 is common this dependency can be removed
    # as python 3.9 has the corresponding native function
    from astunparse import unparse as _unparse

from pycodehash.preprocessing import DocstringStripper, TypeHintStripper


def hash_string(input_string: str) -> str:
    """SHA256 hash of input string

    Args:
        input_string: the string to hash

    Returns:
        SHA256 hashed string
    """
    return hashlib.sha256(input_string.encode("utf-8")).hexdigest()


class FuncNodeHasher(ast.NodeVisitor):
    """Create SHA256 hash of all function nodes.
    Note the following preprocessing steps are taken:
        - set function name to "_"
        - remove docstring
        - remove type annotations
        - strip whitespace
        - strip line-endings

    """

    def __init__(self):
        self.hashes: dict[str, str] = {}
        self.docstring_stripper: DocstringStripper = DocstringStripper()
        self.typehint_stripper: TypeHintStripper = TypeHintStripper()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        super().generic_visit(node)
        name = node.name
        node.name = "_"
        node = self.docstring_stripper.visit(node)
        node = self.typehint_stripper.visit(node)
        # str.split will split on all whitespace and line-endings
        self.hashes[name] = hash_string("".join(_unparse(node).split()))
