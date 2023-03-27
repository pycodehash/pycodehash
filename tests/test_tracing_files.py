import pytest

from pycodehash.tracing.files import trace_file


@pytest.mark.parametrize("file_name", ["tliba/src/tliba/etl.py"])
def test_trace_file(resource_file):
    trace_file(resource_file, ("tliba",))
