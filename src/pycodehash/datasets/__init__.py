"""Embarrassingly fast approximate hashes for specific datasets"""

from pycodehash.datasets.approximate_hasher import ApproximateHasher, PartitionedApproximateHasher
from pycodehash.datasets.local import LocalDirectoryHash, LocalFileHash, LocalFilesHash

__all__ = ["LocalFileHash", "LocalFilesHash", "LocalDirectoryHash", "ApproximateHasher", "PartitionedApproximateHasher"]
