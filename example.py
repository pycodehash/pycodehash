from pycodehash import hash_function
from pycodehash.preprocessing import FunctionStripper, DocstringStripper, TypeHintStripper, WhitespaceNormalizer
from pycodehash.tracing.stores import FunctionStore, ModuleStore, ProjectStore


def hello():
    return None


h1 = hash_function(
    hash_function,
    func_store=FunctionStore(),
    module_store=ModuleStore(),
    project_store=ProjectStore(),
    ast_transformers=[
        FunctionStripper(),
        DocstringStripper(),
        TypeHintStripper(),
    ],
    lines_transformers=[
        WhitespaceNormalizer(),
    ],
)
print(h1)
