"""Embarrassingly fast approximate hashes for specific datasets"""
from pycodehash.datasets.approximate_hasher import ApproximateHasher, PartitionedApproximateHasher
from pycodehash.datasets.local import LocalDirectoryHash, LocalFileHash, hash_file_full

__all__ = [
    "LocalFileHash",
    "LocalFileHash",
    "LocalDirectoryHash",
    "ApproximateHasher",
    "PartitionedApproximateHasher",
    "hash_file_full",
]
