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
    assert pmh.collect_metadata(compute_moments) == {
        "tliba.etl": "2bce4e1c857681febbc2a4fd29dcff45ea56aaf0e55d720c69017eb60d1ab7a9",
        "tliba.random": "e9c8f90484c672003b45bfe5eb63f14870e1f4bc4b2c6e685da97a8c11e75672",
        "tliba.random.rng": "31de2d05f98b1b3c15bff6936cd42a13382a3e17b4ad23167a0f4bdc6828fd73",
        "tliba.summary": "1bd82726ac6894c6a319d39fea833aed3a6f253eef4815e56dddfdd127bec504",
    }
    assert pmh.compute_hash(compute_moments) == "53e829a40578ecaaf89bf07deff1359f13abc90cf7cca424abc37c9afebb6f55"
