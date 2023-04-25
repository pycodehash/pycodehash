"""Preprocessing classes to make the hash invariant to certain source code transformations"""
from pycodehash.preprocessing.function_stripper import FunctionStripper
from pycodehash.preprocessing.docstring_stripper import DocstringStripper
from pycodehash.preprocessing.whitespace_normalizer import WhitespaceNormalizer
from pycodehash.preprocessing.typehint_stripper import TypeHintStripper

__all__ = ["DocstringStripper", "WhitespaceNormalizer", "TypeHintStripper", "FunctionStripper"]
