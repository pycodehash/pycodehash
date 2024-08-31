from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import tliba
from pycodehash import FunctionHasher
from tlibb.etl import combine_random_samples as tlibb_etl_combine_random_samples

from tests.python_function.standalone import standalone_func, wrapper_func

if TYPE_CHECKING:
    from types import FunctionType

    from rope.contrib.findit import Location


_REFERNCE_HASHES: dict[FunctionType, str] = {
    tliba.random.draw_beta_samples: "67368a1431e4d2a52682e24d2a77b3853c98d8a2aaeca3b91bd658906a30803a",
    tliba.random.draw_bernoulli_samples: "88abbb3570d3e10d94c2b961459bd9a0098f72a7c2efca793ac705d214cb4e74",
    tliba.etl.combine_random_samples: "d02be82025882229b1e87780b56eb5761bbf3335911b28261bebb5605de3bad7",
    tlibb_etl_combine_random_samples: "742e291eb1a634b919ddaf9a295d7ef8733860487fdf7fa813bb029a110570e8",
    tliba.summary.add_bernoulli_samples: "d88ea0c3977bb0bd1fa68f5970286fbe18218b0e78ad897ae4e28350c9618e11",
    standalone_func: "1b4196e28cc1e2a4658d151d1a31ae77a96ac190d98d31cadc80ccbc720ef6e3",
    wrapper_func: "a6bcb86d4331a0fddb3741a583038f31b707734a2f2bf8d1297c4b358251792c",
}

_REFERNCE_CALLS = {
    tliba.summary.add_bernoulli_samples: ("combine_random_samples", "draw_bernoulli_samples"),
    tliba.etl.combine_random_samples: ("draw_beta_samples", "draw_normal_samples"),
    tliba.random.draw_bernoulli_samples: ("draw_beta_samples",),
    tliba.summary.compute_conditional_moments: ("add_bernoulli_samples",),
}


def test_no_fp_calls():
    """Test hash of reference without first party calls."""
    tfunc = tliba.random.draw_beta_samples
    fh = FunctionHasher()
    result = fh.hash_func(tfunc)
    print(fh.func_ir_store[fh.get_func_location(tfunc)])
    assert _REFERNCE_HASHES[tfunc] == result


def test_within_module_fp_calls():
    """Test hash of reference with within module first-party calls."""
    tfunc = tliba.random.draw_beta_samples
    fh = FunctionHasher()
    result = fh.hash_func(tfunc)
    print(fh.func_ir_store[fh.get_func_location(tfunc)])
    assert _REFERNCE_HASHES[tfunc] == result


def test_across_module_fp_calls():
    """Test hash of reference with across module first party calls."""
    tfunc = tliba.etl.combine_random_samples
    fh = FunctionHasher()
    result = fh.hash_func(tfunc)
    print(fh.func_ir_store[fh.get_func_location(tfunc)])
    assert _REFERNCE_HASHES[tfunc] == result


def test_example_bernoulli_tliba():
    """Test hash of `add_bernoulli_samples` (which is used in `example.py`)"""
    tfunc = tliba.summary.add_bernoulli_samples
    fh = FunctionHasher()
    result = fh.hash_func(tfunc)
    print(fh.func_ir_store[fh.get_func_location(tfunc)])
    assert _REFERNCE_HASHES[tfunc] == result


def test_across_package_calls():
    """Test hash of reference with across pacakge first party calls."""
    tfunc = tlibb_etl_combine_random_samples
    # we first check that we don't trace functions if we don't explicitly set tliba
    fh = FunctionHasher()
    result = fh.hash_func(tfunc)
    ref_no_tliba = "9858b571a9ea3c93d56ce23a2a74e27418bf54666054f1612350d9c2c4bdb989"
    print(fh.func_ir_store[fh.get_func_location(tfunc)])
    assert ref_no_tliba == result

    fh = FunctionHasher(packages=["tliba", "tlibb"])
    result = fh.hash_func(tfunc)
    print(fh.func_ir_store[fh.get_func_location(tfunc)])
    assert _REFERNCE_HASHES[tfunc] == result


def test_standalone_module():
    """Test that functions from standalone modules can be picked up."""
    fh = FunctionHasher()

    tfunc = standalone_func
    result = fh.hash_func(tfunc)
    print(fh.func_ir_store[fh.get_func_location(tfunc)])
    assert _REFERNCE_HASHES[tfunc] == result

    tfunc = wrapper_func
    result = fh.hash_func(tfunc)
    print(fh.func_ir_store[fh.get_func_location(tfunc)])
    assert _REFERNCE_HASHES[tfunc] == result


def test_builtin_handling():
    """Test handling of builtin modules."""
    # default setting: error="raise"
    fh = FunctionHasher()
    with pytest.raises(TypeError) as e_info:
        fh.hash_func(print)
    exp_msg = "builtin function `print` cannot be hashed as there is no Python source code."
    assert e_info.type is TypeError
    assert e_info.value.args[0] == exp_msg


def test_lambda_handling():
    """Test handling of builtin modules."""
    # default setting: error="raise"
    fh = FunctionHasher()
    with pytest.raises(ValueError) as e_info:
        fh.hash_func(lambda x: print(x))  # noqa: PLW0108
    exp_msg = "Source code for function `<lambda>` could not be found or does not exist."
    assert e_info.type is ValueError
    assert e_info.value.args[0] == exp_msg


def test_call_collection():
    """Test that all the first party calls are collected."""

    def _get_fname(loc: Location):
        return loc.resource.read()[loc.region[0] : loc.region[1]]

    tfunc = tliba.summary.compute_conditional_moments
    fh = FunctionHasher()
    fh.hash_func(tfunc)

    calls = tuple(_get_fname(loc) for loc in fh.func_call_store[fh.get_func_location(tfunc)])
    assert calls == _REFERNCE_CALLS[tfunc]

    tfunc = tliba.summary.add_bernoulli_samples
    calls = tuple(_get_fname(loc) for loc in fh.func_call_store[fh.get_func_location(tfunc)])
    assert calls == _REFERNCE_CALLS[tfunc]

    tfunc = tliba.etl.combine_random_samples
    calls = tuple(_get_fname(loc) for loc in fh.func_call_store[fh.get_func_location(tfunc)])
    assert calls == _REFERNCE_CALLS[tfunc]

    tfunc = tliba.random.draw_bernoulli_samples
    calls = tuple(_get_fname(loc) for loc in fh.func_call_store[fh.get_func_location(tfunc)])
    assert calls == _REFERNCE_CALLS[tfunc]
