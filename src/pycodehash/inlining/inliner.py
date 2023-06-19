# Inline source code
from __future__ import annotations

import ast
import logging

from pycodehash.inlining.call_visitor import CallVisitor
from pycodehash.inlining.fqn import get_fqn
from pycodehash.inlining.source import get_function_source, get_method_source, get_module_source
from pycodehash.node import Node
from pycodehash.tracer import Tracer

logger = logging.getLogger(__name__)


# Mapping from module to fully qualified name
all_bindings = {}


def inline_node(node: Node, first_party: list[str] | None = None):
    """Inline a `Node` object

    Args:
        node: the node to inline
        first_party: list of modules to trace

    Returns:
        Inlined function source
    """
    inlined = []
    return inline(node.source, node.module, first_party=first_party, inlined=inlined)


def trace_module(module: str, first_party: list[str] | None = None) -> None:
    """Recursively trace imports in modules

    Args:
        module: name of the module
        first_party: list of top-level modules to trace

    Returns:
        Nothing, results are stored in the global `all_bindings` dictionary
    """
    if module not in all_bindings and (first_party is None or str(module).startswith(tuple(first_party))):
        logger.debug(f"trace `{module}`")

        source = get_module_source(module)
        if source is None:
            all_bindings[module] = {}
            logger.info(f"no source code available for `{module}`")
            return

        module_src = ast.parse(source)

        tracer = Tracer(module)
        tracer.visit(module_src)

        all_bindings[module] = tracer.import_bindings

        # Recursively trace modules
        for v in tracer.import_bindings.values():
            if len(v) >= 1 and (first_party is None or v[0].startswith(tuple(first_party))):
                trace_module(v[0], first_party)


def _module_namespace(module: str) -> str:
    """Helper to generate module namespace comment

    Args:
        module: name of the module

    Returns:
        Comment block denoting the module namespace
    """
    return f"""{'#' * 80}
# Module: {module}
{'#' * 80}
"""


def inline(source: str, module, first_party: list[str] | None = None, inlined: list[str] | None = None) -> str:
    """Inline a function provided the source code

    Args:
        source: function source code to inline
        module: the function's module
        first_party: list of top-level modules to search in
        inlined: list of already inlined modules (for recursive tracking)

    Returns:
        Inlined function source code
    """
    inlined_source = ""

    try:
        src = ast.parse(source)
    except IndentationError:
        print(f"could not parse AST for module {module} with source code:")
        print(repr(source))
        raise

    # Trace module
    trace_module(module, first_party)
    # found in {module: {variable: full q name}}
    # ex       {tliba.etl: {rng: tba.random.rng}}
    # print('all bindings', json.dumps(all_bindings, indent=4))

    # Search for all calls in the node source
    visitor = CallVisitor()
    visitor.visit(src)
    for call in visitor.calls:
        if call[0] not in all_bindings[module]:
            logger.debug(f"{call[0]} not found in all_bindings[{module}]", all_bindings[module].keys())
            continue

        # TODO: move to FQN logic
        prefx = all_bindings[module][call[0]]
        prefx = get_fqn(prefx)
        binding = (*prefx, *call[1:])

        # print('binding', binding)
        logger.debug(f"{call[0]} found in all_bindings[{module}]", binding)

        if binding[0] == "__builtins__":
            logger.debug("skip builtins")
            continue
        if first_party is not None and not binding[0].startswith(tuple(first_party)):
            logger.debug("skip non-first party", binding[0], first_party)
            continue
        if binding in inlined:
            # print("already inlined")
            continue

        # TODO: move to source
        # TODO: use above logic based on binding[1], binding[0] types
        # TODO: FQN -> then source
        try:
            if len(binding) == 1:
                continue
                # c_src = get_module_source(binding[0])
            elif len(binding) == 2:
                c_src = get_function_source(binding[1], binding[0])
            elif len(binding) == 3:
                c_src = get_method_source(binding[2], binding[1], binding[0])
            else:
                print(binding)
                continue
        except TypeError:
            logger.info(f"TypeError while fetching source from {binding}")
            continue
        except AttributeError:
            logger.info(f"AttributeError while fetching source from {binding}")
            continue

        if c_src is None:
            logger.info(f"OSError: source code not available for {binding}")
            continue
        inlined.append(binding)
        inlined_source += inline(c_src, binding[0], first_party, inlined)

    # Comment to identify the module
    inlined_source += _module_namespace(module)

    inlined_source += source
    return inlined_source