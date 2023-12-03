import importlib
from pathlib import Path
from py_compile import PycInvalidationMode

import pytest
from pycodehash.datasets.python import PythonFileHash


@pytest.fixture(scope="function")
def empty_cache():
    # Ensure cache is recomputed
    cache_file = Path(importlib.util.cache_from_source(__file__))
    if cache_file.exists():
        cache_file.unlink()


def test_python_file_hash_timestamp(empty_cache):
    pfh = PythonFileHash(PycInvalidationMode.TIMESTAMP)
    metadata = pfh.collect_metadata(__file__)
    assert "magic" in metadata
    assert "timestamp" in metadata
    assert "size" in metadata
    assert "hash" in metadata
    assert "bit_field" in metadata

    assert isinstance(metadata["magic"], str)
    assert isinstance(metadata["timestamp"], str)
    assert isinstance(metadata["size"], int)
    assert metadata["hash"] is None
    assert metadata["bit_field"] == 0


def test_python_file_hash_unchecked_hash(empty_cache):
    pfh = PythonFileHash(PycInvalidationMode.UNCHECKED_HASH)
    metadata = pfh.collect_metadata(__file__)
    assert "magic" in metadata
    assert "timestamp" in metadata
    assert "size" in metadata
    assert "hash" in metadata
    assert "bit_field" in metadata

    assert isinstance(metadata["magic"], str)
    assert isinstance(metadata["hash"], str)
    assert metadata["timestamp"] is None
    assert metadata["size"] is None
    assert metadata["bit_field"] == 1


def test_python_file_hash_checked_hash(empty_cache):
    pfh = PythonFileHash(PycInvalidationMode.CHECKED_HASH)
    metadata = pfh.collect_metadata(__file__)
    assert "magic" in metadata
    assert "timestamp" in metadata
    assert "size" in metadata
    assert "hash" in metadata
    assert "bit_field" in metadata

    assert isinstance(metadata["magic"], str)
    assert isinstance(metadata["hash"], str)
    assert metadata["timestamp"] is None
    assert metadata["size"] is None
    assert metadata["bit_field"] == 3
