"""Extract references to input and output tables in the SQL AST"""

from __future__ import annotations

from sqllineage.runner import LineageRunner


def _table_reference_to_string(reference: list | dict) -> str:
    if isinstance(reference, list):
        return "".join(_table_reference_to_string(token) for token in reference)
    if isinstance(reference, dict):
        assert len(reference) == 1
        return list(reference.values())[0]
    msg = "Expected list or dict"
    raise TypeError(msg)


def _create_fqtn(table: str, default_db: str) -> str:
    return table.replace("<default>", default_db)


def extract_table_references(query: str, default_db: str, dialect: str) -> tuple[set[str], set[str], set[str]]:
    """Extract table references from the query

    Args:
        query: SQL query to extract the references from
        default_db: the default database name (e.g. `dbo`). This is used to create the fully qualified table name.
        dialect: SQL dialect

    Returns:
        three sets, of input tables, output tables and dropped tables
    """
    result = LineageRunner(query, dialect=dialect, verbose=True)
    inlets = {_create_fqtn(str(table), default_db) for table in result.source_tables}
    outlets = {_create_fqtn(str(table), default_db) for table in result.target_tables}
    dropped = {_create_fqtn(str(table), default_db) for holder in result._stmt_holders for table in holder.drop}
    return inlets, outlets, dropped
