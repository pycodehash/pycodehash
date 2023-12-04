from tliba.summary import compute_moments


def standalone_func():
    return list(range(100))


def wrapper_func():
    return compute_moments()
