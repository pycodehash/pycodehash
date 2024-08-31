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
assert h1 == "38d6e9f262ab77f6536e14c74be687ce2cb44cdebb7045e5b2f51946215cf4d0"
