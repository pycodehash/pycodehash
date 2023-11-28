# PyCodeHash

[![Build](https://github.com/pycodehash/pycodehash/workflows/build/badge.svg)](https://github.com/pycodehash/pycodehash/actions)
[![Latest Github release](https://img.shields.io/github/v/release/pycodehash/pycodehash)](https://github.com/pycodehash/pycodehash/releases)
[![GitHub release date](https://img.shields.io/github/release-date/pycodehash/pycodehash)](https://github.com/pycodehash/pycodehash/releases)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/astral-sh/ruff)

Data pipelines are of paramount importance in data science, engineering and analysis.
Often, there are parts of the pipeline that have not changed.
Recomputing these nodes is wasteful, especially for larger datasets.
PyCodeHash is a generic data and code hashing library that facilitates downstream caching.

Read more on the [documentation site](https://pycodehash.github.io/pycodehash/).

## Detecting changes in data pipelines

The canonical way to check if two things are equal is to compare their hashes.
Learn more on how PyCodeHash detects changes in:

- [Python Functions](https://pycodehash.github.io/pycodehash/python_functions/)
- [SQL Queries](https://pycodehash.github.io/pycodehash/sql_queries/)
- [Dataset](https://pycodehash.github.io/pycodehash/datasets/): Files, Directories, S3, Hive

## Installation

PyCodeHash is available from [PyPI](https://pypi.org/project/pycodehash/):

```shell
pip install pycodehash
```

## Examples

### Python

Use the FunctionHasher to obtain the hash of a Python function object:

```python
from pycodehash import FunctionHasher
from tliba import compute_moments
from tliba.etl import add_bernoulli_samples, combine_random_samples

fh = FunctionHasher()
# Hash the function `add_bernoulli_samples`
h1 = fh.hash_func(add_bernoulli_samples)
print("Hash for `add_bernoulli_samples`", h1)

# Hash the function `compute_moments`
h2 = fh.hash_func(compute_moments)
print("Hash for `compute_moments`", h2)

# Hash the function `combine_random_samples`
h3 = fh.hash_func(combine_random_samples)
print("Hash for `combine_random_samples`", h3)
```
_[Python Usage Example](https://github.com/pycodehash/pycodehash/blob/dev/example.py)_

### SQL

Hash SQL queries and files using the `SQLHasher` (requires `pip install pycodehash[sql]`):

```python
from pathlib import Path

from pycodehash.sql.sql_hasher import SQLHasher
from pycodehash.sql.whitespace_filter import WhitespaceFilter

# First query
query_1 = "SELECT * FROM db.templates"

# The second query is equivalent, but has additional whitespace
query_2 = "SELECT\n    * \nFROM \n    db.templates"

# Write the second query to a file
query_2_file = Path("/tmp/query.sql")
query_2_file.write_text(query_2)

# Create the SQLHasher object for SparkSQL
hasher = SQLHasher(ast_transformers=[WhitespaceFilter()], dialect="sparksql")

# We can hash a string
print(hasher.hash_query(query_1))

# Or pass a path
print(hasher.hash_file(query_2_file))
```
_[SQL Usage Example](https://github.com/pycodehash/pycodehash/blob/dev/example_sql.py)_

## Datasets

Hash data, such as files, directories, database tables:

```python
from pathlib import Path

from pycodehash.datasets import LocalFileHash, LocalDirectoryHash


# Hash a single file
fh = LocalFileHash()

print(fh.collect_metadata("example.py"))
# {'last_modified': datetime.datetime(2023, 11, 24, 23, 38, 17, 524024), 'size': 621}

print(fh.compute_hash("example.py"))
# 2582e4198b42e6ceedeb58e05925da2480cdafddf87a731b971f315352beca47

# Hash a directory
dh = LocalDirectoryHash()

# Recursively hash all files in a directory
print(len(dh.collect_hashes(Path(__file__).parent / "src")))
# 29
```
_[Dataset Usage Example](example_data.py)_

## License

Pycodehash is completely free, open-source and licensed under the [MIT license](https://en.wikipedia.org/wiki/MIT_License).
