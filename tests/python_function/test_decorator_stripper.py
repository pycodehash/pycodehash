# import ast
#
# from pycodehash import DecoratorStripper
# from pycodehash.unparse import _unparse
#
# def test_decorator_stripper():
#     f_str = (
#         "import functools\n"
#         "from functools import lru_cache\n"
#         "\n"
#         "def hello(x):\n"
#         "    return x\n"
#         "\n"
#         "@hello()\n"
#         "@hello\n"
#         "@functools.lru_cache()\n"
#         "@functools.lru_cache\n"
#         "@lru_cache()\n"
#         "@lru_cache\n"
#         "def world():\n"
#         "    pass\n"
#     )
#     processed = _unparse(DecoratorStripper(decorators=["functools.lru_cache"]).visit(ast.parse(f_str)))
#     f_str_ref = (
#         "import functools\n"
#         "from functools import lru_cache\n"
#         "\n"
#         "def hello(x):\n"
#         "    return x\n"
#         "\n"
#         "@hello()\n"
#         "@hello\n"
#         "def world():\n"
#         "    pass\n"
#     )
#     assert processed == f_str_ref
