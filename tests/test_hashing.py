import pytest
from pycodehash.hashing import hash_file_full


@pytest.fixture(scope="function")
def local_dataset(tmp_path):
    file_name = tmp_path / "my_file.txt"
    file_name.write_text("Hello World!")

    return file_name


def test_hash_file_full(local_dataset):
    assert hash_file_full(local_dataset) == "7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069"
