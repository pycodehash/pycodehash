from __future__ import annotations

import inspect
import shutil
from collections import defaultdict
from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Iterator

import asttokens
from rope.base.libutils import analyze_modules
from rope.base.project import Project

if TYPE_CHECKING:
    import ast

    from rope.base.pyobjectsdef import PyModule
    from rope.contrib.findit import Location

    from pycodehash.python_function import ProjectSourceProcessor


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

    def __contains__(self, item: Location) -> bool:
        key = _item_to_key(item)
        return key in self.store


class FunctionCallStore:
    def __init__(self):
        self.store: defaultdict[tuple[str, int, int, int], list[Location]] = defaultdict(list)

    def __getitem__(self, item: Location) -> list[Location]:
        return self.store[_item_to_key(item)]

    def __setitem__(self, item: Location, value: Location) -> None:
        key = _item_to_key(item)
        self.store[key].append(value)

    def __contains__(self, item: Location) -> bool:
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

    def _initialize_module_view(self, name: str, module: PyModule) -> None:
        pkg, _, _ = name.partition(".")
        path = module.get_resource().pathlib
        code = module.resource.read()
        tree = module.get_ast()
        tree_tokens = asttokens.ASTTokens(code, parse=False, tree=tree)

        self.store[name] = ModuleView(pkg=pkg, name=name, path=path, code=code, tree=tree, tree_tokens=tree_tokens)


class ProjectStore:
    """Caching mechanism for rope.projects.

    Each package results in a project which is analyzed by Rope.
    Note that analyzing a large package can be fairly slow.
    """

    def __init__(self, tempdir: Path | None = None, source_processors: list[ProjectSourceProcessor] | None = None):
        """Initialise the class.

        Args:
            tempdir: path to the tempdir, or None if modified inplace
            source_processors: transformations to apply to the entire project source
        """
        self.store: dict[str, Project] = {}
        self.tempdir = tempdir
        self.source_processors = source_processors or []
        if tempdir is None and source_processors is not None:
            msg = (
                "It's not supported to modify projects in-place. Either enable `use_tempdir` or remove "
                "the source_preprocessors."
            )
            raise ValueError(msg)

    def __getitem__(self, item: str) -> Project:
        """Get rope project from package name.

        Args:
            item: package name

        Returns:
            project: analyzed rope project
        """
        return self.store[item]

    def _initialize_project(self, pkg: str):
        """Create and set a project.

        If the package name is not provided, then assume
        the project root is the current working directory.

        Args:
            pkg: package name

        """
        if pkg == "__main__":
            # See "Known issues" in CONTRIBUTING.md
            msg = (
                "Cannot resolve `__main__` yet. Import from a module for now. "
                "Please open an issue if you would be willing to contribute this feature: "
                "https://github.com/pycodehash/pycodehash/issues"
            )
            raise ValueError(msg)

        spec = find_spec(pkg)
        if spec is None:
            msg = f"Could not import package {pkg}."
            raise ImportError(msg)

        project_root = (
            Path.cwd() if spec.submodule_search_locations is None else Path(spec.submodule_search_locations[0])
        )
        if self.tempdir is not None:
            new_project_root = self.tempdir / project_root.name
            # note: this may copy unintended files such as the `venv` folder
            shutil.copytree(project_root, str(new_project_root), dirs_exist_ok=True, symlinks=True)
            project_root = new_project_root.absolute()

            for source_processor in self.source_processors:
                source_processor.transform(project_root)

        project = Project(projectroot=project_root, python_path=[str(self.tempdir)])
        analyze_modules(project)
        self.store[pkg] = project

    def add_project(self, pkg: str):
        """Explicitly add a project for tracing.

        Args:
            pkg: the name of the package to be analyzed
        """
        self._initialize_project(pkg)

    def get_or_create_for_func(self, func: Callable) -> Project:
        # get the module from the function
        module = inspect.getmodule(func)
        if module is None:
            msg = "Module for function not found"
            raise ValueError(msg)
        name = module.__name__
        pkg, _, _ = name.partition(".")
        if pkg not in self.store:
            self._initialize_project(pkg)
        return self[pkg]

    def __iter__(self) -> Iterator[Project]:
        yield from self.store.values()
