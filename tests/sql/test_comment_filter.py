from pycodehash.sql.comment_filter import CommentFilter


def test_comment_filter():
    query = {
        "file": {
            "statement": {
                "create_table_as_statement": [
                    {"keyword": "CREATE"},
                    {"whitespace": " "},
                    {"keyword": "TABLE"},
                    {"whitespace": " "},
                    {"table_reference": {"naked_identifier": "my_table"}},
                    {"whitespace": " "},
                    {"keyword": "AS"},
                    {"newline": "\n"},
                    {"newline": "\n"},
                    {
                        "select_statement": [
                            {
                                "select_clause": [
                                    {"keyword": "SELECT"},
                                    {"newline": "\n"},
                                    {"whitespace": " "},
                                    {"inline_comment": "-- select all columns"},
                                    {"newline": "\n"},
                                    {"whitespace": " "},
                                    {
                                        "select_clause_element": {
                                            "wildcard_expression": {"wildcard_identifier": {"star": "*"}}
                                        }
                                    },
                                ]
                            },
                            {"newline": "\n"},
                            {
                                "from_clause": {
                                    "keyword": "FROM",
                                    "newline": "\n",
                                    "whitespace": "    ",
                                    "from_expression": {
                                        "from_expression_element": {
                                            "table_expression": {
                                                "table_reference": {"naked_identifier": "another_table"}
                                            }
                                        }
                                    },
                                }
                            },
                            {"newline": "\n"},
                            {
                                "groupby_clause": [
                                    {"keyword": "GROUP"},
                                    {"whitespace": " "},
                                    {"keyword": "BY"},
                                    {"newline": "\n"},
                                    {"whitespace": "    "},
                                    {"column_reference": {"naked_identifier": "column1"}},
                                    {"comma": ","},
                                    {"block_comment": "/*column2*/"},
                                    {"column_reference": {"naked_identifier": "column3"}},
                                ]
                            },
                        ]
                    },
                ]
            },
            "newline": "\n",
        }
    }

    expected = {
        "file": {
            "statement": {
                "create_table_as_statement": [
                    {"keyword": "CREATE"},
                    {"whitespace": " "},
                    {"keyword": "TABLE"},
                    {"whitespace": " "},
                    {"table_reference": {"naked_identifier": "my_table"}},
                    {"whitespace": " "},
                    {"keyword": "AS"},
                    {"newline": "\n"},
                    {"newline": "\n"},
                    {
                        "select_statement": [
                            {
                                "select_clause": [
                                    {"keyword": "SELECT"},
                                    {"newline": "\n"},
                                    {"whitespace": " "},
                                    {"newline": "\n"},
                                    {"whitespace": " "},
                                    {
                                        "select_clause_element": {
                                            "wildcard_expression": {"wildcard_identifier": {"star": "*"}}
                                        }
                                    },
                                ]
                            },
                            {"newline": "\n"},
                            {
                                "from_clause": {
                                    "keyword": "FROM",
                                    "newline": "\n",
                                    "whitespace": "    ",
                                    "from_expression": {
                                        "from_expression_element": {
                                            "table_expression": {
                                                "table_reference": {"naked_identifier": "another_table"}
                                            }
                                        }
                                    },
                                }
                            },
                            {"newline": "\n"},
                            {
                                "groupby_clause": [
                                    {"keyword": "GROUP"},
                                    {"whitespace": " "},
                                    {"keyword": "BY"},
                                    {"newline": "\n"},
                                    {"whitespace": "    "},
                                    {"column_reference": {"naked_identifier": "column1"}},
                                    {"comma": ","},
                                    {"column_reference": {"naked_identifier": "column3"}},
                                ]
                            },
                        ]
                    },
                ]
            },
            "newline": "\n",
        }
    }

    result = CommentFilter().generic_transform(query)
    assert result == expected
