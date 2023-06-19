i = 0
def rt(l, g):
    global i
    i+= 1
    b = l.get("__builtins__", None) or g.get("__builtins__", None)

    f = {'__package__', "__cached__", "__loader__", "__annotations__", "__doc__", "__spec__", "__file__",
         "__package__", "__builtins__"}

    g = dict(g.copy())
    l = dict(l.copy())
    glob = g.get("__name__", None) == "__main__"
    for k in f:
        if k in l:
            del l[k]
        if k in g:
            del g[k]

    if glob:
        print(i, l)
    else:
        print(i, l, g)



rt(locals(), globals())
theta = 3
rt(locals(), globals())
y = 1
rt(locals(), globals())
z= -1
def f():
    from annotate import annotate
    rt(locals(), globals())

    x = 3
    rt(locals(), globals())
    a = lambda z: theta
    rt(locals(), globals())

    x = annotate
    rt(locals(), globals())
    x, a = 3, annotate
    rt(locals(), globals())

    def x():
        rt(locals(), globals())
        return ("xyz")

    rt(locals(), globals())
    x()

    rt(locals(), globals())

    global z
    rt(locals(), globals())

    z = 0
    rt(locals(), globals())

    return x, y
rt(locals(), globals())

f()

rt(locals(), globals())
