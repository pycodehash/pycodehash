from pycodehash.python_module.python_module_hasher import PythonModuleHasher
from tliba.summary import compute_moments


def test_python_module_hasher_first_party():
    pmh = PythonModuleHasher(["tliba"])
    assert len(pmh.collect_partitions(compute_moments)) == 4
    assert pmh.modules == {
        "tliba.summary": {"tliba.etl"},
        "tliba.etl": {"tliba.random", "tliba.random.rng"},
        "tliba.random": {"tliba.random.rng"},
        "tliba.random.rng": set(),
    }
    assert pmh.compute_hash(compute_moments) == "a27e7cbaf064fe8975becb9099e40e0b13eec7982d6ca3dbfa6ad9d362fc61c3"
