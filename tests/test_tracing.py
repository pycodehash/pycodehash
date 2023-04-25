"""Tests for the tracer"""
import pytest

from pycodehash.tracing import Tracer


@pytest.mark.parametrize("file_name", ["tracing_imports_std.py"])
def test_tracing(resource_node):
    v = Tracer()
    v.visit(resource_node)
    assert v.import_bindings["hello"] == "__main__.hello"
    assert v.import_bindings["F"] == "functools"
    assert v.import_bindings["cache"] == "functools.lru_cache"
    assert len(v.import_bindings) == 6


@pytest.mark.parametrize("file_name", ["tracing_imports_star.py"])
def test_tracing_star(resource_node):
    v = Tracer()
    with pytest.raises(NotImplementedError) as msg:
        v.visit(resource_node)

    assert msg.value.args[0] == "Star imports are not supported"


@pytest.mark.parametrize("file_name", ["tracing_nested.py"])
def test_tracing_nested(resource_node):
    v = Tracer()
    v.visit(resource_node)

    assert "buzz" not in v.import_bindings
    assert "bazz" not in v.import_bindings


@pytest.mark.parametrize("file_name", ["tliba/src/tliba/etl.py"])
def test_tracing_package(resource_node):
    v = Tracer()
    v.visit(resource_node)

    assert v.import_bindings["pd"] == "pandas"
    assert v.import_bindings["rng"] == "tliba.random.rng"
    assert v.import_bindings["combine_random_samples"] == "__main__.combine_random_samples"
    assert v.import_bindings["add_bernoulli_samples"] == "__main__.add_bernoulli_samples"

    print(v.import_bindings)
    # via __init__.py
    assert v.import_bindings["draw_bernoulli_samples"] == "tliba.random.rng.draw_bernoulli_samples"
    assert v.import_bindings["normal_samples"] == "tliba.random.rng.normal_samples"
    assert len(v.import_bindings) == 6


@pytest.mark.parametrize("file_name", ["tracing_imports_relative.py"])
def test_tracing_relative_imports(resource_node):
    v = Tracer()

    with pytest.raises(NotImplementedError) as msg:
        v.visit(resource_node)

    assert msg.value.args[0] == "Relative imports are not supported"


@pytest.mark.parametrize("file_name", ["tracing_imports_overwrite.py"])
def test_tracing_overwrite(resource_node):
    v = Tracer()
    v.visit(resource_node)

    assert v.import_bindings["func1"] == "package2.func1"
    assert v.import_bindings["hello"] == "__main__.hello"
    assert v.import_bindings["bar"] == "__main__.hello"
    assert len(v.import_bindings) == 3
