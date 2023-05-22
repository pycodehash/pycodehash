from pathlib import Path
from typing import Callable

import pytest

from pycodehash.node import Node
from pycodehash.inlining.inliner import inline_node, all_bindings

import tliba.etl
import tlibb.etl

@pytest.mark.parametrize(["first_party", "reference_file", "entry_function"], [
    (["tliba"], Path("./resources/inlined/tliba_etl.py"), tliba.etl.add_bernoulli_samples),
    (["tliba", "tlibb"], Path("./resources/inlined/tliba_tlibb_etl.py"), tlibb.etl.add_bernoulli_samples),
    (["tlibb"], Path("./resources/inlined/tlibb_etl.py"), tlibb.etl.add_bernoulli_samples),
    (["tliba", "pandas"], Path("./resources/inlined/tliba_pandas.py"), tliba.etl.add_bernoulli_samples),
])
def test_inline(first_party: list[str], reference_file: Path, entry_function: Callable):
    reference = reference_file.read_text()

    node = Node(entry_function)
    expanded_source = inline_node(node, first_party=first_party)

    if expanded_source != reference:
        reference_file.with_stem(reference_file.stem + "_new").write_text(expanded_source)

    assert expanded_source == reference
    print(all_bindings.keys())

# TODO: test multiple nodes don't duplicate work
# TODO: test only files are traced that are called
# TODO: test inlining with duplicate function names in different namespaces
# TODO: warning when inlinining > X MB or > N traces
