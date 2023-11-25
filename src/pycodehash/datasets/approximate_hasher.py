"""Base class for fast approximate hashing based on dataset metadata"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pycodehash.hashing import hash_string


def inline_metadata(metadata: dict[str, Any]) -> str:
    """Convert dict of metadata to string
    (all dictionary items should be serializable to string)
    """
    return "|".join([f"{key}: {value}" for key, value in metadata.items()])


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
    @abstractmethod
    def collect_hashes(self, *args, **kwargs) -> dict[str, Any]:
        pass

    def collect_metadata(self, *args, **kwargs) -> dict[str, Any]:
        return self.collect_hashes(*args, **kwargs)
