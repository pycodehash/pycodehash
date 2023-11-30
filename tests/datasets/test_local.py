import pytest
from pycodehash.datasets.local import LocalDirectoryHash, LocalFileHash


@pytest.fixture(scope="function")
def local_dataset(tmp_path):
    file_name = tmp_path / "my_file.txt"
    file_name.write_text("Hello World!")

    return file_name


@pytest.fixture(scope="function")
def local_dataset_directory(tmp_path):
    file_name1 = tmp_path / "my_file1.txt"
    file_name1.write_text("Hello Mercury!")
    file_name2 = tmp_path / "my_file2.txt"
    file_name2.write_text("Hello Mars!")
    file_name3 = tmp_path / "my_file3.txt"
    file_name3.write_text("Hello Venus!")
    return tmp_path


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


def test_approximate_hasher_local_directory(local_dataset_directory):
    hasher = LocalDirectoryHash()
    initial_metadata = hasher.collect_hashes(local_dataset_directory)
    assert isinstance(initial_metadata, dict)
    assert len(initial_metadata.keys()) == 3

    initial_hash = hasher.compute_hash(local_dataset_directory)
    assert isinstance(initial_hash, str)

    second_hash = hasher.compute_hash(local_dataset_directory)
    assert initial_hash == second_hash

    file_name4 = local_dataset_directory / "my_file4.txt"
    file_name4.write_text("Hello World!")

    third_hash = hasher.compute_hash(local_dataset_directory)
    assert initial_hash != third_hash

    third_metadata = hasher.collect_metadata(local_dataset_directory)
    assert len(third_metadata.keys()) == 4
