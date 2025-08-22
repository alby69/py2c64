# lib/parser.py
"""Parses Python code into a custom AST."""

import ast
from .ast_nodes import (
    Program, Statement, Expression, Literal, Identifier, BinaryOperation, UnaryOperation,
    BoolOperation, FunctionCall, Assignment, IfStatement, WhileStatement, ForStatement,
    FunctionDefinition, ReturnStatement, ListLiteral, Subscript, Slice
)
from .symbols import SymbolTable, DataType, OperationType, UnaryOperationType, BoolOpType
from .errors import CompilerError

class PythonASTParser(ast.NodeVisitor):
    """
    Parses Python's native AST into a simplified, custom AST for our compiler.
    """
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table

    def parse(self, code: str) -> Program:
        """Parses the Python code and returns the root of the custom AST."""
        try:
            python_ast = ast.parse(code)
            return self.visit(python_ast)
        except SyntaxError as e:
            raise CompilerError(f"Python syntax error: {e}")

    def visit_Module(self, node: ast.Module) -> Program:
        body = [self.visit(stmt) for stmt in node.body]
        # Filter out None values that may be returned by visitors (e.g. for 'pass')
        body = [stmt for stmt in body if stmt is not None]
        return Program(statements=body)

    def visit_Expr(self, node: ast.Expr) -> Statement:
        return self.visit(node.value)

    def visit_Assign(self, node: ast.Assign) -> Assignment:
        if len(node.targets) != 1:
            raise CompilerError("Only single target assignment is supported.")

        target_node = node.targets[0]
        if isinstance(target_node, ast.Name):
            target = target_node.id
        elif isinstance(target_node, ast.Subscript):
            target = self.visit_Subscript(target_node)
        else:
            raise CompilerError(f"Unsupported assignment target type: {type(target_node)}")

        value = self.visit(node.value)
        return Assignment(target=target, value=value)

    def visit_Constant(self, node: ast.Constant) -> Literal:
        value = node.value
        if isinstance(value, bool):
            return Literal(int(value), DataType.INT16)
        elif isinstance(value, int):
            return Literal(value, DataType.INT16)
        elif isinstance(value, float):
            return Literal(value, DataType.FLOAT32)
        elif isinstance(value, str):
            return Literal(value, DataType.STRING)
        elif value is None:
            return Literal(0, DataType.VOID)
        else:
            raise CompilerError(f"Unsupported constant type: {type(value)}")

    def visit_Name(self, node: ast.Name) -> Identifier:
        return Identifier(name=node.id)

    def visit_BinOp(self, node: ast.BinOp) -> BinaryOperation:
        op_map = {
            ast.Add: OperationType.ADD, ast.Sub: OperationType.SUB,
            ast.Mult: OperationType.MUL, ast.Div: OperationType.DIV,
            ast.FloorDiv: OperationType.DIV, # Treat floor division as normal division
            ast.BitXor: OperationType.XOR,
        }
        op_type = op_map.get(type(node.op))
        if not op_type:
            raise CompilerError(f"Unsupported binary operator: {type(node.op)}")
        left = self.visit(node.left)
        right = self.visit(node.right)
        return BinaryOperation(left=left, operation=op_type, right=right)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> UnaryOperation:
        op_map = {ast.USub: UnaryOperationType.NEG, ast.Not: UnaryOperationType.NOT}
        op_type = op_map.get(type(node.op))
        if not op_type:
            raise CompilerError(f"Unsupported unary operator: {type(node.op)}")
        operand = self.visit(node.operand)
        return UnaryOperation(operation=op_type, operand=operand)

    def visit_BoolOp(self, node: ast.BoolOp) -> BoolOperation:
        op_map = {ast.And: BoolOpType.AND, ast.Or: BoolOpType.OR}
        op_type = op_map.get(type(node.op))
        values = [self.visit(v) for v in node.values]
        return BoolOperation(op=op_type, values=values)

    def visit_Call(self, node: ast.Call) -> FunctionCall:
        if not isinstance(node.func, ast.Name):
            raise CompilerError("Dynamic function calls are not supported.")
        func_name = node.func.id
        args = [self.visit(arg) for arg in node.args]
        return FunctionCall(name=func_name, arguments=args)

    def visit_Compare(self, node: ast.Compare) -> BinaryOperation:
        # Simplified to handle one comparison, e.g., a > b
        if len(node.ops) != 1:
            raise CompilerError("Chained comparisons are not supported.")

        op_map = {
            ast.Eq: OperationType.EQ, ast.NotEq: OperationType.NE,
            ast.Lt: OperationType.LT, ast.LtE: OperationType.LE,
            ast.Gt: OperationType.GT, ast.GtE: OperationType.GE,
        }
        op_type = op_map.get(type(node.ops[0]))
        if not op_type:
            raise CompilerError(f"Unsupported comparison operator: {type(node.ops[0])}")

        left = self.visit(node.left)
        right = self.visit(node.comparators[0])
        return BinaryOperation(left=left, operation=op_type, right=right)

    def visit_If(self, node: ast.If) -> IfStatement:
        condition = self.visit(node.test)
        then_body = [self.visit(stmt) for stmt in node.body]
        else_body = [self.visit(stmt) for stmt in node.orelse] if node.orelse else None
        return IfStatement(condition=condition, then_body=then_body, else_body=else_body)

    def visit_While(self, node: ast.While) -> WhileStatement:
        condition = self.visit(node.test)
        body = [self.visit(stmt) for stmt in node.body]
        return WhileStatement(condition=condition, body=body)

    def visit_For(self, node: ast.For) -> ForStatement:
        if not isinstance(node.target, ast.Name):
            raise CompilerError("For loops must use a simple variable (e.g., `for i in ...`)")
        var_name = node.target.id
        iterable = self.visit(node.iter)
        body = [self.visit(stmt) for stmt in node.body]
        # Defer range() parsing to the semantic analysis/code generation phase
        return ForStatement(var=var_name, start=None, end=None, step=None, body=body, iterable=iterable)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> FunctionDefinition:
        is_interrupt = any(isinstance(d, ast.Name) and d.id == 'interrupt' for d in node.decorator_list)

        # Simplified parameter and return type handling
        params = node.args.args
        return_type = DataType.VOID # Assume void if not specified
        if node.returns:
            # A real implementation would parse the return annotation
            if isinstance(node.returns, ast.Name) and node.returns.id == 'int':
                return_type = DataType.INT16

        func = self.symbol_table.declare_function(node.name, params, return_type, is_interrupt)

        body = [self.visit(stmt) for stmt in node.body]

        return FunctionDefinition(
            name=node.name, parameters=func.parameters, body=body,
            return_type=func.return_type, is_interrupt_handler=is_interrupt
        )

    def visit_Return(self, node: ast.Return) -> ReturnStatement:
        value = self.visit(node.value) if node.value else None
        return ReturnStatement(value=value)

    def visit_List(self, node: ast.List) -> ListLiteral:
        elements = [self.visit(e) for e in node.elts]
        return ListLiteral(elements=elements)

    def visit_Subscript(self, node: ast.Subscript) -> Subscript:
        name = self.visit(node.value)
        if isinstance(node.slice, ast.Slice):
            lower = self.visit(node.slice.lower) if node.slice.lower else None
            upper = self.visit(node.slice.upper) if node.slice.upper else None
            step = self.visit(node.slice.step) if node.slice.step else None
            return Subscript(name=name, index=None, slice=Slice(lower, upper, step))
        else:
            index = self.visit(node.slice)
            return Subscript(name=name, index=index)

    def visit_Pass(self, node: ast.Pass) -> None:
        """A 'pass' statement does nothing."""
        return None

    def visit_Break(self, node: ast.Break) -> Statement:
        from .ast_nodes import Break
        return Break()

    def visit_Continue(self, node: ast.Continue) -> Statement:
        from .ast_nodes import Continue
        return Continue()

    def generic_visit(self, node):
        raise CompilerError(f"Unsupported Python feature: {type(node).__name__}")
