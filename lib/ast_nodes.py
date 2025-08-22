# lib/ast_nodes.py
"""Defines the AST node classes for the py2c64 compiler."""

from abc import ABC, abstractmethod
from typing import List, Any, Optional
from dataclasses import dataclass
from .symbols import DataType, OperationType, UnaryOperationType, BoolOpType, Variable

class ASTNode(ABC):
    """Base class for all AST nodes"""
    @abstractmethod
    def accept(self, visitor: 'CodeGenerator') -> Any:
        pass

@dataclass
class Expression(ASTNode):
    pass

@dataclass
class Statement(ASTNode):
    pass

@dataclass
class Literal(Expression):
    value: Any
    data_type: DataType
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_literal(self)

@dataclass
class Identifier(Expression):
    name: str
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_identifier(self)

@dataclass
class BinaryOperation(Expression):
    left: Expression
    operation: OperationType
    right: Expression
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_binary_operation(self)

@dataclass
class UnaryOperation(Expression):
    operation: UnaryOperationType
    operand: Expression
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_unary_operation(self)

@dataclass
class BoolOperation(Expression):
    op: BoolOpType
    values: List[Expression]
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_bool_operation(self)

@dataclass
class FunctionCall(Expression):
    name: str
    arguments: List[Expression]
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_function_call(self)

@dataclass
class ListLiteral(Expression):
    elements: List[Expression]
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_list_literal(self)

@dataclass
class Slice:
    lower: Optional[Expression]
    upper: Optional[Expression]
    step: Optional[Expression]

@dataclass
class Subscript(Expression):
    name: Identifier
    index: Optional[Expression]
    slice: Optional[Slice] = None
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_subscript(self)

@dataclass
class Assignment(Statement):
    target: Any # Can be str (Identifier) or Subscript
    value: Expression
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_assignment(self)

@dataclass
class IfStatement(Statement):
    condition: Expression
    then_body: List[Statement]
    else_body: Optional[List[Statement]] = None
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_if_statement(self)

@dataclass
class WhileStatement(Statement):
    condition: Expression
    body: List[Statement]
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_while_statement(self)

@dataclass
class ForStatement(Statement):
    var: str
    start: Optional[Expression]
    end: Optional[Expression]
    step: Optional[Expression]
    body: List[Statement]
    iterable: Optional[Expression] = None
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_for_statement(self)

@dataclass
class FunctionDefinition(Statement):
    name: str
    parameters: List[Variable]
    body: List[Statement]
    return_type: DataType
    is_interrupt_handler: bool = False
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_function_definition(self)

@dataclass
class ReturnStatement(Statement):
    value: Optional[Expression] = None
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_return_statement(self)

@dataclass
class Break(Statement):
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_break(self)

@dataclass
class Continue(Statement):
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_continue(self)

@dataclass
class Program(ASTNode):
    statements: List[Statement]
    def accept(self, visitor: 'CodeGenerator') -> Any:
        # In the new design, the compiler core calls visit_functions and visit_main
        visitor.visit_functions(self)
        visitor.setup_interrupts(self)
        visitor.visit_main(self)
