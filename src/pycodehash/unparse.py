from __future__ import annotations
import ast

if hasattr(ast, "unparse"):
    _unparse = ast.unparse
else:
    # when python 3.9 is common this dependency can be removed
    # as python 3.9 has the corresponding native function
    from astunparse import unparse

    _unparse = unparse
