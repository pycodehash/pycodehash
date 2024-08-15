from __future__ import annotations

from pycodehash.sql.ast_transformer import ASTTransformer


class CommentFilter(ASTTransformer):
    """Inline- and block comments are removed"""

    @staticmethod
    def transform_block_comment(value: str):
        return None

    @staticmethod
    def transform_inline_comment(value: str):
        return None
