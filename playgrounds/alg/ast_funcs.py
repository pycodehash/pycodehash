from __future__ import  annotations

import ast


def fqn_name(node: ast.Name | ast.Attribute):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{fqn_name(node.value)}.{node.attr}"
    if isinstance(node, ast.Call):
        name = fqn_name(node.func)
        # TODO: get node return type
        return name
    # TODO: subscript
    raise TypeError(f"Type {type(node)} not understood")
