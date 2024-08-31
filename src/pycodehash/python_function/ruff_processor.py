from __future__ import annotations

from tempfile import NamedTemporaryFile

from pycodehash.python_function.ruff_project_processor import RuffProjectProcessor
from pycodehash.python_function.source_processor import SourceProcessor


class RuffProcessor(SourceProcessor):
    def __init__(self, select: list[str] | None = None, unsafe: bool = True):
        self.ruff_path_processor = RuffProjectProcessor(select, unsafe)

    def transform(self, source: str) -> str:
        with NamedTemporaryFile("r+", suffix=".py", encoding="utf-8") as fp:
            fp.write(source)
            fp.seek(0)

            self.ruff_path_processor.transform(fp.name)

            return fp.read().strip()
