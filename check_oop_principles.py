import astroid
import os
import subprocess
from astroid.nodes import Raise, Pass, Module
from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from pylint.extensions.mccabe import PathGraphingAstVisitor


def is_abstract_function(function):
    if function.decorators:
        for decorator_node in function.decorators.nodes:
            if (hasattr(decorator_node, 'expr') and decorator_node.expr.parent.attrname == 'abstractmethod'
                    or hasattr(decorator_node, 'name') and decorator_node.name == 'abstractmethod'):
                return True
    return False


def is_not_implemented(function, expression):
    expression_type = type(expression)
    return (is_abstract_function(function)
            or expression_type is Raise and expression.raises_not_implemented()
            or expression_type is Pass
            or expression_type is astroid.Return
            and (expression.value is None or hasattr(expression.value, 'value') and expression.value.value is None))


class SRPChecker(BaseChecker):
    __implements__ = IAstroidChecker

    name = 'srp-compliance'
    priority = -1
    msgs = {
        'R0001': (
            'Class is potentially violating Single Responsibility Principle. Cohesion among methods in class is low.',
            'srp-COM-too-low',
            'Cohesion among methods in class is low.'
        ),
        'R0002': (
            'Class method is potentially violating Single Responsibility Principle. CCM value (%d) is too high.',
            'srp-CCM-too-high',
            'Cyclomatic Complexity in method is too high.'
        ),
        'R0003': (
            'Class is potentially violating Single Responsibility Principle. It has too many (%d) public methods.',
            'srp-too-many-public-methods',
            'There are too many public methods.'
        ),
        'R0004': (
            'Class is potentially violating Single Responsibility Principle. It has too many (%d) attributes.',
            'srp-too-many-attributes',
            'There are too many class atributes.'
        ),
    }

    options = (
        (
            'srp-max-ccm',
            {
                'default': 10, 'type': 'int',
                'help': 'Set maximum allowed Cyclomatic Complexity value',
            },
        ),
        (
            'srp-max-public-methods',
            {
                'default': 20, 'type': 'int',
                'help': 'Set maximum amount of public methods per class',
            }
        ),
        (
            'srp-max-attributes',
            {
                'default': 15, 'type': 'int',
                'help': 'Set maximum amount of attributes per class',
            }
        )
    )

    def __init__(self, linter=None):
        super(SRPChecker, self).__init__(linter)
        self.LCOM_values = dict()

    def visit_module(self, node):
        self._ccm_checker_visit_module(node)
        self._calculate_lcom(node)

    def _calculate_lcom(self, node):
        module_name = os.path.normpath(node.file)
        command = f'lcom "{module_name}"'
        lcom_result = subprocess.Popen(command, stdout=subprocess.PIPE)
        for encoded_line in lcom_result.stdout.readlines():
            line = encoded_line.decode('utf8').strip()
            if line.find('.') > 0 and not any(['Average' == word for word in line.split()]):
                result = line.split('.')[-1].split('|')
                self.LCOM_values[result[0].strip()] = int(result[1].strip())

    def _ccm_checker_visit_module(self, node):
        visitor = PathGraphingAstVisitor()
        for child in node.body:
            visitor.preorder(child, visitor)
        for graph in visitor.graphs.values():
            complexity = graph.complexity()
            node = graph.root
            if self.config.srp_max_ccm and complexity <= self.config.srp_max_ccm or type(node.parent) is Module:
                continue
            self.add_message(
                'srp-CCM-too-high', node=node, args=complexity
            )

    def visit_classdef(self, node):
        if len(node.instance_attrs) > self.config.srp_max_attributes:
            self.add_message(
                'srp-too-many-attributes',
                node=node,
                args=len(node.instance_attrs),
            )

        if node.name not in self.LCOM_values:
            return

        if self.LCOM_values[node.name] > 1:
            self.add_message(
                'srp-COM-too-low', node=node,
            )

    def leave_classdef(self, node):
        my_methods = sum(
            1 for method in node.mymethods() if not method.name.startswith("_")
        )
        if my_methods > self.config.srp_max_public_methods:
            self.add_message(
                'srp-too-many-public-methods',
                node=node,
                args=my_methods,
            )


