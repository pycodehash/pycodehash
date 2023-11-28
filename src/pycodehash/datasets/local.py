from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

from pycodehash.datasets.approximate_hasher import ApproximateHasher, PartitionedApproximateHasher


def hash_file_full(file_path: str | Path, block_size: int = 8192) -> str:
    """Find SHA256 hash string of a local file

    Function capable of handling large files, loops over file blocks.
    https://www.quickprogrammingtips.com/python/how-to-calculate-sha256-hash-of-a-file-in-python.html

    Args:
        file_path: path to the file to hash
        block_size: read and update hash string in blocks (default: 8K)

    Returns:
        SHA256 hash
    """
    path = Path(file_path)

    sha256_hash = hashlib.sha256()
    with path.open("rb") as fb:
        # Read and update hash string value in blocks
        for byte_block in iter(lambda: fb.read(block_size), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


class LocalFileHash(ApproximateHasher):
    """Fast approximate hash for local files
    Based on last modification time and file size only.
    """

    def collect_metadata(self, path: str | Path) -> dict[str, Any]:
        path = Path(path)
        if path.is_dir():
            raise TypeError("Directories not supported. Please use `LocalDirectoryHash`")

        last_modified = path.stat().st_mtime
        last_modified = datetime.fromtimestamp(last_modified)
        file_size = path.stat().st_size
        return {"last_modified": last_modified, "size": file_size}


class LocalDirectoryHash(PartitionedApproximateHasher):
    def __init__(self):
        self.hasher = LocalFileHash()

    def collect_hashes(self, path: Path) -> dict[str, Any]:
        return {
            str(file_path): self.hasher.compute_hash(file_path)
            if file_path.is_file()
            else self.collect_hashes(file_path)
            for file_path in path.rglob("*")
        }
