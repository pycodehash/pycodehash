from __future__ import annotations

import hashlib
from datetime import datetime
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

    def collect_metadata(self, path: str | Path) -> dict[str, Any]:
        path = Path(path)
        if path.is_dir():
            return self._collect_metadata_dir(path)
        return self._collect_metadata_file(path)

    def _collect_metadata_file(self, path: Path) -> dict[str, Any]:
        last_modified = path.stat().st_mtime
        last_modified = datetime.fromtimestamp(last_modified)
        file_size = path.stat().st_size
        return {"last_modified": last_modified, "size": file_size}

    def _collect_metadata_dir(self, path: Path) -> dict[str, Any]:
        all_files_in_dir = list(path.rglob("*"))
        dict_to_hash = {str(file_path): self._collect_metadata_file(file_path) for file_path in all_files_in_dir}
        return dict_to_hash