class LSPChecker(BaseChecker):
    __implements__ = IAstroidChecker

    name = 'lsp-compliance'
    priority = -1
    msgs = {
        'R0005': (
            'Class is potentially violating Liskov Substitution principle. Derived class method(s) degenerate base '
            'class methods.',
            'not-lsp-compliant',
            'Derived class method(s) degenerate base class methods.'
        )
    }

    def __init__(self, linter=None):
        super(LSPChecker, self).__init__(linter)
        self.classes = dict()

    def visit_classdef(self, node):
        self.classes[node.name] = node

    def close(self):
        self._check_lsp()

    def _check_lsp(self):
        for name, cls in self.classes.items():
            if not cls.bases:
                continue
            for function in [f for f in cls.get_children() if f.is_function and self._is_not_implemented(f)]:
                if self._get_overridden_function(cls, function):
                    self.add_message('not-lsp-compliant', node=function)

    def _is_not_implemented(self, expr):
        expr_type = type(expr)
        if expr_type is Raise and expr.raises_not_implemented() or expr_type is Pass:
            return True
        if hasattr(expr, 'body'):
            for exp in expr.body:
                if self._is_not_implemented(exp):
                    return True
        if hasattr(expr, 'orelse'):
            for exp in expr.orelse:
                if self._is_not_implemented(exp):
                    return True
        return False

    def _get_overridden_function(self, cls, function):
        for base in cls.bases:
            base_cls = self.classes.get(base.name, None) if hasattr(base, 'name') else None
            if not base_cls:
                return None
            for base_function in [f for f in base_cls.get_children() if f.is_function]:
                if base_function.name == function.name and not self._is_not_implemented(base_function):
                    return base_function
            func_overridden_from_root = self._get_overridden_function(base_cls, function)
            if func_overridden_from_root and not self._is_not_implemented(func_overridden_from_root):
                return func_overridden_from_root
        return None


class ISPChecker(BaseChecker):
    __implements__ = IAstroidChecker

    name = 'isp-compliance'
    priority = -1
    msgs = {
        'R0006': (
            'Interface is potentially violating Interface Segregation Principle. '
            'Interface "%s" is not fully implemented by client class "%s".',
            'not-isp-compliant',
            'Interface method is not used by client class.'
        )
    }

    def __init__(self, linter=None):
        super(ISPChecker, self).__init__(linter)
        self.classes = dict()
        self.interfaces = dict()

    def visit_classdef(self, node):
        self.classes[node.name] = node
        if self._is_interface(node):
            self.interfaces[node.name] = node

    @staticmethod
    def _is_interface(node):
        functions = [f for f in node.get_children() if f.is_function]
        for function in functions:
            expression = function.body[0] if function.body else None
            if expression is None:
                continue
            if not is_not_implemented(function, expression):
                return False
        return len(functions) > 0

    def close(self):
        self._check_isp_compliance()

    def _check_isp_compliance(self):
        for name, cls in self.classes.items():
            for base_cls in cls.bases:
                if (hasattr(base_cls, 'name') and base_cls.name in self.interfaces
                        and not self._is_fully_implemented(cls, self.interfaces[base_cls.name])):
                    self.add_message(
                        'not-isp-compliant',
                        node=self.interfaces[base_cls.name],
                        args=(base_cls.name, cls.name)
                    )

    @staticmethod
    def _is_fully_implemented(cls, interface):
        interface_functions = [f for f in interface.get_children() if f.is_function]
        cls_functions = [f for f in cls.get_children() if f.is_function]
        for func in interface_functions:
            match = next((f for f in cls_functions if f.name == func.name), None)
            if not match:
                return False
            expression = match.body[0]
            if is_not_implemented(match, expression):
                return False
        return True


class DIPChecker(BaseChecker):
    __implements__ = IAstroidChecker

    name = 'dip-compliance'
    priority = -1
    msgs = {
        'R0007': (
            'Class is potentially violating Dependency Inversion Principle. '
            'Class "%s" overrides already implemented base class method "%s".',
            'not-dip-compliant',
            'Implemented base class method is overridden.'
        )
    }

    def __init__(self, linter=None):
        super(DIPChecker, self).__init__(linter)
        self.classes = dict()

    def visit_classdef(self, node):
        self.classes[node.name] = node

    def close(self):
        self._check_dip()

    def _check_dip(self):
        for name, cls in self.classes.items():
            if not cls.bases:
                continue
            for function in [f for f in cls.get_children() if f.is_function]:
                if self._overrides_implemented_function(cls.bases, function):
                    self.add_message('not-dip-compliant', node=function, args=(cls.name, function.name))

    def _overrides_implemented_function(self, bases, function):
        for base in bases:
            base_cls = self.classes.get(base.name, None) if hasattr(base, 'name') else None
            if not base_cls:
                return None
            for base_function in [f for f in base_cls.get_children() if f.is_function]:
                if (base_function.name == function.name
                        and not self._returns_super_method(function)
                        and not self._is_not_implemented(base_function) and not self._is_not_implemented(function)):
                    return base_function

    @staticmethod
    def _returns_super_method(function):
        expression = function.body[0] if function.body else None
        if expression is None:
            return False
        try:
            return len(function.body) == 1 and expression.value.func.expr.func.name == 'super'
        except AttributeError:
            return False

    @staticmethod
    def _is_not_implemented(function):
        expression = function.body[0] if function.body else None
        if expression is None:
            return True
        return is_not_implemented(function, expression)


def register(linter):
    linter.register_checker(SRPChecker(linter))
    linter.register_checker(LSPChecker(linter))
    linter.register_checker(ISPChecker(linter))
    linter.register_checker(DIPChecker(linter))
