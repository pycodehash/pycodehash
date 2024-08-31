"""Script to check that the hashes of both implementations is the same."""

from pycodehash import FunctionHasher
from sample1 import func
from sample2 import create_df_mapping

fh = FunctionHasher()

h1 = fh.hash_func(func)
print("Hash for `func`", h1)

h2 = fh.hash_func(create_df_mapping)

print("Hash for `create_df_mapping`", h2)

assert h1 == h2
assert h1 == "316c8b82698ff62aa5e115e73efbd5ded6a7a7a27358a29bd0c289cd3d61f8c5"