"""Base class for fast approximate hashing based on dataset metadata"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pycodehash.hashing import hash_string


def inline_metadata(metadata: dict[str, Any]) -> str:
    """Convert dict of metadata to string
    (all dictionary items should be serializable to string)
    Inlined metadata is invariant to the ordering of keys.
    """
    return "|".join([f"{key}: {value}" for key, value in sorted(metadata.items())])


class ApproximateHasher(ABC):
    """Compute hash based on metadata for a given dataset
    For certain combinations (e.g. file size and modification date) the chance of collisions
    is workable for caching in practice
    """

    @abstractmethod
    def collect_metadata(self, *args, **kwargs) -> dict[str, Any]:
        pass

    def compute_hash(self, *args, **kwargs) -> str:
        metadata = self.collect_metadata(*args, **kwargs)
        inlined_metadata = inline_metadata(metadata)
        return hash_string(inlined_metadata)


class PartitionedApproximateHasher(ApproximateHasher):
    def __init__(self, hasher: ApproximateHasher):
        self.hasher = hasher

    @abstractmethod
    def collect_partitions(self, *args, **kwargs) -> list[str]:
        pass

    def _hash_partitions(self, partitions: list[str | list[str]]):
        return {
            partition: self.hasher.compute_hash(partition)
            if not isinstance(partition, list)
            else self._hash_partitions(partition)
            for partition in partitions
        }

    def collect_metadata(self, *args, **kwargs) -> dict[str, Any]:
        partitions = self.collect_partitions(*args, **kwargs)
        return self._hash_partitions(partitions)
