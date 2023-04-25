import ast

from pycodehash.hashing import hash_string, FuncNodeHasher

# to_hash = "def _(x, y=None):;y = y or 10;z = 2 * x;return z + y"
# hashlib.sha256(to_hash.encode("utf-8")).hexdigest()
_REF_FUNC_HASH = "da19d7c7d47231be0c466c457b41bb551a533c186d4a8cf3e2fee55a02311ff9"


def test_hash_string():
    assert (
        hash_string("hello world")
        == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    )


def test_FuncNodeHasher_smoke():
    f_str = (
        "def foo(x, y=None):\n"
        "    y = y or 10\n"
        "    z = 2 * x\n"
        "    return z + y\n"
    )
    hasher = FuncNodeHasher()
    hasher.visit(ast.parse(f_str))
    assert hasher.hashes["foo"] == _REF_FUNC_HASH


def test_FuncNodeHasher_name_invariance():
    f_str = (
        "def bar(x, y=None):\n"
        "    y = y or 10\n"
        "    z = 2 * x\n"
        "    return z + y\n"
    )
    hasher = FuncNodeHasher()
    hasher.visit(ast.parse(f_str))
    assert hasher.hashes["bar"] == _REF_FUNC_HASH


def test_FuncNodeHasher_docstring():
    f_str = (
        "def foo(x, y=None):\n"
        '    """Foo contains a docstring."""\n'
        "    y = y or 10\n"
        "    z = 2 * x\n"
        "    return z + y\n"
    )
    hasher = FuncNodeHasher()
    hasher.visit(ast.parse(f_str))
    assert hasher.hashes["foo"] == _REF_FUNC_HASH


def test_FuncNodeHasher_typehints():
    f_str = (
        "def foo(x: int | tuple[int, int], y : Optional[int] = None) -> int | tuple[int, int]:\n"
        "    y : int | tuple[int, int] = y or 10\n"
        "    z : int | float = 2 * x\n"
        "    return z + y\n"
    )
    hasher = FuncNodeHasher()
    hasher.visit(ast.parse(f_str))
    assert hasher.hashes["foo"] == _REF_FUNC_HASH


def test_FuncNodeHasher_invariance():
    f_str = (
        "def bar(x: int | tuple[int, int], y : Optional[int] = None) -> int | tuple[int, int]:\n"
        '    """Bar contains a docstring."""\n'
        "    y : int | tuple[int, int] = y or 10\n"
        "    z : int | float = 2 * x\n"
        "    return z + y\n"
    )
    hasher = FuncNodeHasher()
    hasher.visit(ast.parse(f_str))
    assert hasher.hashes["bar"] == _REF_FUNC_HASH


def test_FuncNodeHasher_detection():
    hasher = FuncNodeHasher()

    # body change
    f_str = (
        "def bar(x: int | tuple[int, int], y : Optional[int] = None) -> int | tuple[int, int]:\n"
        '    """Bar contains a docstring."""\n'
        "    y : int | tuple[int, int] = y or 10\n"
        "    z : int | float = 3 * x\n"
        "    return z + y\n"
    )
    hasher.visit(ast.parse(f_str))
    assert hasher.hashes["bar"] != _REF_FUNC_HASH

    # default arg change
    f_str = (
        "def bar(x: int | tuple[int, int], y : Optional[int] = 0) -> int | tuple[int, int]:\n"
        '    """Bar contains a docstring."""\n'
        "    y : int | tuple[int, int] = y or 10\n"
        "    z : int | float = 3 * x\n"
        "    return z + y\n"
    )
    hasher.visit(ast.parse(f_str))
    assert hasher.hashes["bar"] != _REF_FUNC_HASH

    # arg name change
    f_str = (
        "def bar(x: int | tuple[int, int], a : Optional[int] = None) -> int | tuple[int, int]:\n"
        '    """Bar contains a docstring."""\n'
        "    y : int | tuple[int, int] = y or 10\n"
        "    z : int | float = 3 * x\n"
        "    return z + y\n"
    )
    hasher.visit(ast.parse(f_str))
    assert hasher.hashes["bar"] != _REF_FUNC_HASH
