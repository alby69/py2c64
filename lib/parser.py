import ast
from typing import Optional, List

from .errors import CompilerError
from .ast_nodes import (
    Program, Statement, Expression, Assignment, IfStatement, WhileStatement,
    ForStatement, FunctionDefinition, ReturnStatement, Literal, Identifier,
    BinaryOperation, FunctionCall, ListLiteral, Subscript, UnaryOperation
)
from .symbols import SymbolTable, DataType, Variable, OperationType, UnaryOperationType

class PythonASTParser:
    """Parser that converts the Python AST to our internal AST."""

    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table

    def parse(self, python_code: str) -> Program:
        """Parses Python code and returns our AST."""
        python_ast = ast.parse(python_code)
        statements = []

        for node in python_ast.body:
            stmt = self._parse_statement(node)
            if stmt:
                statements.append(stmt)

        return Program(statements)

    def _parse_statement(self, node: ast.AST) -> Optional[Statement]:
        """Parses a Python statement."""
        if isinstance(node, ast.Assign):
            return self._parse_assignment(node)
        elif isinstance(node, ast.If):
            return self._parse_if_statement(node)
        elif isinstance(node, ast.While):
            return self._parse_while_statement(node)
        elif isinstance(node, ast.For):
            return self._parse_for_statement(node)
        elif isinstance(node, ast.FunctionDef):
            return self._parse_function_definition(node)
        elif isinstance(node, ast.Return):
            return self._parse_return_statement(node)
        elif isinstance(node, ast.Expr):
            # Expression statement (e.g., function call)
            if isinstance(node.value, ast.Call):
                return self._parse_expression(node.value)

        return None

    def _parse_assignment(self, node: ast.Assign) -> Assignment:
        """Parses an assignment."""
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            raise CompilerError("Only simple assignments are supported")

        target = node.targets[0].id
        value = self._parse_expression(node.value)
        return Assignment(target, value)

    def _parse_if_statement(self, node: ast.If) -> IfStatement:
        """Parses an if statement."""
        condition = self._parse_expression(node.test)
        then_body = [self._parse_statement(stmt) for stmt in node.body if self._parse_statement(stmt)]

        else_body = []
        if node.orelse:
            else_body = [self._parse_statement(stmt) for stmt in node.orelse if self._parse_statement(stmt)]

        return IfStatement(condition, then_body, else_body)

    def _parse_while_statement(self, node: ast.While) -> WhileStatement:
        """Parses a while loop."""
        condition = self._parse_expression(node.test)
        body = [self._parse_statement(stmt) for stmt in node.body if self._parse_statement(stmt)]
        return WhileStatement(condition, body)

    def _parse_for_statement(self, node: ast.For) -> ForStatement:
        """Parses a for loop (only supports range)."""
        if not isinstance(node.target, ast.Name):
            raise CompilerError("Only simple for loop variables are supported")

        var_name = node.target.id

        if not isinstance(node.iter, ast.Call) or not isinstance(node.iter.func, ast.Name) or node.iter.func.id != "range":
            raise CompilerError("Only range() iterations are supported")

        range_args = node.iter.args
        if len(range_args) == 1:
            start = Literal(0, DataType.INT16)
            end = self._parse_expression(range_args[0])
            step = Literal(1, DataType.INT16)
        elif len(range_args) == 2:
            start = self._parse_expression(range_args[0])
            end = self._parse_expression(range_args[1])
            step = Literal(1, DataType.INT16)
        elif len(range_args) == 3:
            start = self._parse_expression(range_args[0])
            end = self._parse_expression(range_args[1])
            step = self._parse_expression(range_args[2])
        else:
            raise CompilerError("Invalid range() arguments")

        body = [self._parse_statement(stmt) for stmt in node.body if self._parse_statement(stmt)]

        return ForStatement(var_name, start, end, step, body)

    def _parse_function_definition(self, node: ast.FunctionDef) -> FunctionDefinition:
        """Parses a function definition."""
        name = node.name

        parameters = []
        for arg in node.args.args:
            param = Variable(arg.arg, DataType.INT16, is_parameter=True)
            parameters.append(param)

        body = [self._parse_statement(stmt) for stmt in node.body if self._parse_statement(stmt)]

        return_type = DataType.VOID
        for stmt in body:
            if isinstance(stmt, ReturnStatement) and stmt.value:
                return_type = DataType.INT16
                break

        return FunctionDefinition(name, parameters, body, return_type)

    def _parse_return_statement(self, node: ast.Return) -> ReturnStatement:
        """Parses a return statement."""
        value = self._parse_expression(node.value) if node.value else None
        return ReturnStatement(value)

    def _parse_expression(self, node: ast.AST) -> Expression:
        """Parses an expression."""
        if isinstance(node, ast.Constant):
            return self._parse_constant(node)
        elif isinstance(node, ast.Name):
            return Identifier(node.id)
        elif isinstance(node, ast.BinOp):
            return self._parse_binary_operation(node)
        elif isinstance(node, ast.Call):
            return self._parse_function_call(node)
        elif isinstance(node, ast.Compare):
            return self._parse_comparison(node)
        elif isinstance(node, ast.List):
            return self._parse_list_literal(node)
        elif isinstance(node, ast.Subscript):
            return self._parse_subscript(node)
        elif isinstance(node, ast.UnaryOp):
            return self._parse_unary_operation(node)
        else:
            raise CompilerError(f"Unsupported expression type: {type(node)}")

    def _parse_unary_operation(self, node: ast.UnaryOp) -> UnaryOperation:
        """Parses a unary operation."""
        op_map = {
            ast.Not: UnaryOperationType.NOT,
            ast.USub: UnaryOperationType.NEG,
        }

        op_type = op_map.get(type(node.op))
        if not op_type:
            raise CompilerError(f"Unsupported unary operation: {type(node.op)}")

        operand = self._parse_expression(node.operand)
        return UnaryOperation(op_type, operand)

    def _parse_list_literal(self, node: ast.List) -> ListLiteral:
        """Parses a list literal."""
        elements = [self._parse_expression(e) for e in node.elts]
        return ListLiteral(elements)

    def _parse_subscript(self, node: ast.Subscript) -> Subscript:
        """Parses a subscript access."""
        if not isinstance(node.value, ast.Name):
            raise CompilerError("Subscript access is only supported for simple variables.")

        list_name = Identifier(node.value.id)
        index_expr = self._parse_expression(node.slice)

        return Subscript(list_name, index_expr)

    def _parse_constant(self, node: ast.Constant) -> Literal:
        """Parses a constant."""
        value = node.value
        if isinstance(value, int):
            return Literal(value, DataType.INT16)
        elif isinstance(value, float):
            return Literal(value, DataType.FLOAT32)
        elif isinstance(value, str):
            return Literal(value, DataType.STRING)
        else:
            raise CompilerError(f"Unsupported constant type: {type(value)}")

    def _parse_binary_operation(self, node: ast.BinOp) -> BinaryOperation:
        """Parses a binary operation."""
        left = self._parse_expression(node.left)
        right = self._parse_expression(node.right)

        op_map = {
            ast.Add: OperationType.ADD,
            ast.Sub: OperationType.SUB,
            ast.Mult: OperationType.MUL,
            ast.FloorDiv: OperationType.DIV,
            ast.Mod: OperationType.MOD,
        }

        op_type = op_map.get(type(node.op))
        if not op_type:
            raise CompilerError(f"Unsupported binary operation: {type(node.op)}")

        return BinaryOperation(left, op_type, right)

    def _parse_function_call(self, node: ast.Call) -> FunctionCall:
        """Parses a function call."""
        if not isinstance(node.func, ast.Name):
            raise CompilerError("Only simple function calls are supported")

        name = node.func.id
        arguments = [self._parse_expression(arg) for arg in node.args]

        return FunctionCall(name, arguments)

    def _parse_comparison(self, node: ast.Compare) -> BinaryOperation:
        """Parses a comparison (simplified for one operator)."""
        if len(node.ops) != 1 or len(node.comparators) != 1:
            raise CompilerError("Only simple comparisons are supported")

        left = self._parse_expression(node.left)
        right = self._parse_expression(node.comparators[0])

        op_map = {
            ast.Eq: OperationType.EQ,
            ast.NotEq: OperationType.NE,
            ast.Lt: OperationType.LT,
            ast.Gt: OperationType.GT,
            ast.LtE: OperationType.LE,
            ast.GtE: OperationType.GE,
        }

        op_type = op_map.get(type(node.ops[0]))
        if not op_type:
            raise CompilerError(f"Unsupported comparison: {type(node.ops[0])}")

        return BinaryOperation(left, op_type, right)
