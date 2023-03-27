from pycodehash.hashing import hash_string


def test_hash_string():
    assert hash_string("hello world") == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
