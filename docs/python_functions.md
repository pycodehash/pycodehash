# Detecting code changes

`pycodehash` attempts to reliably hash code that reflects changes to:

- the implementation
- the dependencies of the implementation
- the dependencies of the dependencies
- ...

but it is invariant to non-functional changes:

- function name
- formatting
- comments and docstrings
- type hints

## Algorithm

Given a Python function as source code we:

1. Create an Abstract Syntax Tree (AST)
2. **Replace the name of called functions with the hash of the function definition**
3. Remove invariant changes 
   - AST: Strip docstrings and type hints, and remove the function name
   - Unparse the AST to a string presentation
   - Lines: Normalize whitespace
4. Hash

## Abstract Syntax Tree

The AST is parsed using Pythons [standard library](https://docs.python.org/3/library/ast.html).
This step removed comments and normalises formatting.

The current implementation in addition uses the `asttokens` package to map AST nodes to their offset in the Python source code.
This is required to interact with `rope` (see below)

## Find call definitions

The inspiration for solving the dependency invariance comes from compilers/interpreters:

> Source code -> ... -> Interpreted/compiled -> ... -> Machine instructions 

Compilers often _inline_ code to enable additional transformations.
PyCodeHash applies the same concept.

For example, in the following code:

```python
def multiply(y, z):
    return y * z

def shift_left(x):
    return multiply(x, 2)
```

If we hash the source code of `shift_left`, then the hash is invariant to changes in multiply. This does not meet our desiderata.
By inlining `multiply`, this is no longer true:

```python
def shift_left(x):
    def multiply(y, z):
        return y * z
    return multiply(x, 2)
```

In our implementation, the function call is replaced with the hash of the source definition, rather than inlined:

```python
def shift_left(x):
    return 9e8c617fe2e0d524469d75f43edb1ff91f9a5387af6c444017ddcd194c983aed(x, 2) 
```

The implementation builds on [`rope`](https://github.com/python-rope/rope), an advanced open-source Python refactoring library.
This package performs a lot of heavy lifting. See the section "What makes it hard to find call definitions in Python" for details.

## Strip invariant changes

In this step, PyCodeHash transforms the AST to remove invariant syntax.
For this we implemented multiple `NodeTransformers` that can be found in `src/pycodehash/preprocessing/`.

Then we unparse the AST representation to obtain the Python source code (without comments and formatting).

On this string, we apply whitespace normalisation to ensure platform-independent hashes.

## Hashing

Finally, the resulting source code is hashed using `hash_string`.
The function uses the SHA256 algorithm provided by the [standard library](https://docs.python.org/3/library/hashlib.html).

## What makes it hard to find call definitions in Python

The example below illustrates how the dynamic nature of Python allows for various styles of function definition:

```python
data = [1, 2, 3, 4, 5]

# builtins
sum(data)


# function definition
def sum(x):
    return x + [6, 7, 8, 9]


sum(data)

from stats import sum

# import
sum(data)


def processing(y):
    # alias import in local scope
    from another.lib import multiply as sum

    sum(y)

    # enclosing scope
    def sum(z):
        return z * 2

    sum(y)


processing(data)

# dynamic function creating
def create_func(y):
    def func(x):
        return x + y

    return func


sum = create_func(3)
sum(data)
```

Read more on the [LEGB Rule for Python Scope](https://realpython.com/python-scope-legb-rule/#using-the-legb-rule-for-python-scope)
