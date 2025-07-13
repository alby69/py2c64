# py2c64/lib/func_structures.py

import ast
from lib.ast_processor import AstProcessor
from lib.func_core import FuncCore
from lib.func_operations import FuncOperations
from lib.func_expressions import FuncExpressions
from lib.func_strings import FuncStrings
from lib.func_dict import FuncDict
from lib.func_c64 import FuncC64
from lib.func_builtins import FuncBuiltins
from lib.c64_routine_library import C64RoutineLibrary
import globals

class FuncStructures:
    def __init__(self, ast_processor: AstProcessor, func_core: FuncCore, func_operations: FuncOperations, func_expressions: FuncExpressions, func_strings: FuncStrings, func_dict: FuncDict, func_c64: FuncC64, func_builtins: FuncBuiltins, c64_routine_library: C64RoutineLibrary, globals: Globals):
        self.ast_processor = ast_processor
        self.func_core = func_core
        self.func_operations = func_operations
        self.func_expressions = func_expressions
        self.func_strings = func_strings
        self.func_dict = func_dict
        self.func_c64 = func_c64
        self.func_builtins = func_builtins
        self.c64_routine_library = c64_routine_library
        self.globals = globals

    def _handle_if(self, node: ast.If) -> str:
        condition_code = self._evaluate_condition(node.test)
        body_code = self.ast_processor.process_node(node.body)
        else_code = self.ast_processor.process_node(node.orelse) if node.orelse else ""
        return f"{condition_code}\n{body_code}\n{else_code}"

    def _evaluate_condition(self, node: ast.AST) -> str:
        if isinstance(node, ast.BoolOp):
            return self._handle_bool_op(node)
        elif isinstance(node, ast.Compare):
            return self.func_expressions._handle_compare(node)
        else:
            raise ValueError(f"Unsupported node type {type(node).__name__}")

    def _handle_bool_op(self, node: ast.BoolOp) -> str:
        op_type = type(node.op)
        if op_type == ast.And:
            return self._handle_and(node)
        elif op_type == ast.Or:
            return self._handle_or(node)
        else:
            raise ValueError(f"Unsupported boolean operator {op_type.__name__}")

    def _handle_and(self, node: ast.BoolOp) -> str:
        code = ""
        for i, value in enumerate(node.values):
            code += self._evaluate_condition(value)
            if i < len(node.values) - 1:
                code += f"    beq {self.globals.get_label('end_and')}\n"
        code += f"{self.globals.get_label('end_and')}:\n"
        return code

    def _handle_or(self, node: ast.BoolOp) -> str:
        code = ""
        for i, value in enumerate(node.values):
            code += self._evaluate_condition(value)
            if i < len(node.values) - 1:
                code += f"    bne {self.globals.get_label('end_or')}\n"
        code += f"{self.globals.get_label('end_or')}:\n"
        return code
