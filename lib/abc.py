# lib/abc.py
"""Abstract Base Classes for the compiler."""

from abc import ABC, abstractmethod
from typing import Any

# Import all AST node types to allow for type hinting in visitor methods
from .ast_nodes import (
    Program, Literal, Identifier, BinaryOperation, UnaryOperation, BoolOperation,
    FunctionCall, Assignment, IfStatement, WhileStatement, ForStatement,
    FunctionDefinition, ReturnStatement, ListLiteral, Subscript
)

class CodeGenerator(ABC):
    """Abstract base class for code generators using the Visitor pattern."""

    def visit_program(self, node: Program) -> Any:
        """Called for the root of the AST."""
        for stmt in node.statements:
            stmt.accept(self)

    @abstractmethod
    def visit_literal(self, node: Literal) -> Any:
        pass

    @abstractmethod
    def visit_identifier(self, node: Identifier) -> Any:
        pass

    @abstractmethod
    def visit_binary_operation(self, node: BinaryOperation) -> Any:
        pass

    @abstractmethod
    def visit_unary_operation(self, node: UnaryOperation) -> Any:
        pass

    @abstractmethod
    def visit_bool_operation(self, node: BoolOperation) -> Any:
        pass

    @abstractmethod
    def visit_function_call(self, node: FunctionCall) -> Any:
        pass

    @abstractmethod
    def visit_assignment(self, node: Assignment) -> Any:
        pass

    @abstractmethod
    def visit_if_statement(self, node: IfStatement) -> Any:
        pass

    @abstractmethod
    def visit_while_statement(self, node: WhileStatement) -> Any:
        pass

    @abstractmethod
    def visit_for_statement(self, node: ForStatement) -> Any:
        pass

    @abstractmethod
    def visit_function_definition(self, node: FunctionDefinition) -> Any:
        pass

    @abstractmethod
    def visit_return_statement(self, node: ReturnStatement) -> Any:
        pass

    @abstractmethod
    def visit_list_literal(self, node: ListLiteral) -> Any:
        pass

    @abstractmethod
    def visit_subscript(self, node: Subscript) -> Any:
        pass

    @abstractmethod
    def visit_break(self, node: 'Break') -> Any:
        pass

    @abstractmethod
    def visit_continue(self, node: 'Continue') -> Any:
        pass
