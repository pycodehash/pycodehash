# Detecting code changes

TODO: expand

## Python

`pycodehash`

### What makes it hard to find call definitions in Python

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

## SQL


## Pipelines and nodes

Always end up with a framework of some kind
_Nodes_ and _Pipelines_
Kedro, Airflow, dagster, [ZenML](https://docs.zenml.io/getting-started/introduction)
dbt