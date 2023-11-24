import ast


def contains_call(node):
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            return True
    return False


class CallTracer(ast.NodeVisitor):
    def __init__(self):
        self.nested = False
        self.has_call = False

    def visit_Call(self, node: ast.Call):
        if self.has_call:
            self.nested = True
        self.has_call = True
        self.generic_visit(node)
