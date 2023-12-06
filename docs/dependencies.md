# Detecting version changes in relevant Python packages

`pycodehash` provides some functionality to hash, and thus keep track of,
the version numbers of the Python packages most relevant to your pipeline or framework.

We emphasize it is up to the user to provide the list of relevant package dependencies.
This list may be different per executed function or node in a pipeline, 
and clearly this may be a selection of the total list of Python dependencies.
For example, provide the most important libraries your code depends on, 
and that you want to track in order to trigger a rerun of your pipeline in case of package version changes.


The class `PythonDependencyHash` hashes a user-provided list of Python packages. 
The hasher retrieves the installed package versions and creates a hash of those. 
Optionally the Python version can be included in the hash.


```python
from pycodehash.dependency import PythonDependencyHash

# hash a list of dependencies
hasher = PythonDependencyHash()

print(hasher.collect_metadata(dependencies=["pycodehash", "rope"], add_python_version=True))
# hasher retrieves the installed package versions found
# {'pycodehash': '0.2.0', 'rope': '1.11.0', 'Python': '3.11'}

print(hasher.compute_hash(dependencies=["pycodehash", "rope"], add_python_version=True))
# cecb8036ad61235c2577db9943f519b824f7a25e449da9cd332bc600fb5dccf0
```

Alternatively, one may wish to track all Python packages installed in 
ones environment. 
In that case call `pip freeze > requirements_freeze.txt` and then make a hash of the file `requirements_freeze.txt`, 
as detailed below.

```python
from pycodehash.datasets import LocalFileHash

# Hash a single file
fh = LocalFileHash()

hash = fh.compute_hash("requirements_freeze.txt"))
```

Comparing this hash with a previous hash allows one to keep track of all changing versions in the total list of installed packages.
