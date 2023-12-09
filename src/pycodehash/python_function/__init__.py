"""Preprocessing classes to make the hash invariant to certain source code transformations"""
from pycodehash.python_function.decorator_stripper import DecoratorStripper
from pycodehash.python_function.docstring_stripper import DocstringStripper
from pycodehash.python_function.function_stripper import FunctionStripper
from pycodehash.python_function.lines_transformer import LinesTransformer
from pycodehash.python_function.typehint_stripper import TypeHintStripper
from pycodehash.python_function.whitespace_normalizer import WhitespaceNormalizer

__all__ = [
    "DocstringStripper",
    "WhitespaceNormalizer",
    "TypeHintStripper",
    "FunctionStripper",
    "DecoratorStripper",
    "LinesTransformer",
]
