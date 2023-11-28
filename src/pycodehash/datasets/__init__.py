"""Embarrassingly fast approximate hashes for specific datasets"""
from pycodehash.datasets.approximate_hasher import ApproximateHasher, PartitionedApproximateHasher
from pycodehash.datasets.hive import HiveTableHash
from pycodehash.datasets.local import LocalDirectoryHash, LocalFileHash, hash_file_full

__all__ = [
    "HiveTableHash",
    "LocalFileHash",
    "LocalDirectoryHash",
    "ApproximateHasher",
    "PartitionedApproximateHasher",
    "hash_file_full",
]
