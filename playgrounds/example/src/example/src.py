from __future__ import annotations

import functools
import sys

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self

import example.p7.x
import example.p7.x as y
from example.p1 import hello
from example.p2 import world as world_func
from example.p4 import bar, buzz, fizz, foobar
# Star without __all__
from example.p6 import *
# Star with __all__
from example.p8 import *
from example.p9 import my_func, another_func

print(MY_VAR)
bar()
buzz()
no()
from example.p7 import yes

yes()
example.p7.x.yes()
y.yes()




def _altrec_b(i=0):
    print(f"b{i}")
    if i < 5:
        altrec(i)


def altrec(i=0):
    print(f"a{i}")
    if i < 5:
        i += 1
        _altrec_b(i)

def rec(i=0):
    print(f"{i}")
    if i < 5:
        i += 1
        rec(i)

def bar():
    print("xyz")


foobar = bar


def lmbda(x):
    return print(x)

lmbda2 = lambda _: 4


class Foo:
    @classmethod
    def m1(cls):
        print("Foo.m1")

    class FooBar:
        @classmethod
        def m2(cls):
            print("Foo.FooBar.m2")


@functools.lru_cache(maxsize=12)
def foo():
    from example.p4 import buzz2 as buzz

    """
    Random Docstring
    """
    bar()
    bar()
    my_func(arg1=3)
    another_func(arg1=3)
    hello()
    # Comments
    world_func()
    foobar()
    fizz()
    buzz()
    def buzz():
        print("even different buzz")
    buzz()
    def buzz():
        print("another even different buzz")
    buzz()

    class Bar:
        def m1(self):
            """Docstr"""
            ...

        def chainmee(self) -> Self:
            print("chain")
            return self

        def __str__(self):
            return "BarObj"

        def __getitem__(self, item):
            return self

    lmbda("L")
    # rec()
    altrec()
    Foo.m1()
    Foo.FooBar.m2()
    Bar.m1(Bar())

    x = Bar().chainmee().chainmee().chainmee()
    print(x)
    b = Bar()
    b["abc"]["def"]
    y = Bar()["abc"]["def"]
    print(y)


fizz = hello


if __name__ == "__main__":
    foo()
