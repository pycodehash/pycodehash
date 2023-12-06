"""Extract references to input and output tables in the SQL AST"""
from __future__ import annotations

from typing import Any


def _table_reference_to_string(reference: list | dict) -> str:
    if isinstance(reference, list):
        return "".join(_table_reference_to_string(token) for token in reference)
    if isinstance(reference, dict):
        assert len(reference) == 1
        return list(reference.values())[0]
    msg = "Expected list or dict"
    raise TypeError(msg)


def _find_table_references(sql_ast: dict[str, Any]) -> str:
    if isinstance(sql_ast, dict):
        for k, v in sql_ast.items():
            if k == "table_reference":
                yield _table_reference_to_string(v)
            if isinstance(v, dict):
                for result in _find_table_references(v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in _find_table_references(d):
                        yield result


def extract_table_references(ast: dict) -> set[str]:
    """Extract the table references from SQL AST

    Args:
        ast: the `sqlfluff` parsed AST

    Returns:
        unique table references
    """
    return set(_find_table_references(ast))
