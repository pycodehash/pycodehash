"""Hash SQL queries and files (requires `sqlfluff` to be installed)"""
from pathlib import Path

from pycodehash.sql.sql_hasher import SQLHasher

# First query
query_1 = "SELECT * FROM db.templates"

# The second query is equivalent, but has additional whitespace
query_2 = "SELECT\n    * \nFROM \n    db.templates"

# Write the second query to a file
query_2_file = Path("/tmp/query.sql")
query_2_file.write_text(query_2)

# Create the SQLHasher object for SparkSQL
hasher = SQLHasher(dialect="sparksql")

# We can hash a string
result_1 = hasher.hash_query(query_1)
print(result_1)

# Or pass a path
result_2 = hasher.hash_file(query_2_file)
print(result_2)

# Both hashes are identical
assert result_1 == result_2
