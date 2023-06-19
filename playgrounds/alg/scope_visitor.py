from abc import ABC, abstractmethod


class ScopeVisitor(ABC):
    @abstractmethod
    def trace(self, *args) -> tuple[dict[str, str], tuple[str, str]]:
        raise NotImplementedError
