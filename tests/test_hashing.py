from __future__ import annotations
def test_builtin_handling():
    """Test handling of builtin modules."""
    # default setting: error="raise"
    fh = FunctionHasher()
    with pytest.raises(TypeError) as e_info:
        fh.hash_func(print)
    exp_msg = (
        "builtin function `print` cannot be hashed as there is no Python source code."
    )
    assert e_info.type is TypeError
    assert e_info.value.args[0] == exp_msg


def test_lambda_handling():
    """Test handling of builtin modules."""
    # default setting: error="raise"
    fh = FunctionHasher()
    with pytest.raises(ValueError) as e_info:
        fh.hash_func(lambda x: print(x))
    exp_msg = (
        "Source code for function `<lambda>` could not be found or does not exist."
    )
    assert e_info.type is ValueError
    assert e_info.value.args[0] == exp_msg
