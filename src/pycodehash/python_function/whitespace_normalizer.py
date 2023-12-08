from __future__ import annotations

from pycodehash.python_function.lines_transformer import LinesTransformer


class WhitespaceNormalizer(LinesTransformer):
    """Normalize source code newlines

    The trailing whitespace is removed
    and line breaks are replaced with a semicolon
    (for identical cross-platform hashes).
    """

    def __init__(self, sep: str = "\n"):
        """Initialize the WhitespaceNormalizer

        Args:
            sep: the token to replace newlines with
        """
        self.sep = sep

    def transform(self, src: str) -> str:
        """Removes whitespace from lines and joins lines with constant separator.

        Args:
            src: the source lines.

        Returns:
            The normalised string representation
        """
        return self.sep.join(s.rstrip() for s in src.splitlines() if s)
