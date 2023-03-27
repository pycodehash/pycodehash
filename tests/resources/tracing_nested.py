def foo():
    pass


def bar():
    pass


def fizz():
    def buzz():
        def bazz():
            pass

        return bazz

    return buzz


class Foo:
    class Bar:
        pass
