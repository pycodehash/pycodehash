import ast

from pycodehash.preprocessing import DocstringStripper, TypeHintStripper, WhitespaceNormalizer, FunctionStripper
from pycodehash.preprocessing.decorator_stripper import DecoratorStripper
from pycodehash.unparse import _unparse


def _strip(src: str) -> str:
    """Remove whitespace and line-endings."""
    return "".join(src.split())


def _to_stripped_str(src: ast.Module) -> str:
    return _strip(_unparse(src))


_RAW_REFERENCE_FUNC = """
def foo(x, y=None):
    y = y or 10
    z = 2 * x
    return z + y
"""
_REFERENCE_FUNC = _strip(_RAW_REFERENCE_FUNC)


def test_to_normalised_string_smoke():
    ref = "def foo(x, y=None):;y = y or 10;z = 2 * x;return z + y"
    res = WhitespaceNormalizer().transform(_unparse(ast.parse(_RAW_REFERENCE_FUNC)))
    assert ref == res


def test_smoke_docstring():
    """Test nothing happens when nothing has to happen."""
    processed = DocstringStripper().visit(ast.parse(_RAW_REFERENCE_FUNC))
    assert _to_stripped_str(processed) == _REFERENCE_FUNC


def test_docstring_removal():
    """Test that docstring is properly removed."""
    f_str = (
        "def foo(x, y=None):\n"
        '    """Foo contains a docstring."""\n'
        "    y = y or 10\n"
        "    z = 2 * x\n"
        "    return z + y\n"
    )
    processed = DocstringStripper().visit(ast.parse(f_str))
    assert _to_stripped_str(processed) == _REFERENCE_FUNC


def test_multiline_docstring_removal():
    """Test that docstring is properly removed."""
    f_str = (
        "def foo(x, y=None):\n"
        '    """Foo contains a docstring.\n\n'
        "    Parameters\n"
        "    ----------\n"
        "    x : int\n"
        '    """\n'
        "    y = y or 10\n"
        "    z = 2 * x\n"
        "    return z + y\n"
    )
    processed = DocstringStripper().visit(ast.parse(f_str))
    assert _to_stripped_str(processed) == _REFERENCE_FUNC


def test_nodoc_with_str_expr():
    """Test that docstring is properly removed."""
    f_str = (
        "def foo(x, y=None):\n"
        "    'This an unassigned string.'\n"
        "    y = y or 10\n"
        "    z = 2 * x\n"
        "    return z + y\n"
    )
    processed = DocstringStripper().visit(ast.parse(f_str))
    assert _to_stripped_str(processed) == _REFERENCE_FUNC


def test_nodoc_with_doc_and_str_expr():
    """Test that docstring is properly removed."""
    f_str = (
        "def foo(x, y=None):\n"
        '    """Foo contains a docstring."""\n'
        "    'This an unassigned string.'\n"
        "    y = y or 10\n"
        "    z = 2 * x\n"
        "    return z + y\n"
    )
    processed = DocstringStripper().visit(ast.parse(f_str))
    assert _to_stripped_str(processed) == _REFERENCE_FUNC


def test_nodoc_with_str_assign():
    """Test that docstring is properly removed."""
    f_str = (
        "def foo(x, y=None):\n"
        "    dummy = 'This an unassigned string.'\n"
        "    y = y or 10\n"
        "    z = 2 * x\n"
        "    return z + y\n"
    )
    processed = DocstringStripper().visit(ast.parse(f_str))
    assert _to_stripped_str(processed) != _REFERENCE_FUNC


def test_smoke_typehints():
    """Test nothing happens when nothing has to happen."""
    processed = TypeHintStripper().visit(ast.parse(_RAW_REFERENCE_FUNC))
    assert _to_stripped_str(processed) == _REFERENCE_FUNC


def test_typehints_return_simple():
    """Test that return type annotation is removed."""
    f_str = (
        "def foo(x, y=None) -> int:\n"
        "    y = y or 10\n"
        "    z = 2 * x\n"
        "    return z + y\n"
    )
    processed = TypeHintStripper().visit(ast.parse(f_str))
    assert _to_stripped_str(processed) == _REFERENCE_FUNC


