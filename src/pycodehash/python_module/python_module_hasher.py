from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from rope.base.libutils import modname
from rope.base.project import NoProject
from rope.base.resources import Resource

from pycodehash.datasets.approximate_hasher import PartitionedApproximateHasher
from pycodehash.datasets.local import LocalFileHash
from pycodehash.python_module.import_visitor import ImportVisitor

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec


def find_module_spec(module_name: str) -> ModuleSpec | None:
    spec = None
    if not module_name or module_name.startswith("__main__"):
        return None

    try:
        spec = importlib.util.find_spec(module_name)
    except AssertionError:
        return None
    except (ModuleNotFoundError, ImportError):
        pass

    if spec is None:
        if "." not in module_name:
            return None
        new_name = module_name.rsplit(".", 1)[0]
        return find_module_spec(new_name)

    if spec.origin is None or spec.origin in {"built-in", "frozen"} or "site-packages" not in spec.origin:
        # Exclude built-ins and stdlib
        return None

    return spec


class PythonModuleHasher(PartitionedApproximateHasher):
    def __init__(self, first_party: list[str] | None):
        self.first_party = first_party
        # Import graph
        self.modules: dict[str, set[str]] = {}
        # Module paths
        self.module_paths: dict[str, str | Path] = {}
        super().__init__(LocalFileHash())  # Alternative: PythonFileHash

    def is_whitelisted(self, module_name: str) -> bool:
        pkg, _, _ = module_name.partition(".")
        # check whitelisted
        return self.first_party is None or pkg in self.first_party

    def visit_module(self, module_path: str | Path) -> None:
        module_name = modname(Resource(NoProject(), module_path))
        self.module_paths[module_name] = module_path

        src = Path(module_path).read_text()
        root = ast.parse(src)

        iv = ImportVisitor()
        iv.visit(root)

        module_references = set()
        for module_import in iv.imports:
            if not self.is_whitelisted(module_import):
                continue

            spec = find_module_spec(module_import)
            if spec is not None and spec.origin is not None and spec.origin.endswith(".py"):  # Exclude .so sources
                module_references.add(spec.name)
                self.module_paths[spec.name] = spec.origin

        self.modules[module_name] = module_references

        for module_reference in module_references:
            if module_reference not in self.modules:
                self.visit_module(self.module_paths[module_reference])

    def collect_partitions(self, func: Callable) -> dict[str, str]:
        file_name = inspect.getsourcefile(func)
        if file_name is None:
            msg = "Could not obtain source file for function"
            raise ValueError(msg)
        self.visit_module(file_name)
        return {module_name: str(module_path) for module_name, module_path in self.module_paths.items()}
