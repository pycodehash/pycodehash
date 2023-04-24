"""Base class for fast approximate hashing based on dataset metadata"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pycodehash.hashing import hash_string


def inline_metadata(metadata: dict[str, Any]) -> str:
    """
    Convert dict of metadata to string
    (all dictionary items should be serializable to string)
    """
    return "".join([
        f"<entry><key>{key}</key><value>{value}</value></entry>"
        for key, value in metadata.items()
    ])


class ApproximateHasher(ABC):
    @abstractmethod
    def collect_metadata(self, *args, **kwargs) -> dict[str, Any]:
        pass

    def compute_hash(self, *args, **kwargs) -> str:
        metadata = self.collect_metadata(*args, **kwargs)
        inlined_metadata = inline_metadata(metadata)
        return hash_string(inlined_metadata)
