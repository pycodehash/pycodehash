import pytest
from pycodehash.datasets.local import LocalFileHash


@pytest.fixture(scope="function")
def local_dataset(tmp_path):
    file_name = tmp_path / "my_file.txt"
    file_name.write_text("Hello World!")

    return file_name


def test_approximate_hasher_local_file(local_dataset):
    hasher = LocalFileHash()
    initial_metadata = hasher.collect_metadata(local_dataset)
    assert isinstance(initial_metadata, dict)
    assert initial_metadata["size"] == 12

    initial_hash = hasher.compute_hash(local_dataset)
    assert isinstance(initial_hash, str)

    # Access
    local_dataset.read_text()

    second_hash = hasher.compute_hash(local_dataset)
    assert initial_hash == second_hash

    # Append
    with local_dataset.open("a") as fp:
        fp.write("Foo Bar!")

    third_hash = hasher.compute_hash(local_dataset)
    assert initial_hash != third_hash
    third_metadata = hasher.collect_metadata(local_dataset)
    assert third_metadata["size"] == 20
