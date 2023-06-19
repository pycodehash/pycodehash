import functools


def world_ops(arg):
    @functools.cache
    @functools.lru_cache(maxsize=100)
    def inner():
        print(f"Hello {arg}!")

    return inner


world = world_ops("world")
