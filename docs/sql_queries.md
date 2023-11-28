# Detecting changes in SQL

_Functionality described on this page requires installation via `pip install pycodehash[sql]`_

The same principle holds for SQL as for Python functions: the hash of an SQL query should reflect changes of the implementation and be invariant to non-functional chagnes.

PyCodeHash supports hashing SQL queries and files.

The Abstract Syntax Tree (AST) parsing from the excellent [`SQLFluff`](https://docs.sqlfluff.com/en/stable/index.html) library is used in our implementation.

Currently, our implementation is invariant to newlines and whitespace.

This results in many dialects of SQL being [supported](https://docs.sqlfluff.com/en/stable/dialects.html) out of the box, e.g.:

- ANSI
- BigQuery
- PostgreSQL
- SparkSQL
- SQLite
- T-SQL (MSSQL)
- Trino

The `SQLHasher` allows for passing on configuration to `SQLFluff` via [configuration files](https://docs.sqlfluff.com/en/stable/configuration.html).
