"""Backwards compatibility unparsing for <= py3.8"""
import sys

if sys.version_info < (3, 8):
    # when python 3.9 is common this dependency can be removed
    # as python 3.9 has the corresponding native function
    from astunparse import unparse

    _unparse = unparse
else:
    import ast

    _unparse = ast.unparse
