# https://peps.python.org/pep-0227/
# https://peps.python.org/pep-3104/
from scope_visitor import ScopeVisitor


def _builtins() -> dict[str, tuple[str, ...]]:
    """Python Builtins

    Returns:
        dictionary of python builtins import bindings

    References:
        https://docs.python.org/3/library/functions.html
    """
    return {
        key: f"__builtins__.{key}"
        for key in [
            "abs",
            "aiter",
            "all",
            "any",
            "anext",
            "ascii",
            "bin",
            "bool",
            "breakpoint",
            "bytearray",
            "bytes",
            "callable",
            "chr",
            "classmethod",
            "compile",
            "complex",
            "delattr",
            "dict",
            "dir",
            "divmod",
            "enumerate",
            "eval",
            "exec",
            "filter",
            "float",
            "format",
            "frozenset",
            "getattr",
            "globals",
            "hasattr",
            "hash",
            "help",
            "hex",
            "id",
            "input",
            "int",
            "isinstance",
            "issubclass",
            "iter",
            "len",
            "list",
            "locals",
            "map",
            "max",
            "memoryview",
            "min",
            "next",
            "object",
            "oct",
            "open",
            "ord",
            "pow",
            "print",
            "property",
            "range",
            "repr",
            "reversed",
            "round",
            "set",
            "setattr",
            "slice",
            "sorted",
            "staticmethod",
            "str",
            "sum",
            "super",
            "tuple",
            "type",
            "vars",
            "zip",
            "_",
            "__import__",
        ]
    }


class BuiltinsScopeVisitor(ScopeVisitor):
    def __init__(self, python_version=None):
        self.python_version = python_version or (3, 8)

    def trace(self):
        return _builtins(), []
