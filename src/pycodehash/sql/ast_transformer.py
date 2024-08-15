from __future__ import annotations

from abc import ABC
from typing import Any


def _flatten(data: list[dict[Any, Any]]) -> dict[Any, Any]:
    return {k: v for d in data for k, v in d.items()}


def _should_flatten(data: list[Any]) -> bool:
    if any(not isinstance(v, dict) for v in data):
        return False

    keys = [x for v in data for x in list(v.keys())]
    return len(keys) == len(set(keys))


class ASTTransformer(ABC):
    """Base class for transforming based on the AST"""

    def transform(self, key: str, value: Any) -> Any:
        method = f"transform_{key}"
        if hasattr(self, method):
            return getattr(self, method)(value)
        if isinstance(value, (dict, list)):
            return self.generic_transform(value)

        return value

    def generic_transform(self, node: dict[str, Any] | list[dict[str, Any]] | None):
        """Called if no explicit visitor function exists for a node."""

        if node is None:
            return None

        if isinstance(node, list):
            transformed_list = [self.generic_transform(item) for item in node]
            transformed_list = [value for value in transformed_list if value is not None]
            # SQLFluff parses clauses with non-unique dict keys (e.g. newline) as a list of dicts
            # When after stripping whitespace and newlines the keys are distinct, we should try to flatten
            if _should_flatten(transformed_list):
                return _flatten(transformed_list)
            return transformed_list
        if isinstance(node, dict):
            transformed_dict = {key: self.transform(key, value) for key, value in node.items()}
            transformed_dict = {key: value for key, value in transformed_dict.items() if value is not None}
            if transformed_dict:
                return transformed_dict
            return None

        msg = "AST invalid"
        raise TypeError(msg)
