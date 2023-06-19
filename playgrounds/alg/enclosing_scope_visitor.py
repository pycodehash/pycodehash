from ast import NodeVisitor
import ast


class EnclosingScopeVisitor(NodeVisitor):
    def __init__(self, fqn, s):
        self.s = s
        self.fqn = fqn
        self.obj = None

    def visit_ClassDef(self, node: ast.ClassDef):
        if node.name == self.fqn:
            self.obj = node
        if node.name == self.s:
            self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name == self.fqn:
            self.obj = node
        if node.name == self.s:
            self.generic_visit(node)