"""trace through files"""
from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path

from pycodehash.tracing.tracer import Tracer


def trace_file(file_name, first_party: str | tuple[str]):
    """

    Args:
        file_name:
        first_party:

    Returns:

    """
    source_code = (Path("resources") / file_name).read_text()
    node = ast.parse(source_code)

    v = Tracer()
    v.visit(node)

    for key, value in v.import_bindings.items():
        if value.startswith(first_party):
            print(key, value)
            module = importlib.import_module(value)
            module_source = inspect.getsource(module)
            print(module_source)
    print(v.import_bindings)


