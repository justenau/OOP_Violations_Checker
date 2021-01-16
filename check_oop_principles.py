import astroid
import os
import subprocess
from astroid.nodes import Raise, Pass, Module
from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from pylint.extensions.mccabe import PathGraphingAstVisitor

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
        moduleName = os.path.normpath(node.file)
        command = f'lcom "{moduleName}"'
        lcom_result = subprocess.Popen(command, stdout=subprocess.PIPE)
        for bytes in lcom_result.stdout.readlines():
            line = bytes.decode('utf8').strip()
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
    node = None

    name = 'lsp-compliance'
    priority = -1
    msgs = {
        'R0005': (
            'Class is potentially violating Liskov Substitution principle.',
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
                if self._get_overriden_function(cls, function):
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

    def _get_overriden_function(self, cls, function):
        for base in cls.bases:
            base_cls = self.classes.get(base.name, None) if hasattr(base, 'name') else None
            if not base_cls:
                return None
            for base_function in [f for f in base_cls.get_children() if f.is_function]:
                if base_function.name == function.name:
                    return base_function
            func_overriden_from_root = self._get_overriden_function(base_cls, function)
            if func_overriden_from_root and not self._is_not_implemented(func_overriden_from_root):
                return func_overriden_from_root
        return None

def register(linter):
    linter.register_checker(SRPChecker(linter))
    linter.register_checker(LSPChecker(linter))
