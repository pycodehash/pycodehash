# Detecting changes in SQL

_Functionality described on this page requires installation via `pip install pycodehash[sql]`_

The same principle holds for SQL as for Python functions: the hash of an SQL query should reflect changes of the implementation and be invariant to non-functional changes.

## Hashing SQL queries and files

PyCodeHash supports hashing SQL queries and files.

Currently, our default implementation is invariant to omitting database names, comments, and whitespace, e.g.

```sql
/* block comment: set `my_database` as the default database */
USE my_database;

SELECT 
    -- inline comment: select all columns
    * 
FROM 
    hello_world
```

is equivalent to

```sql
USE my_database;
SELECT * FROM my_database.hello_world
```

This behavior can be extended with user-provided Abstract Syntax Tree (AST) transformers.

The AST parsing from the excellent [SQLFluff] library is used in our implementation.

This results in many dialects of SQL being [supported](https://docs.sqlfluff.com/en/stable/dialects.html) out of the box, e.g.:

* ANSI
* BigQuery
* PostgreSQL
* SparkSQL
* SQLite
* T-SQL (MSSQL)
* Trino

The `SQLHasher` allows for passing on configuration to [SQLFluff] via [configuration files](https://docs.sqlfluff.com/en/stable/configuration.html).

## Usage examples

### Hashing SQL files and queries

The [SQL Usage Example](https://github.com/pycodehash/pycodehash/blob/main/example_sql.py) demonstrates how to hash SQL queries and files:

```python
{% include 'example_sql.py' %}
```

### Hashing files in git history

Below is a more advanced example for checking if there was a behavioural change in a [SQL file in a specific git commit](https://github.com/pycodehash/pycodehash/blob/main/example_sql_git.py):

```python
{% include 'example_sql_git.py' %}
```

## SQL query dependencies

In real-world applications, engineers and analysts typically structure
multiple SQL queries in separate files that are executed sequentially or according to a topological order.
This is often achieved using data transformation frameworks like [dbt],
[SQLMesh] , or similar commercial products.

In such scenarios, simply relying on the hash of individual SQL files is
insufficient. When a referenced table in a query is updated, the query
must be re-executed, regardless of whether the query's contents have
changed. To address this, we can automatically extract table references by
parsing the SQL Abstract Syntax Tree (AST).

This approach is straightforward, as table references are limited to
specific contexts like `CREATE`, `FROM`, `INTO` and [Common Table Expressions]
(CTEs). We've chosen to integrate with existing efforts, leveraging the
[SQLLineage] implementation built on top of [SQLFluff], to prevent duplication
of effort.

Usage:

```python
from pycodehash.sql import extract_table_references

query = "SELECT * INTO output_table FROM my_database.input_table"

input_tables, output_tables, dropped_tables = extract_table_references(
    query, 
    default_db="my_database", 
    dialect="t-sql"
)
print(input_tables)
# {'my_database.input_table'}
print(output_tables)
# {'my_database.output_table'}
print(dropped_tables)
# {}
```

[dbt]: https://github.com/dbt-labs/dbt-core
[SQLMesh]: https://github.com/TobikoData/sqlmesh
[SQLLineage]: https://github.com/reata/sqllineage
[Common Table Expressions]: https://en.wikipedia.org/wiki/Hierarchical_and_recursive_queries_in_SQL#Common_table_expression
[SQLFluff]: https://docs.sqlfluff.com/en/stable/index.html
