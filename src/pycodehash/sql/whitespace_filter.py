from __future__ import annotations

from typing import Any

from pycodehash.sql.ast_transformer import ASTTransformer


def _flatten(data: list[dict[Any, Any]]) -> dict[Any, Any]:
    return {k: v for d in data for k, v in d.items()}


def _should_flatten(data: list[Any]) -> bool:
    if any(not isinstance(v, dict) for v in data):
        return False

    keys = [x for v in data for x in list(v.keys())]
    return len(keys) == len(set(keys))


class WhitespaceFilter(ASTTransformer):
    """Whitespace and newlines are removed"""

    def transform(self, node: Any):
        if isinstance(node, dict):
            return {k: self.transform(v) for k, v in node.items() if k not in {"whitespace", "newline"}}
        if isinstance(node, list):
            data = [self.transform(v) for v in node]
            # Filter nones
            data = [v for v in data if v]

            # SQLFluff parses clauses with non-unique dict keys (e.g. newline) as a list of dicts
            # When after stripping whitespace and newlines the keys are distinct, we should try to flatten
            if _should_flatten(data):
                data = _flatten(data)  # type: ignore[assignment]
            return data
        return node
