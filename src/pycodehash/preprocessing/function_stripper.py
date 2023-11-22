from __future__ import annotations

import ast
import logging
from ast import NodeTransformer

logger = logging.getLogger(__name__)


class FunctionStripper(NodeTransformer):
    """Removes docstring node from function and class definitions."""

    def visit_FunctionDef(self, node: ast.FunctionDef):
        logger.debug(f"Replace function name `{node.name}` with `_`")
        node.name = "_"
        return node
