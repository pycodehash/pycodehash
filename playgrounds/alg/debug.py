import ast
import functools


def _dump(d):
    import json
    print(json.dumps(d, indent=4, separators=(",", ": ")))


def print_source(x, label: str):
    print("=" * 80)
    print(label.upper())
    print(x)
    print("=" * 80)


ppd = functools.partial(ast.dump, indent=4)
appd = lambda x: print(ppd(ast.parse(x)))
apd = lambda x: print(ppd(x))


# def remove_func(source):
#     module = ast.parse(source)
#     assert len(module.body) == 1
#     v = module.body[0]
#     module = ast.Module(v.body, type_ignores=[])
#     new_source = ast.unparse(module)
#     return new_source
