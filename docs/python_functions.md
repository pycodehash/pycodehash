# Detecting code changes in Python function

## How `pycodehash` detects code changes

`pycodehash` attempts to accurately detect code modifications by focusing on the
following aspects that reflect true changes to your implementation

**Functional Changes**:

* _Implementation_: Changes to the underlying logic of your code,
including new functionality or updates to existing behavior.
* _Dependencies_: Modifications to the external libraries, frameworks,
or modules upon which your code relies.
* _Transitive Dependencies_: Updates to the dependencies of your
dependencies, ensuring that `pycodehash` captures changes that may not be
immediately apparent.

**Ignored Non-Functional Changes**:

On the other hand, `pycodehash` intentionally ignores non-functional
modifications that do not affect the actual behavior of your code. These
include:

* _Function Name_: Renaming functions or variables does not change their functionality.
* _Formatting_: Code formatting changes, such as indentation or line wrapping, trailing commas, are disregarded.
* _Comments and Docstrings_: Comments and documentation strings may be updated without affecting the code's execution.
* _Type Hints_: Changes to type hints do not impact the code's behavior.
* _Dead code elimination_: [Unused imports](https://pylint.pycqa.org/en/latest/user_guide/messages/warning/unused-import.html), [unused variables](https://pylint.readthedocs.io/en/stable/user_guide/messages/warning/unused-variable.html), unused arguments in formatting, [duplicate dictionary keys](https://pylint.pycqa.org/en/latest/user_guide/messages/warning/duplicate-key.html)
* _Newer Python Syntax_: super calls, set literals, etc. See [pyupgrade](https://github.com/asottile/pyupgrade) for details.
* _Miscellaneous code style idiom and conventions_: [simplified comprehensions](https://github.com/adamchainz/flake8-comprehensions), [dictionary key membership checks](https://github.com/MartinThoma/flake8-simplify/issues/40), [import ordering](https://github.com/PyCQA/isort), [unnecessary return syntax](https://pypi.org/project/flake8-return/)  

By focusing on functional changes while ignoring non-functional
modifications, `pycodehash` provides a reliable way to detect true changes
in your code.

See the two equivalent code snippets in the [Equivalence example](examples/equivalance/) for examples of the non-functional changes listed below.

## Code change detection guarantees

For code change detection: False positive matches are possible, but false negatives are not*.
In other words, if the hash of two functions is equal, it's guaranteed there is no functional change.
If the hashes are not equal, then it's likely, but not guaranteed that there is no functional change.
These guarantees are analogous to that of the [bloom filter] probabilistic data structure.

* Except for hash collisions that are caused by the choice of hashing algorithm, by default SHA512.

## Simplifying Hash Computation with Pure Functions

In the context of Python, implementing hash computations for arbitrary
functions can be challenging due to the language's dynamic nature. To
simplify this process and avoid having to implement a full Python
execution module, we restrict hashing to [pure functions].

In simple terms, a pure function is a function that:

* Always returns the same output given the same inputs
* Has no side effects

Requiring Python functions to be pure is not a significant restriction,
but rather a natural design principle. Pure functions are easier to test
and have predictable behavior.

## Algorithm

Given a Python function as source code we:

1. Initialize or load the function's package source
2. Create an Abstract Syntax Tree (AST) for the provided function
3. **Replace the name of called functions with the hash of the function definition**
4. Remove invariant changes
    * AST: Strip docstrings and type hints, and remove the function name
    * Unparse the AST to a string presentation
    * Lines: Normalize whitespace
5. Unparse the AST and normalise
6. Hash

### 1. Package initialization

PyCodeHash initializes a package when it's first encountered, e.g., in `from my_package.functions import func`, `my_package` would be the package.
The initialization phase consists of:

* Copying the source to a temporary directory (enabled by default)
* Indexing the source via static object analysis on all python files (via `rope`)
* Brining the source in a canonical form where possible via auto-fixing lint violations (via `ruff`)

### 2. Abstract Syntax Tree

The AST is parsed using Pythons [standard library](https://docs.python.org/3/library/ast.html).
This step removed comments and normalises formatting.

### 3. Find call definitions

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
    return c_9e8c617fe2e0d524469d75f43edb1ff91f9a5387af6c444017ddcd194c983aed(x, 2) 
```

Note that the hash is prefixed with an `c_` (for call) to ensure syntactical validity.
Hashes can start with digits, which makes the code snippet is no longer valid Python
syntax due to the function name constraint: identifiers (such as function
names) cannot start with digits. According to the [Python reference
documentation](https://docs.python.org/3/reference/lexical_analysis.html#identifiers), this is a fundamental rule for Python's lexical analysis.
Syntactical validity is required to be able to use tools that transform the code afterward.

The implementation builds on [rope], an advanced open-source Python refactoring library.
This package performs a lot of heavy lifting.
See the section "The Challenge of Finding Call Definitions in Python" for details.

### 4. Strip invariant AST changes

In this step, PyCodeHash transforms the AST to remove invariant syntax.
For this we implemented multiple `NodeTransformers` that can be found in `src/pycodehash/preprocessing/`.

### 5. Unparse AST and normalise

Then we unparse the AST representation to obtain the Python source code (without comments and formatting).

On this string, we apply whitespace normalisation to ensure platform-independent hashes.

### 6. Hashing

Finally, the resulting source code is hashed using `hash_string`.
The function uses the SHA256 algorithm provided by the [standard library](https://docs.python.org/3/library/hashlib.html).

## The Challenge of Finding Call Definitions in Python

Python's dynamic nature makes it difficult to find call definitions due to
the various ways functions can be defined. This section highlights some
examples that illustrate this challenge.

### Naive approach to hashing

We can use the `inspect` module to get the source code of the
function as a string, and then compute its hash.

Here's an example:

```python
import inspect

from pycodehash.hashing import hash_string

def my_function(x):
    return x * 2

# Get the source code of the function as a string
func_str = inspect.getsource(my_function)

# Compute the hash value. Uses the stdlib `hashlib.sha256` underneath
hash_value = hash_string(func_str)

print(hash_value)
```

Please note that this approach has a serious limitation:

It only works for functions with simple source code. If the function
has a very long or complex implementation (e.g., due to many nested
loops), computing its hash might be problematic.

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

## Cant we use Python's built-in hashing functions?

In Python, there is the built-in `hash()` function or the `__hash__`
method in classes to compute a hash value for an object, which is an
integer that represents the "identity" of the object being hashed.
When you call `hash()` on an
object, it computes the hash value on-the-fly using the object's
attributes and methods.
The built-in `hash()` function in Python cannot be used
to reliably compare if the content of a function has changed because
even if two functions have the same source code, there's no guarantee
that their hash values will remain stable across different runs of your program or in different environments.

Python also has a built-in library to "hash" your functions, namely [hashlib],
which provides secure and efficient hashing algorithms. The [cryptography] package
is an example of a third-party packages that also offers such cryptographic algorithms.
However, these libraries are designed for general-purpose hashing, not specifically for
computing hashes of Python functions.

## Tips for writing Pure Functions

### How to make functions with randomness pure?

To make functions with randomness pure, pass the seed value or random number generator object as an argument.

For instance:

```python
import numpy as np

def my_random_function(seed: int) -> int:
    """A function that generates a random number between 1 and 10.
    
    Args:
        seed: The seed value for the random number generator.

    Returns:
        A random number between 1 and 10.
    """
    rng = np.random.default_rng(seed)
    return rng.integers(1, 10)

# Usage example:
print(my_random_function(42))  # Always generates the same output (if seeded correctly)
```

This way, you can control the sequence of random numbers generated by the
RNG and make your function's output deterministic.

### Tools for enforcing pureness

In modern software engineering practices, lints like [mr-proper] can aid
in identifying and enforcing the purity of functions, making it a more
maintainable and efficient development process.

## Implementation Considerations

To maximize development efficiency and minimize long-term maintenance burdens, this library uses established third-party libraries rather than implementing similar functionality from scratch.
Hence, PyCodeHash is built on top of `rope` (for call tracing) and `ruff` (for applying a multitude of invariant changes).
The current implementation in addition uses the `asttokens` package to map AST nodes to their offset in the Python source code, which is required to interact with [rope].
This results in an effective library that can be used today.

This approach does come with some trade-offs, however.
By relying on external libraries, we sacrifice access to internal state from these programs, such as the control-flow graph that may be useful for more highly optimized or specialized functionality.
Users who already have access to their own control-flow graphs may find it more beneficial to implement equivalent functionality directly within their own systems.

[pure functions]: https://en.wikipedia.org/wiki/Pure_function
[mr-proper]: https://github.com/best-doctor/mr_proper
[rope]: https://github.com/python-rope/rope
[LEGB Rule for Python Scope]: https://realpython.com/python-scope-legb-rule/#using-the-legb-rule-for-python-scope
[hashlib]: https://docs.python.org/3/library/hashlib.html
[cryptography]: https://cryptography.io/en/latest/
[bloom filter]: https://en.wikipedia.org/wiki/Bloom_filter
