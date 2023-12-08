from __future__ import annotations

import importlib
import sys
from binascii import hexlify
from pathlib import Path
from py_compile import PycInvalidationMode, compile
from struct import unpack
from time import asctime, localtime
from typing import Any

from pycodehash.datasets.approximate_hasher import ApproximateHasher


class PythonFileHash(ApproximateHasher):
    """Hashing based on the metadata from the Python bytecode (.pyc) file.
    If the file is not compiled, then it is compiled using the `PycInvalidationMode`.
    In theory, this method should be slightly faster than the `LocalFileHash` or than hashing the full file, when
    the compiled file is present.
    Take note that it relies on Python internals of the .pyc format and thus depends on the invalidation mode and
    Python version. Consider using the aforementioned methods, which do not have such dependency.
    """

    def __init__(self, invalidation_mode: PycInvalidationMode = PycInvalidationMode.TIMESTAMP):
        self.invalidation_mode = invalidation_mode

    def collect_metadata(self, path: str | Path) -> dict[str, Any]:
        """Read PYC from PEP: https://peps.python.org/pep-0552/
        Based on https://stackoverflow.com/questions/11141387/given-a-python-pyc-file-is-there-a-tool-that-let-me-view-the-bytecode
        """
        cache_file = Path(importlib.util.cache_from_source(str(path)))
        if not cache_file.exists():
            compile(str(path), invalidation_mode=self.invalidation_mode)

        hash_str = None
        timestamp = None
        size = None
        with cache_file.open("rb") as file:
            magic = hexlify(file.read(4)).decode("utf-8")

            bit_field = int.from_bytes(file.read(4), byteorder=sys.byteorder)
            if bit_field & 1 == 1:
                hash_str = hexlify(file.read(8)).decode("utf-8")
            else:
                timestamp = asctime(localtime(unpack("I", file.read(4))[0]))
                size = unpack("I", file.read(4))[0]

        return {"magic": magic, "timestamp": timestamp, "size": size, "hash": hash_str, "bit_field": bit_field}
