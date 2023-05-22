"""Visitors used in call tracing."""
import ast
from ast import NodeVisitor


class ImportCollector(NodeVisitor):
    """Collect fully qualified names of imports.

    Attributes:
        imports: the call name as the key and the fully qualified name as value.
    """

    def __init__(self):
        """Initialise the visitor."""
        self.imports: dict[str, dict[str]] = dict()

    def visit_Import(self, node: ast.Import):
        """Visit each name of an Import."""
        for n in node.names:
            self.visit_alias(n)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Visit each name of an ImportFrom."""
        for n in node.names:
            self.visit_alias_with_mod(node, node.module)

    def visit_alias(self, node: ast.alias):
        """Extract name and qualified name from alias."""
        name = node.asname or node.name.split(".")[-1]
        self.imports[name] = node.name

    def visit_alias_with_mod(self, node: ast.alias, module: str):
        """Extract name and qualified name from alias and module name."""
        name = node.asname or node.name.split(".")[-1]
        self.imports[name] = f"{module}.{node.name}"


class LocalImportCollector(NodeVisitor):
    """Collect non module level imports.

    Attributes:
        imports: the imports per definition (key) where the value is a dict.
            The inner dict has the call name as the key and the fully qualified
            name as value.
    """

    def __init__(self):
        """Initialise the visitor."""
        self.imports: dict[str, dict[str]] = dict()
        self._local_imports: dict[str] = dict()
        self._collector = ImportCollector()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Collect imports from function definitions."""
        self._collector.visit(node)
        if len(self._collector.imports) > 0:
            self.imports[node.name] = self._collector.imports
            self._collector.imports = dict()

    def visit_AsyncFunctionDef(self, node: ast.FunctionDef):
        """Collect imports from async function definitions."""
        self._collector.visit(node)
        if len(self._collector.imports) > 0:
            self.imports[node.name] = self._collector.imports
            self._collector.imports = dict()


class ModuleImportCollector(ImportCollector):
    """Collect imports at top level.

    Note this visitor skips nested imports by overwriting
    note types that can have import nodes as descendants.

    Attributes:
        imports: the call name as the key and the fully qualified name as value.
    """

    def visit_FunctionDef(self, node: ast.ClassDef):
        """Block FunctionDef traversal."""
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Block AsyncFunctionDef traversal."""
        return

    def visit_ClassDef(self, node: ast.ClassDef):
        """Block ClassDef traversal."""
        return
