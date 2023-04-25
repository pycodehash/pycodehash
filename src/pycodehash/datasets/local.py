from __future__ import annotations

from datetime import datetime
import hashlib
from pathlib import Path
from typing import Any

from pycodehash.datasets.approximate_hasher import ApproximateHasher


def hash_file_full(file_path: str | Path):
    """Find SHA256 hash string of a local file

    Function capable of handling large files, loops over file blocks.
    https://www.quickprogrammingtips.com/python/how-to-calculate-sha256-hash-of-a-file-in-python.html

    Args:
        file_path: path to the file to hash

    Returns:
        SHA256 hash
    """
    path = Path(file_path)

    sha256_hash = hashlib.sha256()
    with path.open("rb") as fb:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: fb.read(8192), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


class LocalFileHash(ApproximateHasher):
    """
    Fast approximate hash for local files
    Based on last modification time and file size only.
    """
    def collect_metadata(self, file_path: str | Path) -> dict[str, Any]:
        path = Path(file_path)

        last_modified = path.stat().st_mtime
        last_modified = datetime.fromtimestamp(last_modified)
        file_size = path.stat().st_size
        return {"last_modified": last_modified, "size": file_size}
