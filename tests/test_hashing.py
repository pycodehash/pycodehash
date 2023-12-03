from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import tliba
from pycodehash import FunctionHasher
from tlibb.etl import combine_random_samples as tlibb_etl_combine_random_samples

if TYPE_CHECKING:
    from types import FunctionType

_REFERNCE_HASHES: dict[FunctionType, str] = {
    tliba.random.draw_beta_samples: "d36952212d075fc821149f80ca84f5c7974afd46f9aa19027e0db112e1b2a649",
    tliba.random.draw_bernoulli_samples: "88abbb3570d3e10d94c2b961459bd9a0098f72a7c2efca793ac705d214cb4e74",
    tliba.etl.combine_random_samples: "f390f9124ae848c40990c6306ac68145ee29131165c9973e17c9ceeff7fb9681",
    tlibb_etl_combine_random_samples: "482acd40279d561126e281ddc57be141e3f474ae466cdfc25ab82896a71e8fba",
    tliba.summary.add_bernoulli_samples: "9f084968cc4a3baf0743f49df222ca88d32db8d241b089f6d09d1adbc9014a74",
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
    ref_no_tliba = "b67a8c52603f12272b25c2c3a513cd14c7cfddf8163678897ab3f0986cf9fc8b"
    print(fh.func_ir_store[fh.get_func_location(tfunc)])
    assert ref_no_tliba == result

    fh = FunctionHasher(packages=["tliba", "tlibb"])
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
