import abc
import ast


class Variables:
    def __init__(self):
        self.variables = set()
        self.functions = set()
        self.classes = set()
        self.import_statements = set()

    @property
    def all_symbols(self):
        return self.var_names | self.block_definitions | self.import_statements

    @property
    def var_names(self):
        return {var.id if isinstance(var, ast.Name) else var.arg for var in self.variables}

    @property
    def imports(self):
        return {var.asname or var.name for var in self.import_statements}

    @property
    def block_definitions(self):
        return {var.name for var in self.functions | self.classes}


class Scope(abc.ABC):
    def __init__(self):
        self.variables = Variables()

    def add_variable(self, node):
        self.variables.variables.add(node)

    def add_import(self, node):
        self.variables.import_statements.add(node)

    @abc.abstractmethod
    def add_child(self, scope):
        pass

    def add_function(self, node, function_scope, include_as_variable):
        if include_as_variable:
            self.variables.functions.add(node)
        self.add_child(function_scope)

    def add_class(self, node, class_scope):
        self.variables.classes.add(node)
        self.add_child(class_scope)

    @property
    def symbols_in_frame(self):
        return self.variables.all_symbols

    def __str__(self):
        return f"{self.__class__.__name__}: imports={self.variables.imports}, variables={self.variables.var_names}, blocks={self.variables.block_definitions}"


class ScopeWithChildren(Scope):
    def __init__(self):
        Scope.__init__(self)
        self.children = []

    def add_child(self, scope):
        self.children.append(scope)


class ScopeWithParent(Scope, abc.ABC):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent


class ErrorScope(Scope):
    def add_child(self, scope):
        raise RuntimeError("Error Scope cannot have children")


class GlobalScope(ScopeWithChildren):
   pass


class FunctionScope(ScopeWithChildren, ScopeWithParent):
    def __init__(self, function_node, parent):
        ScopeWithChildren.__init__(self)
        ScopeWithParent.__init__(self, parent)
        self.function_node = function_node


class ClassScope(ScopeWithParent):
    def __init__(self, class_node, parent):
        super().__init__(parent)
        self.class_node = class_node

    def add_child(self, scope):
        return self.parent.add_child(scope)
