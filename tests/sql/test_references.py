from pycodehash.sql import WhitespaceFilter
from pycodehash.sql.references import (
    EnrichedTableReferenceVisitor,
    TableReferenceVisitor,
    _table_reference_to_string,
    extract_table_references,
)
from sqlfluff import parse


def test_table_reference_to_string():
    assert _table_reference_to_string({"naked_identifier": "my_table"}) == "my_table"
    assert (
        _table_reference_to_string([{"naked_identifier": "src"}, {"dot": "."}, {"naked_identifier": "my_table"}])
        == "src.my_table"
    )


def test_find_table_references():
    query = {
        "file": [
            {
                "statement": {
                    "create_table_statement": [
                        {"keyword": "CREATE"},
                        {"whitespace": " "},
                        {"keyword": "TABLE"},
                        {"whitespace": " "},
                        {"table_reference": {"naked_identifier": "db.my_table"}},
                        {"whitespace": " "},
                        {"keyword": "AS"},
                        {"whitespace": " "},
                        {
                            "select_statement": {
                                "select_clause": {
                                    "keyword": "SELECT",
                                    "whitespace": " ",
                                    "select_clause_element": {
                                        "wildcard_expression": {"wildcard_identifier": {"star": "*"}}
                                    },
                                },
                                "whitespace": " ",
                                "from_clause": {
                                    "keyword": "FROM",
                                    "whitespace": " ",
                                    "from_expression": {
                                        "from_expression_element": {
                                            "table_expression": {
                                                "table_reference": {"naked_identifier": "db.that_table"}
                                            }
                                        }
                                    },
                                },
                            }
                        },
                    ]
                }
            },
            {"statement_terminator": ";"},
            {"whitespace": " "},
            {
                "statement": {
                    "select_statement": {
                        "select_clause": {
                            "keyword": "SELECT",
                            "whitespace": " ",
                            "select_clause_element": {"wildcard_expression": {"wildcard_identifier": {"star": "*"}}},
                        },
                        "whitespace": " ",
                        "from_clause": {
                            "keyword": "FROM",
                            "whitespace": " ",
                            "from_expression": {
                                "from_expression_element": {
                                    "table_expression": {"table_reference": {"naked_identifier": "db.my_table"}}
                                }
                            },
                        },
                    }
                }
            },
        ]
    }

    v = TableReferenceVisitor()
    v.generic_visit(query)
    assert v.references == ["db.my_table", "db.that_table", "db.my_table"]
    assert extract_table_references(query) == {"db.my_table", "db.that_table"}

    ev = EnrichedTableReferenceVisitor()
    ev.generic_visit(query)
    assert ev.references == [("CREATE", "db.my_table"), ("FROM", "db.that_table"), ("FROM", "db.my_table")]


def test_enriched_table_reference_visitor_cte():
    query = """CREATE TABLE output_table AS (
        WITH intermediate_table AS (
            SELECT
                *
            FROM sdb.source_table1 AS st1
            LEFT JOIN sdb.source_table2 AS st2 ON st1.record_id = st2.record_id
            LEFT JOIN sdb.source_table3 AS st3 ON st1.record_id = st3.record_id
        ),
        another_intermediate_table AS (
            SELECT * FROM hello_world
        ),

        SELECT
            *
        FROM
            intermediate_table
    )
    """
    ast = parse(query, dialect="sparksql")
    ev = EnrichedTableReferenceVisitor()
    ev.generic_visit(ast)
    assert ev.references == [
        ("CREATE", "output_table"),
        ("CTE", "intermediate_table"),
        ("FROM", "sdb.source_table1"),
        ("FROM", "sdb.source_table2"),
        ("FROM", "sdb.source_table3"),
        ("CTE", "another_intermediate_table"),
        ("FROM", "hello_world"),
        ("FROM", "intermediate_table"),
    ]

    # Without whitespace should yield identical results
    ast = WhitespaceFilter().transform(ast)
    ewv = EnrichedTableReferenceVisitor()
    ewv.generic_visit(ast)
    assert ewv.references == ev.references
