"""Tests for the tracer"""
import pytest

from pycodehash.tracer import Tracer


@pytest.mark.parametrize("file_name", ["tracing_imports_std.py"])
def test_tracing(resource_node):
    v = Tracer("xyz")
    v.visit(resource_node)
    assert v.import_bindings["hello"] == ("xyz", "hello")
    assert v.import_bindings["F"] == ("functools", )
    assert v.import_bindings["cache"] == ("functools", "lru_cache")
    assert len([1 for v in v.import_bindings.values() if v[0] != '__builtins__']) == 6


@pytest.mark.parametrize("file_name", ["tracing_imports_star.py"])
def test_tracing_star(resource_node):
    v = Tracer("xyz")
    with pytest.raises(NotImplementedError) as msg:
        v.visit(resource_node)

    assert msg.value.args[0] == "Star imports are not supported"


@pytest.mark.parametrize("file_name", ["tracing_nested.py"])
def test_tracing_nested(resource_node):
    v = Tracer("xyz")
    v.visit(resource_node)

    assert "buzz" not in v.import_bindings
    assert "bazz" not in v.import_bindings


@pytest.mark.parametrize("file_name", ["tliba/src/tliba/etl.py"])
def test_tracing_package(resource_node):
    v = Tracer("xyz")
    v.visit(resource_node)

    assert v.import_bindings["pd"] == ("pandas", )
    assert v.import_bindings["rng"] == ("tliba.random.rng", )
    assert v.import_bindings["combine_random_samples"] == ("xyz", "combine_random_samples")
    assert v.import_bindings["add_bernoulli_samples"] == ("xyz", "add_bernoulli_samples")
    assert v.import_bindings["draw_bernoulli_samples"] == ("tliba.random", "draw_bernoulli_samples")
    assert v.import_bindings["normal_samples"] == ("tliba.random", "draw_normal_samples")
    assert len([1 for v in v.import_bindings.values() if v[0] != '__builtins__']) == 6


@pytest.mark.parametrize("file_name", ["tracing_imports_relative.py"])
def test_tracing_relative_imports(resource_node):
    v = Tracer("xyz")
    with pytest.raises(NotImplementedError) as msg:
        v.visit(resource_node)

    assert msg.value.args[0] == "Relative imports are not supported"


@pytest.mark.parametrize("file_name", ["tracing_imports_overwrite.py"])
def test_tracing_overwrite(resource_node):
    v = Tracer("xyz")
    v.visit(resource_node)

    assert v.import_bindings["func1"] == ("package2", "func1")
    assert v.import_bindings["hello"] == ("xyz", "hello")
    assert v.import_bindings["bar"] == ("xyz", "hello")
    assert len([1 for v in v.import_bindings.values() if v[0] != '__builtins__']) == 3


@pytest.mark.parametrize("file_name", ["tracing_class.py"])
def test_tracing_class(resource_node):
    v = Tracer("xyz")
    v.visit(resource_node)

    assert v.import_bindings["NDFrame"] == ("xyz", "NDFrame")
    assert v.import_bindings["NDFrame.__init__"] == ("xyz", "NDFrame", "__init__")


@pytest.mark.parametrize("file_name", ["tracing_builtins.py"])
def test_tracing_builtins(resource_node):
    v = Tracer("xyz")
    v.visit(resource_node)

    assert all(v[0] == "__builtins__" for v in v.import_bindings.values())
    assert len(v.import_bindings) == 72

