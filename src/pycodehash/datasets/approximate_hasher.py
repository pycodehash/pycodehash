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

    METADATA: list[str] | None = None

    @abstractmethod
    def collect_metadata(self, *args, **kwargs) -> dict[str, Any]:
        """Collect metadata used for hashing"""

    def compute_hash(self, *args, **kwargs) -> str:
        metadata = self.collect_metadata(*args, **kwargs)
        if self.METADATA is not None:
            metadata = {key: value for key, value in metadata.items() if key in self.METADATA}
        inlined_metadata = inline_metadata(metadata)
        return hash_string(inlined_metadata)


class PartitionedApproximateHasher(ApproximateHasher):
    """Compute the hash of multiple objects"""

    def __init__(self, hasher: ApproximateHasher):
        self.hasher = hasher

    @abstractmethod
    def collect_partitions(self, *args, **kwargs) -> list[str] | dict[str, str]:
        """Collect partitions (key, value) or list of keys for hashing"""

    def _hash_partitions(self, partitions: list[str] | dict[str, Any]):
        if isinstance(partitions, list):
            partitions = dict(zip(partitions, partitions))

        return {
            partition_key: self.hasher.compute_hash(partition_value)
            if not isinstance(partition_value, dict)
            else self._hash_partitions(partition_value)
            for partition_key, partition_value in partitions.items()
        }

    def collect_metadata(self, *args, **kwargs) -> dict[str, Any]:
        partitions = self.collect_partitions(*args, **kwargs)
        return self._hash_partitions(partitions)
