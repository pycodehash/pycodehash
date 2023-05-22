from pathlib import Path
from typing import Callable

import pytest

from pycodehash.node import Node
from pycodehash.inlining.inliner import inline_node

import tliba.etl
import tlibb.etl
import tlibb.local


@pytest.mark.parametrize(["first_party", "reference_file", "entry_function", "reference_modules"], [
    (["tliba"], Path("./resources/inlined/tliba_etl.py"), tliba.etl.add_bernoulli_samples, ["tliba.etl", "tliba.random.rng", "tliba.random"]),
    (["tliba", "tlibb"], Path("./resources/inlined/tliba_tlibb_etl.py"), tlibb.etl.add_bernoulli_samples, ['tliba.etl', 'tliba.random.rng', 'tliba.random', 'tlibb.etl']),
    (["tlibb"], Path("./resources/inlined/tlibb_etl.py"), tlibb.etl.add_bernoulli_samples, ['tlibb.etl']),
    (["tlibb"], Path("./resources/inlined/tlibb_local.py"), tlibb.local.bar, ['tliba.etl', 'tliba.random.rng', 'tliba.random', 'tlibb.etl', 'tlibb.local', 'tlibb.a']),
    (["tliba", "pandas"], Path("./resources/inlined/tliba_pandas.py"), tliba.etl.add_bernoulli_samples, []),
], ids=[
    "tliba",
    "tliba & tlibb",
    "tlibb",
    "tlibb local",
    "tliba & pandas"
])
def test_inline(first_party: list[str], reference_file: Path, entry_function: Callable, reference_modules: list[str]):
    try:
        reference = reference_file.read_text()
    except FileNotFoundError:
        reference = ""

    node = Node(entry_function)
    expanded_source = inline_node(node, first_party=first_party)

    if expanded_source != reference:
        reference_file.with_stem(reference_file.stem + "_new").write_text(expanded_source)

    assert expanded_source == reference
