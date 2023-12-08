from pycodehash.sql.references import (
    EnrichedTableReferenceVisitor,
    TableReferenceVisitor,
    _table_reference_to_string,
    extract_table_references,
)


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
