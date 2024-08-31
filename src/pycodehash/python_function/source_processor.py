from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class SourceProcessor(ABC):
    """Base class for transforming operating on source code"""

    @abstractmethod
    def transform(self, src: str) -> str:
        pass


class ProjectSourceProcessor(ABC):
    """Base class for inplace transforming operating on a project"""

    @abstractmethod
    def transform(self, path: str | Path) -> None:
        pass
