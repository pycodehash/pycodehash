from pycodehash.datasets.approximate_hasher import inline_metadata


def test_inline_metadata_invariant():
    d1 = {"k1": "v1", "k2": "v2"}
    d2 = {"k2": "v2", "k1": "v1"}
    assert inline_metadata(d1) == inline_metadata(d2)
