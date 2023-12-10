"""Extract references to input and output tables in the SQL AST"""
from __future__ import annotations

from pycodehash.sql.ast_visitor import ASTVisitor


def _table_reference_to_string(reference: list | dict) -> str:
    if isinstance(reference, list):
        return "".join(_table_reference_to_string(token) for token in reference)
    if isinstance(reference, dict):
        assert len(reference) == 1
        return list(reference.values())[0]
    msg = "Expected list or dict"
    raise TypeError(msg)


def extract_table_references(ast: dict) -> set[str]:
    """Extract the table references from SQL AST

    Args:
        ast: the `sqlfluff` parsed AST

    Returns:
        unique table references
    """
    visitor = TableReferenceVisitor()
    visitor.generic_visit(ast)
    return set(visitor.references)


class TableReferenceVisitor(ASTVisitor):
    def __init__(self):
        self.references = []
        super().__init__()

    def visit_table_reference(self, node: dict):
        self.references.append(_table_reference_to_string(node))


class EnrichedTableReferenceVisitor(ASTVisitor):
    def __init__(self):
        self.references = []
        self.mode = None
        super().__init__()

    def visit_table_reference(self, node: dict | list):
        self.references.append((self.mode, _table_reference_to_string(node)))
        self.mode = None

    def visit_create_table_statement(self, node: dict | list):
        self.mode = "CREATE"
        self.generic_visit(node)

    def visit_from_expression_element(self, node: dict | list):
        self.mode = "FROM"
        self.generic_visit(node)

    def visit_common_table_expression(self, node: dict | list):
        if isinstance(node, dict) and "naked_identifier" in node:
            self.references.append(("CTE", node["naked_identifier"]))
        # AST is structured this way when there are multiple nodes of the same type, e.g. `whitespace`
        if isinstance(node, list):
            for item in node:
                if "naked_identifier" in item:
                    self.references.append(("CTE", item["naked_identifier"]))
        self.generic_visit(node)
