import ast

from pycodehash.inlining import CallVisitor


def test_call_visitor():
    src = """
def hello():
    world()
    def foo(a, b):
        return hello(a + b + 3)
    
    MyClass.theMethod(3)
    foo(1, 3)
    foo(bar())
    
@decorated
def world(c, d: float) -> str:
    print(f"{c} {d}")
    
@MyClass.my_decorator
@MyClass.another_decorator()
@also_decorated(example="arguments")
def bar():
    fizzbuzz()
    hello().world(["mean", "sum"])
    hello().world(["mean", "sum"]).map(len).tolist()
    
def creator():
    a = MyClass()
    a.fit()
    """

    visitor = CallVisitor()
    visitor.visit(ast.parse(src))

    assert len(visitor.calls) == 16
    assert visitor.calls[0] == ("call", "world")
    assert visitor.calls[1] == ("call", "hello")
    assert visitor.calls[2] == ("call", "MyClass.theMethod")
    assert visitor.calls[3] == ("call", "foo")
    assert visitor.calls[4] == ("call", "foo")
    assert visitor.calls[5] == ("call", "bar")
    assert visitor.calls[6] == ("decorator", "decorated")
    assert visitor.calls[7] == ("call", "print")
    assert visitor.calls[8] == ("decorator", "MyClass.my_decorator")
    assert visitor.calls[9] == ("decorator call", "MyClass.another_decorator")
    assert visitor.calls[10] == ("decorator call", "also_decorated")
    assert visitor.calls[11] == ("call", "fizzbuzz")
    assert visitor.calls[12] == ("call", "hello")
    assert visitor.calls[13] == ("call", "hello")
    # note that `.world()` is currently ignored
    assert visitor.calls[14] == ("call", "MyClass")
    assert visitor.calls[15] == ("call", "a.fit")
