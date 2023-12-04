from pathlib import Path

from pycodehash.datasets import LocalDirectoryHash, LocalFileHash

# Hash a single file
fh = LocalFileHash()

print(fh.collect_metadata("example.py"))
# {'last_modified': datetime.datetime(2023, 11, 24, 23, 38, 17, 524024), 'size': 543}

print(fh.compute_hash("example.py"))
# 6189721d3ecdf86503a82c07eed82743069ebbf39e974f33ca684809e67e9e0e

# Hash a directory
dh = LocalDirectoryHash()

# Recursively hash all files in a directory
print(len(dh.collect_partitions(Path(__file__).parent / "src")))
# 29
