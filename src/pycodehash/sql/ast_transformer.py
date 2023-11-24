from abc import ABC, abstractmethod


class ASTTransformer(ABC):
    """Base class for transforming based on the AST"""

    @abstractmethod
    def transform(self, src: str) -> str:
        pass
