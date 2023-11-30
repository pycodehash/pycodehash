from pycodehash.sql.sql_hasher import SQLHasher


def test_sql_hasher():
    query = "SELECT * FROM table"
    sh = SQLHasher()
    hash_str = sh.hash_query(query)
    assert hash_str == "688d619bbc67c43971fcf129e50b8d449c05809f317b38a641daec3d73a90f3e"