def test_typehints_return_complex():
    """Test that return type annotation is removed."""
    f_str = (
        "def foo(x, y=None) -> int | tuple[int, int]:\n"
        "    y = y or 10\n"
        "    z = 2 * x\n"
        "    return z + y\n"
    )
    processed = TypeHintStripper().visit(ast.parse(f_str))
    assert _to_stripped_str(processed) == _REFERENCE_FUNC


def test_typehints_params():
    """Test that return type annotation is removed."""
    f_str = (
        "def foo(x: int, y : Optional[int] = None):\n"
        "    y = y or 10\n"
        "    z = 2 * x\n"
        "    return z + y\n"
    )
    processed = TypeHintStripper().visit(ast.parse(f_str))
    assert _to_stripped_str(processed) == _REFERENCE_FUNC


def test_typehints_params_complex():
    """Test that return type annotation is removed."""
    f_str = (
        "def foo(x: int | tuple[int, int], y : Optional[int] = None):\n"
        "    y = y or 10\n"
        "    z = 2 * x\n"
        "    return z + y\n"
    )
    processed = TypeHintStripper().visit(ast.parse(f_str))
    assert _to_stripped_str(processed) == _REFERENCE_FUNC


def test_typehints_assign_simple():
    """Test that return type annotation is removed."""
    f_str = (
        "def foo(x, y=None):\n"
        "    y : int = y or 10\n"
        "    z : int = 2 * x\n"
        "    return z + y\n"
    )
    processed = TypeHintStripper().visit(ast.parse(f_str))
    assert _to_stripped_str(processed) == _REFERENCE_FUNC


def test_typehints_assign_complex():
    """Test that return type annotation is removed."""
    f_str = (
        "def foo(x, y=None):\n"
        "    y : int | tuple[int, int] = y or 10\n"
        "    z : int | float = 2 * x\n"
        "    return z + y\n"
    )
    processed = TypeHintStripper().visit(ast.parse(f_str))
    assert _to_stripped_str(processed) == _REFERENCE_FUNC


def test_typehints_all():
    """Test that return type annotation is removed."""
    f_str = (
        "def foo(x: int | tuple[int, int], y : Optional[int] = None) -> int | tuple[int, int]:\n"
        "    y : int | tuple[int, int] = y or 10\n"
        "    z : int | float = 2 * x\n"
        "    return z + y\n"
    )
    processed = TypeHintStripper().visit(ast.parse(f_str))
    assert _to_stripped_str(processed) == _REFERENCE_FUNC


def test_function_name_stripper():
    """Test if the function name is removed."""
    f_str = (
        "def foo(x, y):\n"
        "    y = y or 10\n"
        "    z = 2 * x\n"
        "    return z + y"
    )
    processed = _unparse(FunctionStripper().visit(ast.parse(f_str)))
    f_str_ref = (
        "def _(x, y):\n"
        "    y = y or 10\n"
        "    z = 2 * x\n"
        "    return z + y"
    )
    assert processed == f_str_ref


def test_decorator_stripper():
    f_str = (
        "import functools\n"
        "from functools import lru_cache\n"
        "\n"
        "def hello(x):\n"
        "    return x\n"
        "\n"
        "@hello()\n"
        "@hello\n"
        "@functools.lru_cache()\n"
        "@functools.lru_cache\n"
        "@lru_cache()\n"
        "@lru_cache\n"
        "def world():\n"
        "    pass\n"
    )
    processed = _unparse(DecoratorStripper(decorators=["functools.lru_cache"]).visit(ast.parse(f_str)))
    f_str_ref = (
        "import functools\n"
        "from functools import lru_cache\n"
        "\n"
        "def hello(x):\n"
        "    return x\n"
        "\n"
        "@hello()\n"
        "@hello\n"
        "def world():\n"
        "    pass\n"
    )
    assert processed == f_str_ref
