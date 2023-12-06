from pycodehash.sql.references import _find_table_references, _table_reference_to_string, extract_table_references


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
                                    "table_expression": {
                                        "table_reference": [
                                            {"naked_identifier": "db"},
                                            {"dot": "."},
                                            {"naked_identifier": "templates"},
                                        ]
                                    }
                                }
                            },
                        },
                    }
                }
            },
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
                                    "table_expression": {
                                        "table_reference": [
                                            {"naked_identifier": "db"},
                                            {"dot": "."},
                                            {"naked_identifier": "templates"},
                                        ]
                                    }
                                }
                            },
                        },
                    }
                }
            },
        ]
    }
    assert list(_find_table_references(query)) == ["db.templates", "db.templates"]
    assert extract_table_references(query) == {"db.templates"}
