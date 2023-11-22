from __future__ import annotations

import logging

from pycodehash.preprocessing.lines_transformer import LinesTransformer

logger = logging.getLogger(__name__)


class WhitespaceNormalizer(LinesTransformer):
    """Normalize source code newlines

    The trailing whitespace is removed
    and line breaks are replaced with a semicolon
    (for identical cross-platform hashes).
    """

    def __init__(self):
        self.sep = "\n"

    def transform(self, src: str) -> str:
        """Removes whitespace from lines and joins lines with constant separator.

        Args:
            src: the source lines.

        Returns:
            The normalised string representation
        """
        logger.debug(f"Strip whitespace and replace platform-dependent line endings with {self.sep!r}")
        return self.sep.join(s.rstrip() for s in src.splitlines() if s)
