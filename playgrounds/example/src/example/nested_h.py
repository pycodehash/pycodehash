def bar():
    print('b1')


def func1():
    def bar():
        print('b2')
    def func2():
        bar()

    bar = lambda: print('b3')
    return func2


func1()()

# =>

# def func1():
#     def func2():
#         example.bar()
#     return nested_h.func1.<locals>.func2