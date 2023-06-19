# pycodehash

node := <id, module, func.src>
dataset := <id, type>
pipeline := [nodes]

hash(node) :=
-> ...


preprocess(AST) :=
-> strip docstring
-> strip function name
-> strip type hints

preprocess(Lines) :=
-> normalize whitespace/newlines

hash(dataset) :=
-> map type => approximate hasher
-> collect metadata
-> hasher

##

https://tree-sitter.github.io/tree-sitter/playground
https://github.com/kavigupta/ast_scope


scope(ast.Node) -> {variable: value}