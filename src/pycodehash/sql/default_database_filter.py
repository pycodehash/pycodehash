from __future__ import annotations

from typing import Any

from pycodehash.sql.ast_transformer import ASTTransformer


class DefaultDatabaseFilter(ASTTransformer):
    """Whitespace and newlines are removed"""

    def __init__(self, default_db: str | None = None):
        super().__init__()
        self.default_db = default_db

    def transform_table_reference(self, node: Any):
        FQTN_LEN = 3
        if isinstance(node, list) and len(node) == FQTN_LEN:
            return node
        if isinstance(node, dict) and len(node) == 1 and "naked_identifier" in node:
            return [{"naked_identifier": self.default_db}, {"dot": "."}, node]

        msg = "AST invalid"
        raise ValueError(msg)

    def transform_use_statement(self, node: Any):
        self.default_db = node["database_reference"]["naked_identifier"]
        return node
