from pathlib import Path

from pycodehash.sql.sql_hasher import SQLHasher


def test_sql_hasher():
    query = "SELECT * FROM table"
    sh = SQLHasher()
    hash_str = sh.hash_query(query)
    assert hash_str == "ba46f6c7ebf45fb57da743ef050869e1e45d32defe9da56e4593ba82c3305d8a"


def test_sql_hasher_file():
    query = "SELECT * FROM table"
    query_file = Path("query.sql")
    query_file.write_text(query)

    sh = SQLHasher()
    hash_str = sh.hash_file(query_file)
    assert hash_str == "ba46f6c7ebf45fb57da743ef050869e1e45d32defe9da56e4593ba82c3305d8a"

    hash_str = sh.hash_file(str(query_file))
    assert hash_str == "ba46f6c7ebf45fb57da743ef050869e1e45d32defe9da56e4593ba82c3305d8a"
