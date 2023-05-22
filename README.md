# pycodehash

node := <id, module, func.src>
dataset := <id, type>
pipeline := [nodes]

hash(node) :=
-> preprocess (AST, Lines)
-> CallVisitor <-> calls
-> Resolve qualified name (tracer) <-> import bindings
-> Inliner
-> Hasher

preprocess(AST) :=
-> strip docstring
-> strip function name
-> strip type hints

preprocess(Lines) :=
-> normalize whitespace/newline

hash(dataset) :=
-> map type => approximate hasher
-> collect metadata
-> hasher
