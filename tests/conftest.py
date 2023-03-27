import ast
from pathlib import Path

import pytest


@pytest.fixture
def resource_file(file_name: str) -> Path:
    """pathlib.Path pointing towards test resource file

    Args:
        file_name: file path string in the resources directory

    Returns:
        absolute path towards the test resource file
    """
    return (Path("resources") / file_name).resolve()


@pytest.fixture
def resource_node(resource_file: Path) -> ast.AST:
    """Abstract-syntax-tree representation of source code in a file

    Args:
        resource_file: the resource fixture

    Returns:
        Parsed AST node
    """
    source_code = resource_file.read_text()
    return ast.parse(source_code)
