from __future__ import annotations

from pycodehash.sql.ast_transformer import ASTTransformer


class WhitespaceFilter(ASTTransformer):
    """Whitespace and newlines are removed"""

    @staticmethod
    def transform_whitespace(value: str):
        return None

    @staticmethod
    def transform_newline(value: str):
        return None
