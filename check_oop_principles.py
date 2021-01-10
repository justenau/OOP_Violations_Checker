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
            'Class is not compliant with Single Responsibility Principle. Cohesion among methods in class is low.',
            'COM-too-low',
            'Cohesion among methods in class is low.'
        ),
        'R0002': (
            'Class is not compliant with Single Responsibility Principle. CCM value (%d) is too high.',
            'CCM-too-high',
            'Cyclomatic Complexity in method is too high.'
        ),
    }

    options = (
        (
            'max-ccm',
            {
                'default': 10, 'type': 'int',
                'help': 'Set maximum allowed Cyclomatic Complexity value',
            }
        ),
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
            if self.config.max_ccm and complexity <= self.config.max_ccm or type(node.parent) is Module:
                continue
            self.add_message(
                "CCM-too-high", node=node, args=complexity
            )

    def visit_classdef(self, node):
        if node.name not in self.LCOM_values:
            return

        if self.LCOM_values[node.name] > 1:
            self.add_message(
                'COM-too-low', node=node,
            )


class LSPChecker(BaseChecker):
    __implements__ = IAstroidChecker
    node = None

    name = 'lsp-compliance'
    priority = -1
    msgs = {
        'R0003': (
            'Class is not compliant with Liskov Substitution principle.',
            'not-lsp-compliant',
            'Derived dlass method(s) degenerate base class methods.'
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
