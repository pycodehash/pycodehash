from functools import wraps


def decorator(func):
    """Docstring"""
    d = 1
    e = 1
    a = 1

    @wraps(func)
    def inner(*args, **kwargs):
        ret = func(*args, **kwargs)
        return (ret + d) * e + a
    return inner


def decorator_with_args(d, e : int = 1, a : int = 1):
    """Docstring"""
    def pseudo_decorator(func):
        @wraps(func)  # comment
        def inner(*args, **kwargs):
            ret = func(*args, **kwargs)
            return (ret + d) * e + a

        return inner
    return pseudo_decorator


@decorator
@decorator_with_args(3, a=4)
def my_func(arg1: int, **kwargs):
    return 1  # comment


def another_func_base(arg1: int, **kwargs):
    return 2


another_func = decorator(decorator_with_args(1, 2, 3)(another_func_base))
