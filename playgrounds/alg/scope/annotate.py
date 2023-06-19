
from annotator import AnnotateScope, IntermediateGlobalScope
from pull_scope import PullScopes


class ScopeInfo:
    def __init__(self, tree, global_scope, error_scope, node_to_containing_scope):
        self._tree = tree
        self._global_scope = global_scope
        self._error_scope = error_scope
        self._node_to_containing_scope = node_to_containing_scope

    @property
    def global_scope(self):
        return self._global_scope

    @property
    def nodes(self):
        return self._node_to_containing_scope


def annotate(tree, class_binds_near=False):
    annotation_dict = {}
    annotator = AnnotateScope(IntermediateGlobalScope(), annotation_dict, class_binds_near=class_binds_near)
    annotator.visit(tree)

    pull_scopes = PullScopes(annotation_dict)
    pull_scopes.visit(tree)
    return ScopeInfo(tree, pull_scopes.global_scope, pull_scopes.error_scope, pull_scopes.node_to_containing_scope)


if __name__ == "__main__":
    import ast

    code = """
from ast import parse

def f():
    def g(x):
        a = parse
        a('print(\"it\")')
        print(\"hello world\")
        def h(y, z: int = 3):
            c = 3
            c()
            parse()
            print(y, z)
        
    return parse
    """
    tree =ast.parse(code)
    scope_info = annotate(tree, class_binds_near=True)

    for node, scope in scope_info._node_to_containing_scope.items():
        if isinstance(node, ast.FunctionDef):
            print(node.name, scope)
        elif isinstance(node, ast.Name):
            print(node.id, scope)
        elif isinstance(node, ast.arg):
            print(node.arg, scope)
        else:
            print(type(node), scope)
    print(scope_info.global_scope)
    last_g = tree.body[1].body[-1].value
    print(scope_info.nodes[last_g])

    print("-"*80)
    code = """
def f(x):
    def g(x): return x()
    return g(lambda: x)
    """
    tree = ast.parse(code)
    last_x = tree.body[0].body[-1].value.args[0].body
    # run the annotator
    scope_info = annotate(tree)
    scope_x = scope_info.nodes[last_x]
    print(scope_x, scope_x.children[0])

    code = """
def f():
    x = 3
    lambda z: theta
    
    def x():
        print("xyz")
    return x + y
"""
    tree = ast.parse(code)
    scope_info = annotate(tree)
    global_variables = sorted(scope_info.global_scope.symbols_in_frame)
    print(global_variables)

    for node, scope in scope_info._node_to_containing_scope.items():
        if isinstance(node, ast.FunctionDef):
            print(node.name, scope)
        elif isinstance(node, ast.Name):
            print(node.id, scope)
        elif isinstance(node, ast.arg):
            print(node.arg, scope)
        else:
            print(type(node), scope)