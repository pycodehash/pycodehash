import ast
from ast import NodeTransformer

from rope.base.libutils import path_to_resource
from rope.contrib.findit import Location, find_definition

from pycodehash.hashing import hash_string


class ReplaceCall(NodeTransformer):
    def find_definition(self, node, project) -> Location | None:
        loc = find_definition(project, self.module.code, self.module.tree_tokens.get_text_range(node)[0])
        if isinstance(loc, Location) and loc.resource is None:
            loc.resource = path_to_resource(project, self.module.path)
        return loc

    def visit_Call(self, node: ast.Call):
        # call a function that hashes the source of the function
        self.hash_repr = hash_string(ast.unparse(node))
        super().generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name):
        if self.hash_repr is not None:
            node.id = self.hash_repr
            self.hash_repr = None
        return node
