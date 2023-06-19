from __future__ import annotations

import ast
import logging
from ast import NodeVisitor

from scope_visitor import ScopeVisitor
from source import _get_source, get_module
from ast_funcs import fqn_name

logger = logging.getLogger("module_scope_visitor")


class ModuleScopeVisitor(NodeVisitor, ScopeVisitor):
    def __init__(self, imports: dict[str,str] | None = None):
        self.imports = {} or imports
        self.calls = []

    def trace(self, source, module_fqn) -> tuple[dict[str, str], list[tuple[str, str]]]:
        logger.debug("Analyzing module scope for `%s`", module_fqn)

        self.module_fqn = module_fqn
        self.visit(ast.parse(source))
        return self.imports, self.calls

    def visit_Import(self, node: ast.Import):
        """Visit each name of an Import."""
        for n in node.names:
            self.visit_alias(n)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Visit each name of an ImportFrom."""
        for n in node.names:
            self.visit_alias_with_mod(n, node.module)

    def visit_alias(self, node: ast.alias):
        """Extract name and qualified name from alias."""
        name = node.asname or node.name
        self.imports[name] = node.name

    def visit_alias_with_mod(self, node: ast.alias, module: str):
        """Extract name and qualified name from alias and module name."""
        name = node.asname or node.name
        if name == "*":
            logger.debug("Star import found in `%s`, importing `%s`", self.module_fqn, module)
            m = get_module(module)
            if hasattr(m, "__all__"):
                for k in m.__all__:
                    self.imports[k] = f"{module}.k"
            else:
                s = _get_source(m)
                star_imports, _ = ModuleScopeVisitor(self.imports.copy()).trace(s, module)
                star_imports = {k: v for k,v in star_imports.items() if v.startswith(module)}
                self.imports.update(star_imports)
        else:
            self.imports[name] = f"{module}.{node.name}"

    def visit_FunctionDef(self, node: ast.FunctionDef):
        name = node.name
        self.imports[name] = f"{self.module_fqn}.{name}"

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        name = node.name
        self.imports[name] = f"{self.module_fqn}.{name}"

    def visit_Assign(self, node: ast.Assign):
        # Simple alias, e.g. `foo = bar`
        if (
            isinstance(node.value, ast.Name)
            and node.value.id in self.imports
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            name = node.targets[0].id
            self.imports[name] = self.imports[node.value.id]
        if isinstance(node.value, ast.Lambda) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            self.imports[name] = f"{self.module_fqn}.{node.value}"
        super().generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        name = node.name
        self.imports[name] = f"{self.module_fqn}.{name}"
        for sub_node in node.body:
            if isinstance(sub_node, ast.FunctionDef):
                self.imports[f"{node.name}.{sub_node.name}"] = f"{self.module_fqn}.{name}.{sub_node.name}"

    # Combine with CallVisitor
    def visit_Call(self, node: ast.Call):
        # Fixate call
        name = fqn_name(node.func)
        if name not in self.imports:
            if "." in name:
                parent_module, import_name = name.rsplit('.', 1)
                if parent_module in self.imports:
                    m = get_module(self.imports[parent_module])
                    if m is None or not hasattr(m, import_name):
                        print(f"WARNING: `{name}` not found in scope")
                else:
                    print(f"WARNING: `{name}` not found in scope")
            else:
                print(f"WARNING: `{name}` not found in scope")

        self.calls.append((name, self.imports.get(name, None)))
        super().generic_visit(node)
