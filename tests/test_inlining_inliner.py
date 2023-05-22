from pathlib import Path

import pytest

from pycodehash.node import Node
from pycodehash.inlining.inliner import inline_node, all_bindings

import tliba.etl



@pytest.fixture()
def reference():
    return '''def draw_normal_samples():
    """Create table consisting of 5000 draws from a standard normal distribution."""
    return pd.DataFrame(np.random.normal(0, 1, 5000), columns=["normal"])
def combine_random_samples():
    return pd.concat((rng.draw_beta_samples(), normal_samples()), axis=1)
def draw_beta_samples():
    """Create table consisting of 5000 draws from a Beta(2, 5) distribution."""
    return pd.DataFrame(np.random.beta(2, 5, 5000), columns=["beta"])
def draw_bernoulli_samples():
    """Create table consisting of 5000 draws from a bernoulli distribution where the probability is drawn form a Beta(2, 5)."""
    return pd.DataFrame(
        np.random.binomial(1, draw_beta_samples().values.flatten(), 5000),
        columns=["binomial"],
    )
def add_bernoulli_samples():
    df = combine_random_samples().copy()
    df["bernoulli"] = draw_bernoulli_samples()
    return df
'''


def test_inline_tliba(reference):
    first_party = ["tliba"]
    node = Node(tliba.etl.add_bernoulli_samples)
    expanded_source = inline_node(node, first_party=first_party)
    assert expanded_source == reference
    print(all_bindings.keys())


def test_inline_tliba_pandas():
    reference = Path("resources/inline_pandas.py").read_text()
    first_party = ["tliba", "pandas"]
    node = Node(tliba.etl.add_bernoulli_samples)
    expanded_source = inline_node(node, first_party=first_party)
    assert expanded_source == reference
    # print(all_bindings.keys())
    # Path("resources/inline_pandas.py").write_text(expanded_source)


# TODO: test multiple nodes don't duplicate work
# TODO: test only files are traced that are called
# TODO: test inlining with duplicate function names in different namespaces
# TODO: warning when inlinining > X MB or > N traces
