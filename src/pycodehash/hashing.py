from __future__ import annotations

import hashlib
from pathlib import Path


def hash_string(input_string: str) -> str:
    """Compute SHA256 hash of input string.

    Args:
        input_string: the string to hash

    Returns:
        SHA256 hashed string
    """
    return hashlib.sha256(input_string.encode("utf-8")).hexdigest()


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
