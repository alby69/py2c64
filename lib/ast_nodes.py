# lib/ast_nodes.py
"""Defines the AST node classes for the py2c64 compiler."""

from abc import ABC, abstractmethod
from typing import List, Any, Optional
from dataclasses import dataclass
from .symbols import DataType, OperationType, Variable

class ASTNode(ABC):
    """Base class for all AST nodes"""

    @abstractmethod
    def accept(self, visitor: 'CodeGenerator') -> Any:
        """Accepts a visitor and calls the appropriate visit method."""
        pass

@dataclass
class Expression(ASTNode):
    """Base class for all expressions."""
    pass

@dataclass
class Statement(ASTNode):
    """Base class for all statements."""
    pass

@dataclass
class Literal(Expression):
    """Represents a literal value (e.g., 10, "hello")."""
    value: Any
    data_type: DataType

    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_literal(self)

@dataclass
class Identifier(Expression):
    """Represents an identifier (variable name)."""
    name: str

    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_identifier(self)

@dataclass
class BinaryOperation(Expression):
    """Represents a binary operation (e.g., +, -, *)."""
    left: Expression
    operation: OperationType
    right: Expression

    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_binary_operation(self)

@dataclass
class FunctionCall(Expression):
    """Represents a function call."""
    name: str
    arguments: List[Expression]

    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_function_call(self)

@dataclass
class Assignment(Statement):
    """Represents an assignment statement (e.g., x = 5)."""
    target: str  # Target is now a string (variable name)
    value: Expression

    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_assignment(self)

@dataclass
class IfStatement(Statement):
    """Represents an if statement."""
    condition: Expression
    then_body: List[Statement]
    else_body: Optional[List[Statement]] = None

    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_if_statement(self)

@dataclass
class WhileStatement(Statement):
    """Represents a while loop."""
    condition: Expression
    body: List[Statement]

    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_while_statement(self)

@dataclass
class ForStatement(Statement):
    """Represents a for loop."""
    var: str  # Loop variable name
    start: Expression
    end: Expression
    step: Expression
    body: List[Statement]

    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_for_statement(self)

@dataclass
class FunctionDefinition(Statement):
    """Represents a function definition."""
    name: str
    parameters: List['Variable']  # List of parameter variables
    body: List[Statement]
    return_type: DataType

    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_function_definition(self)

@dataclass
class ReturnStatement(Statement):
    """Represents a return statement."""
    value: Optional[Expression] = None

    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_return_statement(self)

@dataclass
class Program(ASTNode):
    """Represents the root of the AST, the entire program."""
    statements: List[Statement]

    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_program(self)