from datetime import datetime
import hashlib
from pathlib import Path


def hash_file(file_path: str, mode: str = 'approximate'):
    """ Find SHA256 hash string of a local file
    """
    assert mode in ['full', 'approximate']
    if mode == 'full':
        return hash_file_full(file_path=file_path)
    return hash_file_approximate(file_path=file_path)


def hash_file_full(file_path: str):
    """ Find SHA256 hash string of a local file

    Function capable of handling large files, loops over file blocks.
    https://www.quickprogrammingtips.com/python/how-to-calculate-sha256-hash-of-a-file-in-python.html

    :param str: file path
    :return: sha256 hash
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as fb:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: fb.read(8192), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def hash_file_approximate(file_path: str):
    """ Find SHA256 hash string of a local file

    Based on last modification time and file size only. (fast)

    :param str: file path
    :return: sha256 hash
    """
    path = Path(file_path)
    last_modified = path.stat().st_mtime
    last_modified = datetime.fromtimestamp(last_modified)
    file_size = path.stat().st_size
    combined = f'last modified: {last_modified} / size: {file_size}'
    bytes = str.encode(combined)
    return hashlib.sha256(bytes).hexdigest()
