from __future__ import annotations

import ast
import inspect
import logging

from builtins_scope_visitor import BuiltinsScopeVisitor
from call_visitor import CallVisitor
from module_scope_visitor import ModuleScopeVisitor
from function_scope_visitor import FunctionScopeVisitor
from transform import Transformer
from pycodehash.hashing import hash_string
from source import get_source

from debug import print_source, _dump


logger = logging.getLogger("source_hasher")
logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] [%(levelname)s] --- %(message)s (%(filename)s:%(lineno)s)")


class SourceHasher:
    _bscope = None

    def __init__(self, first_party: list[str] | None, python_version: tuple[int, int] | None = None, hashes: dict[str, str] | None = None):
        self.first_party = first_party
        self.transformer = Transformer()
        self.python_version = python_version

        # TODO: option 1, return dict of hashes
        #       option 2, return single hash (for large number of funcs)
        #       option 3, replace calls with FQN
        self.hashes = hashes or {}

    @property
    def bscope(self):
        if self._bscope is None:
            # Built-ins scope
            logger.debug("Analyzing Builtins")
            self._bscope, _ = BuiltinsScopeVisitor(self.python_version).trace()
        return self._bscope

    # TODO: pass node?
    def transform(self, source, module_source, fqn1, fqn2):
        logger.debug("Hash source code for `%s`", fqn2)

        self.hashes[fqn2] = "<in progress>"
        # Short-circuit if no calls
        # TODO: consistent with below
        lcv = CallVisitor()
        lcv.visit(ast.parse(source))
        if lcv.found:
            logger.debug("At least one call found in module `%s`, analyzing scope", fqn1)

            # Module scope
            mscope, mcalls = ModuleScopeVisitor(self.bscope).trace(module_source, fqn1)

            # Function scope
            lscope, lcalls = FunctionScopeVisitor(mscope).trace(source, fqn2, fqn1)
            logger.debug("Calls found %d", len(lcalls))
            # assert len(lcalls) > 0

            # Filter non-first-party
            if self.first_party is not None:
                before = len(lcalls)
                print(lcalls)
                lcalls = [(k, v) for k, v in lcalls if v is not None and v.startswith(tuple(self.first_party))]
                diff = before - len(lcalls)
                if diff > 0:
                    logger.debug("Filtered out %d/%d non-first-party calls", diff, before)

            # Deduplicate (keep order)
            prev = []
            calls = []
            before = len(lcalls)
            for call in lcalls:
                if call[1] not in prev:
                    prev.append(call[1])
                    calls.append(call)
            diff = before - len(calls)
            if diff > 0:
                logger.debug("Removed %d duplicated calls", diff)

            # Full list of calls and FQNs
            for lcall in calls:
                _, call_fqn = lcall
                # Skip calls already computed
                if call_fqn in self.hashes:
                    continue
                logger.debug("Get source for %s", call_fqn)
                call_source, call_mod_source = get_source(call_fqn)
                if call_source.startswith("    "):
                    # TODO: fix when the import refers to a variable instead of function
                    print(f"ERROR RETRIEVING SOURCE FROM {lcall}")
                    continue

                sh = SourceHasher(first_party=self.first_party, hashes=self.hashes)
                result = sh.transform(call_source, call_mod_source, call_fqn.rsplit(".", 1)[0], call_fqn)
                # print(f'hash for `{call_fqn}: {result}')
                self.hashes.update(result)
                # TODO: replace func call name with hash?

        else:
            print(f"NO CALLS FOR {fqn1}")
        # TODO: add all inlined hashes
        transformed_source = self.transformer.transform(ast.parse(source))
        print_source(transformed_source, "transformed source")
        self.hashes[fqn2] = hash_string(transformed_source)
        return self.hashes


if __name__ == "__main__":
    import ast_scope
    import ast


    from example import src, p9
    from example.src import foo, bar
    from example.p9 import my_func

    func = foo
    mod = src

    tree = ast.parse(inspect.getsource(foo))
    scope_info = ast_scope.annotate(tree)
    # print(scope_info._node_to_containing_scope)
    # for node, scope in scope_info._node_to_containing_scope.items():
    #     if isinstance(node, ast.FunctionDef):
    #         print(node.name, scope.symbols_in_frame)
    # print(scope_info.static_dependency_graph)
    # global_variables = sorted(scope_info.global_scope.symbols_in_frame)
    # print(global_variables)
    # exit()
    # func = bar
    # mod = src

    # func = my_func
    # mod = p9

    sh = SourceHasher(["example"])
    print("-start-")
    result = sh.transform(
        inspect.getsource(func),
        inspect.getsource(mod),
        func.__module__,
        f"{func.__module__}.{func.__qualname__}"
    )
    _dump(result)
