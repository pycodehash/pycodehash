from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from sqlfluff import parse

from pycodehash.datasets.approximate_hasher import inline_metadata
from pycodehash.hashing import hash_string
from pycodehash.sql.whitespace_filter import WhitespaceFilter

if TYPE_CHECKING:
    from pycodehash.sql.ast_transformer import ASTTransformer


class SQLHasher:
    """Hash an SQL file or query using `SQLFluff <https://docs.sqlfluff.com/en/stable/index.html>`_."""

    def __init__(
        self,
        ast_transformers: list[ASTTransformer] | None = None,
        dialect: str = "ansi",
        config_path: str | None = None,
    ):
        """Initialize the SQLHasher object

        Args:
            ast_transformers: a list of ASTTransformers for SQL
            dialect: SQLFluff `dialect <https://docs.sqlfluff.com/en/stable/dialects.html>`_
            config_path: SQLFLuff `config path <https://docs.sqlfluff.com/en/stable/configuration.html>`_
        """
        self.dialect = dialect
        self.config_path = config_path
        self.ast_transformers = ast_transformers or [WhitespaceFilter()]

    def hash_file(self, file_path: Path | str):
        """Hash the query in a file

        Args:
            file_path: location of the file

        Returns:
            String hash of the query in the file
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        query = file_path.read_text()
        return self.hash_query(query)

    def hash_query(self, query: str):
        """Hash an SQL query

        Args:
            query: query

        Returns:
            String hash of the query
        """
        ast = parse(query, dialect=self.dialect, config_path=self.config_path)
        for transformer in self.ast_transformers:
            ast = transformer.transform(ast)

        data = inline_metadata(ast)

        return hash_string(data)
