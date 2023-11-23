import logging

from pycodehash import FunctionHasher
from pycodehash.preprocessing import DocstringStripper, FunctionStripper, TypeHintStripper, WhitespaceNormalizer

from tliba.etl import add_bernoulli_samples, combine_random_samples
from tliba import compute_moments

# Enable debugging
logging.basicConfig(level=logging.DEBUG)


fh = FunctionHasher(
    ast_transformers=[
        FunctionStripper(),
        DocstringStripper(),
        TypeHintStripper(),
    ],
    lines_transformers=[
        WhitespaceNormalizer(),
    ],
)
# Hash the function `add_bernoulli_samples`
h1 = fh.hash_func(add_bernoulli_samples)
print('Hash for `add_bernoulli_samples`', h1)

# Hash the function `compute_moments`
h2 = fh.hash_func(compute_moments)
print('Hash for `compute_moments`', h2)

# Hash the function `combine_random_samples`
h3 = fh.hash_func(combine_random_samples)
print('Hash for `combine_random_samples`', h3)
