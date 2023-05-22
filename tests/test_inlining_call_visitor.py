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
    b = a[1][2][3]
    return type(self)(b).__finalize__(self)
    """

    visitor = CallVisitor()
    visitor.visit(ast.parse(src))

    assert len(visitor.calls) == 17
    assert visitor.calls[0] == ("world", )
    assert visitor.calls[1] == ("hello", )
    assert visitor.calls[2] == ("MyClass", "theMethod")
    assert visitor.calls[3] == ("foo", )
    assert visitor.calls[4] == ("foo", )
    assert visitor.calls[5] == ("bar", )
    assert visitor.calls[6] == ("decorated", )
    assert visitor.calls[7] == ("print", )
    assert visitor.calls[8] == ("MyClass", "my_decorator")
    assert visitor.calls[9] == ("MyClass", "another_decorator")
    assert visitor.calls[10] == ("also_decorated", )
    assert visitor.calls[11] == ("fizzbuzz", )
    assert visitor.calls[12] == ("hello", )
    assert visitor.calls[13] == ("hello", )
    # note that `.world()` is currently ignored
    # note that __getitem__ is currently ignored
    assert visitor.calls[14] == ("MyClass", )
    assert visitor.calls[15] == ("a", "fit")
    assert visitor.calls[16] == ("type", )
