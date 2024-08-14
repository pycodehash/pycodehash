from pycodehash.sql.default_database_filter import DefaultDatabaseFilter


def test_default_database_filter():
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
                                "table_expression": {"table_reference": {"naked_identifier": "templates"}}
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
                                        {"naked_identifier": "hello_world"},
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
    result = DefaultDatabaseFilter("hello_world").generic_transform(query)
    assert result == expected


def test_default_database_filter_using():
    query = {
        "file": {
            "batch": [
                {
                    "statement": {
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
                                        "table_expression": {"table_reference": {"naked_identifier": "hello_world"}}
                                    }
                                },
                                "statement_terminator": ";",
                            },
                        }
                    }
                },
                {"whitespace": " "},
                {
                    "statement": {
                        "use_statement": {
                            "keyword": "USE",
                            "whitespace": " ",
                            "database_reference": {"naked_identifier": "your_database"},
                        }
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
                                        "table_expression": {"table_reference": {"naked_identifier": "hello_world"}}
                                    }
                                },
                            },
                        }
                    }
                },
            ]
        }
    }

    expected = {
        "file": {
            "batch": [
                {
                    "statement": {
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
                                            "table_reference": [
                                                {"naked_identifier": "foobar"},
                                                {"dot": "."},
                                                {"naked_identifier": "hello_world"},
                                            ]
                                        }
                                    }
                                },
                                "statement_terminator": ";",
                            },
                        }
                    }
                },
                {"whitespace": " "},
                {
                    "statement": {
                        "use_statement": {
                            "keyword": "USE",
                            "whitespace": " ",
                            "database_reference": {"naked_identifier": "your_database"},
                        }
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
                                            "table_reference": [
                                                {"naked_identifier": "your_database"},
                                                {"dot": "."},
                                                {"naked_identifier": "hello_world"},
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
    }

    result = DefaultDatabaseFilter("foobar").generic_transform(query)
    assert result == expected
