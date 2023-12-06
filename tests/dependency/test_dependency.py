import sys

import pycodehash
from pycodehash.datasets.approximate_hasher import inline_metadata
from pycodehash.dependency import PythonDependencyHash
from pycodehash.hashing import hash_string


def test_dependency():
    expect = {"pycodehash": pycodehash.__version__, "Python": f"{sys.version_info.major}.{sys.version_info.minor}"}
    inlined_expect = inline_metadata(expect)
    expect_hash = hash_string(inlined_expect)

    hasher = PythonDependencyHash()

    result = hasher.collect_metadata(dependencies=["pycodehash"], add_python_version=True)
    assert result == expect

    result_hash = hasher.compute_hash(dependencies=["pycodehash"], add_python_version=True)
    assert result_hash == expect_hash
