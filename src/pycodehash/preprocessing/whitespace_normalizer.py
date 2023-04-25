from __future__ import annotations

from pycodehash.preprocessing.lines_transformer import LinesTransformer


class WhitespaceNormalizer(LinesTransformer):
    """Normalize source code whitespace

    The leading and trailing whitespace is removed
    and line breaks are replaced with a semicolon
    (for identical cross-platform hashes).
    """
    def __init__(self):
        self.sep = ";"

    def transform(self, src: str) -> str:
        """
        Removes whitespace from lines, and joins lines with constant separator.

        Args:
            src: the source lines.

        Returns:
            The normalised string representation
        """
        return self.sep.join(s.strip() for s in src.splitlines())
