from abc import ABC, abstractmethod


class LinesTransformer(ABC):
    """Base class for transforming based on lines"""

    @abstractmethod
    def transform(self, src: str) -> str:
        pass
