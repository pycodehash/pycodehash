from __future__ import annotations

import ast
import inspect
from dataclasses import dataclass
from functools import singledispatchmethod
from importlib.util import find_spec
from pathlib import Path
from types import FunctionType, ModuleType

import asttokens
from rope.base.libutils import analyze_modules
from rope.base.project import Project
from rope.contrib.findit import Location


class FunctionStore:
    # TODO(SB): perhaps just a typed dict instead of classes?
    def __init__(self):
        self.store: dict[Location, str] = {}

    def get(self, location: Location) -> str:
        """Get hash of function at `location`."""
        ...

    def __getitem__(self, item: Location) -> str:
        return self.store[item]

    def __setitem__(self, key, value):
        self.store[key] = value


@dataclass
class ModuleView:
    pkg: str
    name: str
    path: str
    code: str
    tree: ast.Module
    tree_tokens: asttokens.ASTTokens


class ModuleStore:
    def __init__(self):
        self.store: dict[str, ModuleView] = {}

    def _create_module_view(self, mod: ModuleType) -> ModuleView:
        name = mod.__name__
        pkg, _sep, _stem = name.partition(".")
        path = Path(inspect.getsourcefile(mod))
        code = path.read_text()
        tree = ast.parse(code)

        return ModuleView(
            pkg=pkg,
            name=name,
            path=path,
            code=code,
            tree=tree,
            tree_tokens=asttokens.ASTTokens(code, parse=False, tree=tree),
        )

    def set(self, func: FunctionType, error_if_set: bool = False):
        mod = inspect.getmodule(func)
        name = mod.__name__
        if name in self.store and error_if_set:
            raise ValueError(f"Module with name {name} has been previously set.")
        mod_view = self._create_module_view(mod)
        self.store[name] = mod_view

    @singledispatchmethod
    def get(self, key, error_if_missing: bool = False) -> ModuleView:
        """Retrieve ModuleView for `key`.

        Args:
            key (FunctionType | str): the function for which to retrieve its module or the name of the module
            error_if_missing: raise error if `key` is unknown. If False and the `key` is a FunctionType than
                a ModuleView is created and returned, if the `key` is a string that None is returned.

        Raises:
            KeyError: when `key` is unknown and `error_if_missing` is True
            NotImplementedError: when type of `key` is not a string or FunctionType

        """
        raise NotImplementedError("`key` must a `str` or `FunctionType`.")

    @get.register
    def get_from_module(self, key: ModuleType, error_if_missing: bool = False) -> ModuleView:
        """Retrieve ModuleView from module.

        Args:
            key: the module for which to retrieve its view
            error_if_missing: raise error if `key` is unknown, otherwhise a ModuleView is created
                and returned.

        Raises:
            KeyError: when `key` is unknown and `error_if_missing` is True

        """
        name = key.__name__
        mod_view = self.store.get(name)

        if mod_view is not None:
            return mod_view
        if error_if_missing is True:
            raise KeyError(f"Unknown module: {name}")
        mod_view = self._create_module_view(key)
        self.store[name] = mod_view
        return mod_view

    @get.register
    def get_from_func(self, key: FunctionType, error_if_missing: bool = False) -> ModuleView:
        """Retrieve ModuleView from func.

        Args:
            key: the function for which to retrieve its module
            error_if_missing: raise error if `key` is unknown, otherwhise a ModuleView is created
                and returned.

        Raises:
            KeyError: when `key` is unknown and `error_if_missing` is True

        """
        mod = inspect.getmodule(key)
        return self.get_from_module(mod, error_if_missing)

    @get.register
    def get_from_name(self, key: str, error_if_missing: bool = False) -> ModuleView:
        mod_view = self.store.get(key)
        if error_if_missing is True and mod_view is None:
            raise KeyError(f"Unknown name: {key}")
        # TODO(SB): set mod_view = Default value
        return mod_view


class ProjectStore:
    def __init__(self):
        self.store: dict[str, Project] = {}

    def set(self, pkg: str):
        """Create and set a project.

        Args:
            pkg: package name

        """
        if pkg == "__main__":
            raise ValueError("Cannot resolve `__main__` yet")

        spec = find_spec(pkg)
        project = Project(projectroot=spec.submodule_search_locations[0])
        analyze_modules(project)
        self.store[pkg] = project

    def get(self, pkg: str) -> Project:
        """Get rope project from package name.

        Args:
            pkg: package name

        Returns:
            project: analyzed rope project
        """
        if pkg not in self.store:
            self.set(pkg)
        return self.store[pkg]

    def get_projects(self, mod: ModuleView | None = None) -> list[Project]:
        """Create a list with all projects where the first project to which the module belongs to."""
        mod_project = self.get(mod.pkg)
        return [mod] + [v for v in self.store.values() if v != mod_project]
