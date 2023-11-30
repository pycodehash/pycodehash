from pycodehash.sql.whitespace_filter import WhitespaceFilter


def test_whitespace_filter():
    query = {
        "file": {
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
        }
    }
    expected = {
        "file": {
            "statement": {
                "select_statement": {
                    "select_clause": {
                        "keyword": "SELECT",
                        "select_clause_element": {"wildcard_expression": {"wildcard_identifier": {"star": "*"}}},
                    },
                    "from_clause": {
                        "keyword": "FROM",
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
        }
    }
    result = WhitespaceFilter().transform(query)
    assert result == expected
