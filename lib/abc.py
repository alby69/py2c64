from abc import ABC, abstractmethod
from typing import Any

from .symbols import SymbolTable
from .labels import LabelManager
from .output import AssemblyOutput
from .ast_nodes import (
    Program, Literal, Identifier, BinaryOperation, UnaryOperation, FunctionCall,
    Assignment, IfStatement, WhileStatement, ForStatement,
    FunctionDefinition, ReturnStatement, ListLiteral, Subscript
)

class CodeGenerator(ABC):
    """Abstract base class for code generators using the Visitor pattern."""

    def __init__(self, symbol_table: SymbolTable, label_manager: LabelManager, output: AssemblyOutput):
        self.symbol_table = symbol_table
        self.label_manager = label_manager
        self.output = output

    @abstractmethod
    def visit_program(self, node: Program) -> Any:
        pass

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
        """Visits a list literal node."""
        pass

    @abstractmethod
    def visit_subscript(self, node: Subscript) -> Any:
        """Visits a subscript access node."""
        pass
