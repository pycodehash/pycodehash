from pathlib import Path

from pycodehash.datasets import LocalDirectoryHash, LocalFileHash

# Hash a single file
fh = LocalFileHash()

print(fh.collect_metadata("example.py"))
# {'last_modified': datetime.datetime(2023, 11, 24, 23, 38, 17, 524024), 'size': 621}

print(fh.compute_hash("example.py"))
# 2582e4198b42e6ceedeb58e05925da2480cdafddf87a731b971f315352beca47

# Hash a directory
dh = LocalDirectoryHash()

# Recursively hash all files in a directory
print(len(dh.collect_hashes(Path(__file__).parent / "src")))
# 29
