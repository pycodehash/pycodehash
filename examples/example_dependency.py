from pycodehash.dependency import PythonDependencyHash

# hash a list of dependencies
hasher = PythonDependencyHash()

print(hasher.collect_metadata(dependencies=["pycodehash", "rope"], add_python_version=True))
# hasher retrieves the installed package versions found
# {'pycodehash': '0.2.0', 'rope': '1.11.0', 'Python': '3.11'}

print(hasher.compute_hash(dependencies=["pycodehash", "rope"], add_python_version=True))
# cecb8036ad61235c2577db9943f519b824f7a25e449da9cd332bc600fb5dccf0
