from __future__ import annotations

import ast
import inspect
from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
from typing import Callable

import asttokens
from rope.base.libutils import analyze_modules
from rope.base.project import Project
from rope.base.pyobjectsdef import PyModule
from rope.contrib.findit import Location


def _item_to_key(item: Location):
    return item.resource.path, item.region[0], item.region[1], item.lineno


class FunctionStore:
    def __init__(self):
        self.store: dict[tuple[str, int, int, int], str] = {}

    def __getitem__(self, item: Location) -> str:
        key = _item_to_key(item)
        return self.store[key]

    def __setitem__(self, item: Location, value: str) -> None:
        key = _item_to_key(item)
        self.store[key] = value

    def __contains__(self, item):
        key = _item_to_key(item)
        return key in self.store


@dataclass
class ModuleView:
    pkg: str
    name: str
    path: Path
    code: str
    tree: ast.Module
    tree_tokens: asttokens.ASTTokens


class ModuleStore:
    def __init__(self):
        self.store: dict[str, ModuleView] = {}

    def __getitem__(self, item: PyModule) -> ModuleView:
        """Retrieve ModuleView from module.

        Args:
            item: the module for which to retrieve its view

        Raises:
            TypeError: when the key is not a Python Module object or a `rope` module

        """
        name = item.get_name()
        if name not in self.store:
            self._initialize_module_view(name, item)
        return self.store[name]

    def _initialize_module_view(self, name, module: PyModule) -> None:
        pkg, _, _ = name.partition(".")
        path = module.get_resource().pathlib
        code = module.resource.read()
        tree = module.get_ast()
        tree_tokens = asttokens.ASTTokens(code, parse=False, tree=tree)

        self.store[name] = ModuleView(
            pkg=pkg,
            name=name,
            path=path,
            code=code,
            tree=tree,
            tree_tokens=tree_tokens,
        )


class ProjectStore:
    """Caching mechanism for rope.projects.

    Each package results in a project which is analyzed by Rope.
    Note that analyzing a large package can be fairly slow.
    """

    def __init__(self):
        """Initialise the class.

        Args:
            whitelist: set of packages that are allowed to be analyzed.
                By default all packages are allowed.
        """
        self.store: dict[str, Project] = {}

    def __getitem__(self, item: str) -> Project:
        """Get rope project from package name.

        Args:
            item: package name

        Returns:
            project: analyzed rope project
        """
        if item not in self.store:
            self._initialize_project(item)
        return self.store[item]

    def _initialize_project(self, pkg: str):
        """Create and set a project. If the package name is not provided, then assume the project root is the current
        working directory.

        Args:
            pkg: package name

        """
        if pkg == "__main__":
            raise ValueError("Cannot resolve `__main__` yet")

        spec = find_spec(pkg)
        if spec.submodule_search_locations is None:
            project_root = Path.cwd()
        else:
            project_root = spec.submodule_search_locations[0]
        project = Project(projectroot=project_root)
        analyze_modules(project)
        self.store[pkg] = project

    def add_project(self, pkg: str):
        """Explicitly add project for tracing.

        Args:
            pkg: the name of the package to be analyzed
        """
        self._initialize_project(pkg)

    def get_from_func(self, func: Callable) -> Project:
        # get the module from the function
        module = inspect.getmodule(func)
        name = module.__name__
        pkg, _, _ = name.partition(".")
        return self.__getitem__(pkg)

    # TODO: this should be refactored
    def get_projects(self, mod: ModuleView | None = None) -> list[Project]:
        """Create a list with all projects where the first project to which the module belongs to."""
        if mod is None:
            return list(self.store.values())
        mod_project = self[mod.pkg]
        return [mod_project] + [v for v in self.store.values() if v != mod_project]
