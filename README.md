# PyCodeHash

[![Build](https://github.com/pycodehash/pycodehash/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/pycodehash/pycodehash/actions)
[![Latest Github release](https://img.shields.io/github/v/release/pycodehash/pycodehash)](https://github.com/pycodehash/pycodehash/releases)
[![GitHub release date](https://img.shields.io/github/release-date/pycodehash/pycodehash)](https://github.com/pycodehash/pycodehash/releases)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/astral-sh/ruff)
[![Downloads](https://static.pepy.tech/badge/pycodehash)](https://pepy.tech/project/pycodehash)

Data pipelines are of paramount importance in data science, engineering and analysis.
Often, there are parts of the pipeline that have not changed.
Recomputing these nodes is wasteful, especially for larger datasets.
PyCodeHash is a generic data and code hashing library that facilitates downstream caching.

🚩 Output of `hash_func` for **both functions below is identical**: `38d6e9f262ab77f6536e14c74be687ce2cb44cdebb7045e5b2f51946215cf4d0`! 🚩

Read more on the [documentation site](https://pycodehash.github.io/pycodehash/).

```python
def func(data, key_col, value_col, **kwargs):
    if not isinstance(key_col, str) or not isinstance(value_col, str):
        raise TypeError(
            f"Column names must be strings, got {key_col}:{type(key_col)} and {value_col}:{type(value_col)}"
        )

    reserved_col = "index"
    if reserved_col in (key_col, value_col):
        raise ValueError(f"Reserved keyword: `{reserved_col}`")

    data = data[~data.isnull().any(axis=1)].copy()
    data[key_col] = data[key_col].astype(int)

    column_names = [key_col, value_col]
    for column_name in column_names:
        print(f"Unique values in {column_name}", list(data[column_name].unique()))

    return dict(zip(data[key_col], data[value_col]))
```

_[Sample 1](./examples/equivalance/sample1.py): An implementation of a function that creates a mapping from two columns in a pandas DataFrame. Hash: `38d6e9f262ab77f6536e14c74be687ce2cb44cdebb7045e5b2f51946215cf4d0`_

```python
from __future__ import annotations

import logging  # on purpose unused import

import pandas as pd


def create_df_mapping(data: pd.DataFrame, key_col: str, value_col: str, **kwargs) -> dict[int, str]:
    """Example function to demonstrate PyCodeHash.
    This function takes a pandas DataFrame and two column names, and turns them into a dictionary.

    Args:
        data: DataFrame containing the data
        key_col: column
    """
    legacy_variable = None
    if not isinstance(key_col, str) or not isinstance(value_col, str):
        raise TypeError(
            "Column names must be strings, got {key_col}:{key_type} and {value_col}:{value_type}".format(
                key_col=key_col,
                key_type=type(key_col),
                value_col=value_col,
                value_type=type(value_col),
            )
        )
    else:
        reserved_col = str("index")
        if key_col == reserved_col:
            raise ValueError("Reserved keyword: `{}`".format(reserved_col))
        elif value_col == reserved_col:
            raise ValueError("Reserved keyword: `{}`".format(reserved_col))

        data = data[~data.isnull().any(axis=1)].copy()
        data[key_col] = data[key_col].astype(int)

        column_names = [key_col, value_col]
        for index, column_name in enumerate(column_names):
            print(f"Unique values in {column_names[index]}", list(data[column_names[index]].unique()))

        return {
            key: value
            for key, value in zip(data[key_col], data[value_col])
        }
```

_[Sample 2](./examples/equivalance/sample2.py): An alternative implementation of the snippet above. Hash: `38d6e9f262ab77f6536e14c74be687ce2cb44cdebb7045e5b2f51946215cf4d0`_

## Detecting changes in data pipelines

The canonical way to check if two things are equal is to compare their hashes.
Learn more on how PyCodeHash detects changes in:

* [Python Functions](https://pycodehash.github.io/pycodehash/python_functions/)
* [SQL Queries](https://pycodehash.github.io/pycodehash/sql_queries/)
* [Datasets](https://pycodehash.github.io/pycodehash/datasets/): Files, Directories, S3, Hive
* [Python dependencies](https://pycodehash.github.io/pycodehash/dependencies/)

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

_[Python Usage Example](https://github.com/pycodehash/pycodehash/blob/main/example.py)_

### SQL

Hash SQL queries and files using the `SQLHasher` (requires `pip install pycodehash[sql]`):

```python
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
print(hasher.hash_query(query_1))

# Or pass a path
print(hasher.hash_file(query_2_file))
```

_[SQL Usage Example](https://github.com/pycodehash/pycodehash/blob/main/example_sql.py)_

### Datasets

Hash data, such as files, directories, database tables:

```python
from pathlib import Path

from pycodehash.datasets import LocalFileHash, LocalDirectoryHash


# Hash a single file
fh = LocalFileHash()

print(fh.collect_metadata("example.py"))
# {'last_modified': datetime.datetime(2023, 11, 24, 23, 38, 17, 524024), 'size': 543}

print(fh.compute_hash("example.py"))
# 6189721d3ecdf86503a82c07eed82743069ebbf39e974f33ca684809e67e9e0e

# Hash a directory
dh = LocalDirectoryHash()

# Recursively hash all files in a directory
print(len(dh.collect_partitions(Path(__file__).parent / "src")))
# 29
```

_[Dataset Usage Example](https://github.com/pycodehash/pycodehash/blob/main/example_data.py)_

### Python Package Dependencies

Hash a user-provided list of Python packages your code depends on. This may be a selection of the total list of dependencies.
For example the most important libraries your code depends on, that you want to track in order to trigger a rerun of your pipeline in case of version changes.
The hasher retrieves the installed package versions and creates a hash of those. We emphasize it is up to the user to provide the list of relevant dependencies.

```python
from pycodehash.dependency import PythonDependencyHash

# hash a list of dependencies
hasher = PythonDependencyHash()

print(hasher.collect_metadata(dependencies=["pycodehash", "rope"], add_python_version=True))
# hasher retrieves the installed package versions found
# {'pycodehash': '0.2.0', 'rope': '1.11.0', 'Python': '3.11'}

print(hasher.compute_hash(dependencies=["pycodehash", "rope"], add_python_version=True))
# cecb8036ad61235c2577db9943f519b824f7a25e449da9cd332bc600fb5dccf0
```

_[Dependency Usage Example](https://github.com/pycodehash/pycodehash/blob/main/example_dependency.py)_

## License

PyCodeHash is completely free, open-source and licensed under the [MIT license](https://en.wikipedia.org/wiki/MIT_License).
