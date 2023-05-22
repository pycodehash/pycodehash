# Inline source code
from __future__ import annotations

import ast
import logging

from pycodehash.inlining.call_visitor import CallVisitor
from pycodehash.inlining.source import get_module_source, get_function_source, get_method_source
from pycodehash.node import Node
from pycodehash.tracer import Tracer


logger = logging.getLogger(__name__)

all_bindings = {}


def inline_node(node: Node, first_party: list[str] | None = None):
    inlined = []
    return inline(node.source, node.module, first_party=first_party, inlined=inlined)


def trace_module(module, first_party: list[str] | None = None):
    if module not in all_bindings:
        print(f"trace {module}")
        # TODO: move exception handling to source?
        try:
            source = get_module_source(module)
        except OSError: # OSError: source code not available
            all_bindings[module] = {}
            print(f"no source for {module}")
            return
        except Exception:
            all_bindings[module] = {}
            print(f"exception for {module}")
            return
        module_src = ast.parse(source)

        tracer = Tracer(module)
        tracer.visit(module_src)

        all_bindings[module] = tracer.import_bindings

        # Recursively trace modules
        for v in tracer.import_bindings.values():
            if len(v) >= 1 and (first_party is None or v[0].startswith(tuple(first_party))):
                trace_module(v[0], first_party)


def inline(source: str, module, first_party: list[str] | None = None, inlined: list[str] | None = None):
    # TODO: invariant for ordering

    inlined_source = ""

    try:
        src = ast.parse(source)
    except:
        print("SOURCE")
        print(repr(source))
        return ""

    # Trace module
    trace_module(module, first_party)
    # found in {module: {variable: full q name}}
    # ex       {tliba.etl: {rng: tba.random.rng}}
    # print('all bindings', json.dumps(all_bindings, indent=4))

    # Search for all calls in the node source
    visitor = CallVisitor()
    visitor.visit(src)
    print('all calls', visitor.calls)
    for call in visitor.calls:
        print('my call', call)
        if call[0] not in all_bindings[module]:
            print(f"not found in all_bindings[{module}]", all_bindings[module].keys())
            continue
            # x = call
            # TODO: move resolving FQN to tracer (?)
            # if x[0] in all_bindings[module]:
            #     binding = (all_bindings[module][x[0]], x[1])
            #     # print(all_bindings[module][x[0]])
            # else:
            #     print(call, all_bindings.keys())
            #     continue
            #     raise ValueError
        else:
            # pd.concat => not in all bindings
            # pd => in all bindings
            # pandas.concat ?
            binding = (*all_bindings[module][call[0]], *call[1:])
            print(f"found in all_bindings[{module}]", binding)

        if binding[0] == "__builtins__":
            print("skip builtins")
            continue
        if first_party is not None and not binding[0].startswith(tuple(first_party)):
            print("skip non-first party", binding[0], first_party)
            continue
        if binding in inlined:
            print("already inlined")
            continue
        print("first party", first_party)
        print("get source", binding)
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
                raise ValueError
        except:
            continue

        inlined.append(binding)
        inlined_source += inline(c_src, binding[0], first_party, inlined)

    # Comment to identify the module
    module_namespace = f"""{'#' * 80}
# Module: {module}
{'#' * 80}
"""
    inlined_source += module_namespace
    inlined_source += source
    return inlined_source
