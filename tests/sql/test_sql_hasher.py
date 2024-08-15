from pathlib import Path

import pytest
from pycodehash.hashing import hash_string
from pycodehash.sql.comment_filter import CommentFilter
from pycodehash.sql.default_database_filter import DefaultDatabaseFilter
from pycodehash.sql.sql_hasher import SQLHasher
from pycodehash.sql.whitespace_filter import WhitespaceFilter


def test_sql_hasher():
    query = "SELECT * FROM table"
    sh = SQLHasher()
    hash_str = sh.hash_query(query)
    assert hash_str == "ba46f6c7ebf45fb57da743ef050869e1e45d32defe9da56e4593ba82c3305d8a"


def test_sql_database_filter():
    sh = SQLHasher(dialect="tsql", default_db="my_database")

    query_1 = "SELECT * FROM my_database.hello_world"
    query_2 = "SELECT * FROM hello_world"
    assert sh.hash_query(query_1) == sh.hash_query(query_2)


def test_sql_database_whitespace():
    sh = SQLHasher(dialect="tsql", default_db="my_database")

    query_1 = "SELECT \n * \n FROM    \n     hello_world"
    query_2 = "SELECT * FROM hello_world"
    assert sh.hash_query(query_1) == sh.hash_query(query_2)


def test_sql_database_filter_using():
    sh = SQLHasher(dialect="tsql", default_db="my_database")

    query = "USE your_database; SELECT * FROM hello_world"
    print(sh.hash_query(query))

    query = "USE your_database;SELECT * FROM your_database.hello_world"
    print(sh.hash_query(query))


@pytest.fixture(scope="function")
def query_file():
    query = "SELECT * FROM table"
    query_file = Path("query.sql")
    query_file.write_text(query)

    yield query_file

    query_file.unlink()


def test_sql_hasher_file(query_file):
    sh = SQLHasher()
    hash_str = sh.hash_file(query_file)
    assert hash_str == "ba46f6c7ebf45fb57da743ef050869e1e45d32defe9da56e4593ba82c3305d8a"

    hash_str = sh.hash_file(str(query_file))
    assert hash_str == "ba46f6c7ebf45fb57da743ef050869e1e45d32defe9da56e4593ba82c3305d8a"


def test_sql_hasher_empty():
    sh = SQLHasher(dialect="ansi", default_db="my_database")
    assert sh.hash_query("") == hash_string("")


def test_sql_transform_empty():
    # empty ast
    ast = {"file": None}
    for transform in [WhitespaceFilter(), CommentFilter(), DefaultDatabaseFilter("db")]:
        # ensure ast remains None
        ast = transform.generic_transform(ast)
        assert ast is None
