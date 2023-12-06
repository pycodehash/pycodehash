from __future__ import annotations

import sys
from importlib.metadata import version

from pycodehash.datasets.approximate_hasher import ApproximateHasher


class PythonDependencyHash(ApproximateHasher):
    """Get the hash of a list of user-provided dependencies"""

    @staticmethod
    def collect_metadata(dependencies: list[str], add_python_version: bool = False) -> dict[str, str]:
        """Collect versions of list of provided dependency packages

        Args:
            dependencies: list of provided dependency packages. Eg. ["numpy", "pandas"]
            add_python_version: if true, add major.minor python version to output dictionary.

        Returns:
            Dictionary with dependency packages and their installed versions.
        """
        for dep in dependencies:
            if dep not in sys.modules:
                msg = f'No module named "{dep}"'
                raise ModuleNotFoundError(msg)
        metadata = {dep: version(dep) for dep in sorted(dependencies)}

        if add_python_version:
            metadata["Python"] = f"{sys.version_info.major}.{sys.version_info.minor}"

        return metadata
