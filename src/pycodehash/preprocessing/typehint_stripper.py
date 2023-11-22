from __future__ import annotations

import ast
import logging
from ast import NodeTransformer

logger = logging.getLogger(__name__)


class TypeHintStripper(NodeTransformer):
    """Removes the type hints in the function signature and function body."""

    def visit_FunctionDef(self, node):
        if node.returns is not None:
            logger.debug("Strip type hints from function")
            node.returns = None
        super().generic_visit(node)
        return node

    def visit_arg(self, node):
        if node.annotation is not None:
            logger.debug("Strip type hints from argument")
            node.annotation = None
        return node

    def visit_AnnAssign(self, node):
        if node.value is None:
            logger.debug("Strip type hints from assignment")
            return None
        return ast.Assign([node.target], node.value, lineno=node.lineno)
