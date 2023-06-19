import ast

from pycodehash.preprocessing import FunctionStripper, DocstringStripper, TypeHintStripper, WhitespaceNormalizer
from pycodehash.unparse import _unparse


class Transformer:
    """
    A sequence of transformations is applied to the code
    to ensure that equivalent code generates identical hashes.

    The following preprocessing steps are taken:
    - set function name to "_" (see FunctionStripper)
    - remove docstring (see DocstringStripper)
    - remove type annotations (see TypehintStripper)
    - strip trailing white-space (See WhitespaceNormalizer)
    - strip line-endings (See WhitespaceNormalizer)
    """

    def __init__(self):
        self.ast_transformers = [
            FunctionStripper(),
            DocstringStripper(),
            TypeHintStripper(),
        ]
        self.lines_transformers = [
            WhitespaceNormalizer(),
        ]

    def transform(self, node: ast.Expr):
        # Preprocessing of AST
        for transformer in self.ast_transformers:
            node = transformer.visit(node)

        # Preprocessing of Lines
        src = _unparse(node)
        for transformer in self.lines_transformers:
            src = transformer.transform(src)

        return src

