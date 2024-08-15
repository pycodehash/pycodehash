# Detecting code changes in Python function

## Simplifying Hash Computation with Pure Functions

In the context of Python, implementing hash computations for arbitrary
functions can be challenging due to the language's dynamic nature. To
simplify this process and avoid having to implement a full Python
execution module, we restrict hashing to pure functions.

What are [pure functions]? In simple terms, a pure function is a function
that:

* Always returns the same output given the same inputs
* Has no side effects

In modern software engineering practices, lints like [mr-proper] can aid
in identifying and enforcing the purity of functions, making it a more
maintainable and efficient development process.

## How `pycodehash` detects code changes

`pycodehash` attempts to accurately detect code modifications by focusing on the
following aspects that reflect true changes to your implementation

### Functional Changes

* **Implementation**: Changes to the underlying logic of your code,
including new functionality or updates to existing behavior.
* **Dependencies**: Modifications to the external libraries, frameworks,
or modules upon which your code relies.
* **Transitive Dependencies**: Updates to the dependencies of your
dependencies, ensuring that `pycodehash` captures changes that may not be
immediately apparent.

### Ignored Non-Functional Changes

On the other hand, `pycodehash` intentionally ignores non-functional
modifications that do not affect the actual behavior of your code. These
include:

* **Function Name**: Renaming functions or variables does not change their
functionality.
* **Formatting**: Code formatting changes, such as indentation or line
wrapping, are disregarded.
* **Comments and Docstrings**: Comments and documentation strings may be
updated without affecting the code's execution.
* **Type Hints**: Changes to type hints do not impact the code's behavior.

By focusing on functional changes while ignoring non-functional
modifications, `pycodehash` provides a reliable way to detect true changes
in your code.

### Algorithm

Given a Python function as source code we:

1. Create an Abstract Syntax Tree (AST)
2. **Replace the name of called functions with the hash of the function definition**
3. Remove invariant changes
    * AST: Strip docstrings and type hints, and remove the function name
    * Unparse the AST to a string presentation
    * Lines: Normalize whitespace
4. Hash

### 1. Abstract Syntax Tree

The AST is parsed using Pythons [standard library](https://docs.python.org/3/library/ast.html).
This step removed comments and normalises formatting.

The current implementation in addition uses the `asttokens` package to map AST nodes to their offset in the Python source code.
This is required to interact with [rope] (see below)

### 2. Find call definitions

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

```text
def shift_left(x):
    return 9e8c617fe2e0d524469d75f43edb1ff91f9a5387af6c444017ddcd194c983aed(x, 2) 
```

Note that technically speaking, the code snippet is no longer valid Python
syntax due to the function name constraint: identifiers (such as function
names) cannot start with digits. According to the [Python reference
documentation](https://docs.python.org/3/reference/lexical_analysis.html#identifiers), this is a fundamental rule for Python's lexical analysis.

However, since we are only concerned with generating hashes and not
executing the code, the syntactical validity of the inlined code is
irrelevant. Even if the function name were to start with a digit,
prefixing the hash value would ensure that the resulting string is a valid
Python identifier, effectively guaranteeing its syntactical validity.

The implementation builds on [rope], an advanced open-source Python refactoring library.
This package performs a lot of heavy lifting.
See the section "The Challenge of Finding Call Definitions in Python" for details.

### 3. Strip invariant changes

In this step, PyCodeHash transforms the AST to remove invariant syntax.
For this we implemented multiple `NodeTransformers` that can be found in `src/pycodehash/preprocessing/`.

Then we unparse the AST representation to obtain the Python source code (without comments and formatting).

On this string, we apply whitespace normalisation to ensure platform-independent hashes.

### 4. Hashing

Finally, the resulting source code is hashed using `hash_string`.
The function uses the SHA256 algorithm provided by the [standard library](https://docs.python.org/3/library/hashlib.html).

## The Challenge of Finding Call Definitions in Python

Python's dynamic nature makes it difficult to find call definitions due to
the various ways functions can be defined. This section highlights some
examples that illustrate this challenge.

### Function Definition Variations

The following code snippets demonstrate different styles of function
definition:

```python
data = [1, 2, 3, 4, 5]

# Built-in function call (no explicit definition)
sum(data)

# Explicit function definition
def sum(x):
    return x + [6, 7, 8, 9]

sum(data)

from stats import sum

# Importing a function from another module
sum(data)
```

### Function Definition in Nested Scopes

Functions can be defined within other functions or modules, leading to
nested scopes. For example:

```python
def processing(y):
    # Import alias within local scope
    from another.lib import multiply as sum

    sum(y)

    # Enclosing scope function definition
    def sum(z):
        return z * 2

    sum(y)
```

### Dynamic Function Creation

Functions can also be created dynamically using closures. For instance:

```python
def create_func(y):
    def func(x):
        return x + y

    return func

sum = create_func(3)
sum(data)
```

Understanding these variations is crucial for effectively resolving call
definitions in Python.

Read more about the [LEGB Rule for Python Scope] to better grasp how scope and naming work in Python.

[pure functions]: https://en.wikipedia.org/wiki/Pure_function
[mr-proper]: https://github.com/best-doctor/mr_proper
[rope]: https://github.com/python-rope/rope
[LEGB Rule for Python Scope]: https://realpython.com/python-scope-legb-rule/#using-the-legb-rule-for-python-scope
