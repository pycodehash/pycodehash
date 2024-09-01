from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from pycodehash.python_function.source_processor import ProjectSourceProcessor

if TYPE_CHECKING:
    from pathlib import Path


def _ruff_check(path: str, select: list[str], unsafe: bool, preview: bool) -> None:
    """Apply ruff check autofixes for a list of rules.

    Args:
        path: path to pass to ruff check
        select: list of lint codes
        unsafe: if True, also apply autofixes marked as "unsafe"
        preview: if True, also apply autofixes marked as "preview"
    """
    cmd = [
        "ruff",
        "check",
        "--isolated",
        "--no-cache",
        "--select",
        ",".join(select),
        "--ignore",
        "PLR0402",  # See "Known issues" in CONTRIBUTING.md
        "--fix-only",
        "--quiet",
    ]
    if unsafe:
        cmd.append("--unsafe-fixes")
    if preview:
        cmd.append("--preview")
    cmd.append(path)

    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        msg = "The RuffProcessor exited with a non-zero exit code."
        raise RuntimeError(msg)


def _ruff_fmt(path: str) -> None:
    """Apply ruff formatting to a path

    Args:
        path: path to pass to ruff format
    """
    cmd = ["ruff", "format", "--isolated", "--no-cache", "--quiet", path]

    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        msg = "The RuffProcessor exited with a non-zero exit code."
        raise RuntimeError(msg)


class RuffProjectProcessor(ProjectSourceProcessor):
    def __init__(self, select: list[str] | None = None, unsafe: bool = True, preview: bool = True):
        default_select = ["I", "RET", "F", "UP", "E", "W", "COM819", "C4", "PIE", "SIM", "PL", "FURB", "RUF", "PERF"]

        self.select = select or default_select
        self.unsafe = unsafe
        self.preview = preview

    def transform(self, path: str | Path) -> None:
        _ruff_check(str(path), self.select, self.unsafe, self.preview)
        _ruff_fmt(str(path))
