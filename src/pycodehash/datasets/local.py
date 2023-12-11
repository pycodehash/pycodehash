from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from pycodehash.datasets.approximate_hasher import ApproximateHasher, PartitionedApproximateHasher


class LocalFileHash(ApproximateHasher):
    """Fast approximate hash for local files
    Based on last modification time and file size only.
    """

    METADATA = ["size"]

    @staticmethod
    def collect_metadata(path: str | Path) -> dict[str, Any]:
        path = Path(path)
        if path.is_dir():
            msg = "Directories not supported. Please use `LocalDirectoryHash`"
            raise TypeError(msg)

        last_modified = datetime.fromtimestamp(path.stat().st_mtime)
        file_size = path.stat().st_size

        return {"last_modified": last_modified, "size": file_size}


class LocalDirectoryHash(PartitionedApproximateHasher):
    """Recursively find files in the provided directory and compute the hash for each of the files."""

    def __init__(self):
        super().__init__(LocalFileHash())

    @staticmethod
    def collect_partitions(path: Path) -> dict[str, str]:
        return {
            str(file_path.relative_to(path)): str(file_path) for file_path in path.rglob("*") if file_path.is_file()
        }


class LocalFilesHash(PartitionedApproximateHasher):
    def __init__(self):
        super().__init__(LocalFileHash())

    @staticmethod
    def collect_partitions(files: list[str] | dict[str, str]) -> list[str] | dict[str, str]:
        return files
