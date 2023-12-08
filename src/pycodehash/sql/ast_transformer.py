from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ASTTransformer(ABC):
    """Base class for transforming based on the AST"""

    @abstractmethod
    def transform(self, src: dict[str, Any]) -> dict[str, Any]:
        pass
