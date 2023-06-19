from __future__ import annotations

import importlib
import inspect
from types import ModuleType

from debug import print_source
from enclosing_scope_visitor import EnclosingScopeVisitor


def get_module(fqn) -> ModuleType | None:
    try:
        return importlib.import_module(fqn)
    except ModuleNotFoundError:
        return None


def _get_source(o) -> str | None:
    try:
        source = inspect.getsource(o)
    except OSError:
        # no source code available for `o`
        return None

    return source


def get_mod_fqn(fqn):
    if "." not in fqn:
        return None

    mod, rest = fqn.rsplit(".", 1)
    m = get_module(mod)
    if m is not None:
        return m, rest
    else:
        m, name = get_mod_fqn(mod)
        return m, f"{name}.{rest}"


def get_source(fqn):
    """Get source code based on the fully qualified name

    Examples:
    - foo.Bar (module foo, class Bar)
    - foo.Bar.FooBar.m1 (module foo, class Bar, nested class FooBar, method m1)
    - foo.bar (module foo, function bar)
    - foo.bar.<locals>.foo (module foo, function bar, nested function foo)

    Args:
        fqn: fully qualified name

    Returns:
        source code
    """
    mod, name = get_mod_fqn(fqn)
    if mod is None:
        print("no mod")
        return

    its = name.split(".", 1)
    o = mod
    print('NAME', name)
    for element in its:
        if hasattr(o, element):
            o = getattr(o, element)
        else:
            # Example:
            # >>> def func1():
            # >>>  def func2():
            # >>>      ...
            # >>>  return func1
            # fqn: func1.func2 / func1.<locals>.func2
            print("nested visitor")
            # TODO: NOT NEEDED, ALREADY IN PARENT HASH!
            #       (╯°□°）╯︵ ┻━┻
            # exit()
            # nsv = EnclosingScopeVisitor(its[1], "foo")
            # nsv.visit(ast.parse(source))
            # if nsv.obj is not None:
            #     source = ast.unparse(nsv.obj)

    # TODO: dedent
    source = _get_source(o)
    print_source(source, "RETRIEVED")
    return source, _get_source(mod)
