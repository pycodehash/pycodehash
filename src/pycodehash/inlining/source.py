"""Get source code based on fully qualified names"""
import importlib
import inspect


def get_module_by_name(module_name: str):
    return importlib.import_module(module_name)


def get_function_by_name(function_name: str, module_name: str):
    return getattr(get_module_by_name(module_name), function_name)


def get_method_by_name(method_name: str, class_name: str, module_name: str):
    return getattr(get_function_by_name(class_name, module_name), method_name)


def get_module_source(module_name: str):
    return inspect.getsource(get_module_by_name(module_name))


def get_function_source(function_name: str, module_name: str):
    return inspect.getsource(get_function_by_name(function_name, module_name))


def get_method_source(method_name: str, class_name: str, module_name: str):
    src = inspect.getsource(get_method_by_name(method_name, class_name, module_name))
    news = "\n".join([line[4:] for line in src.splitlines()])
    return news
