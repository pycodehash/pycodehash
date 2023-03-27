from package1 import func1
from package2 import func1

from package3 import hello


def hello() -> str:
    return "world"


from package4 import bar

bar = hello
