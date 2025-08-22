# lib/c64.py
"""6502 code generator for the Commodore 64."""

from typing import Any, Set
from lib.core import CodeGenerator, DataType, OperationType
from lib.symbols import SymbolTable
from lib.labels import LabelManager
from lib.output import AssemblyOutput
from lib.errors import CompilerError
from lib.ast_nodes import Program, Literal, Identifier, BinaryOperation, FunctionCall, Assignment, IfStatement, WhileStatement, ForStatement, FunctionDefinition, ReturnStatement

class C64CodeGenerator(CodeGenerator):
    """Generates 6502 assembly code for the Commodore 64."""

    def __init__(self, symbol_table: SymbolTable, label_manager: LabelManager, output: AssemblyOutput):
        super().__init__(symbol_table, label_manager, output)
        self.temp_var_counter = 0
        self.used_routines: Set[str] = set()

    def visit_program(self, node: Program) -> Any:
        """Visits the main program node."""
        self.output.add_line("; py2c64 - Generated 6502 Assembly")
        self.output.add_line("; Target: Commodore 64")
        self.output.add_line("")

        # Process all statements
        for stmt in node.statements:
            stmt.accept(self)

        # Add used routines
        self._add_used_routines()
        return self.output.generate()

    def visit_literal(self, node: Literal) -> Any:
        """Visits a literal value node."""
        temp_var = self._get_temp_var()

        if node.data_type == DataType.INT16:
            self.output.add_instruction("LDA", f"#<{node.value}")
            self.output.add_instruction("STA", f"{temp_var}")
            self.output.add_instruction("LDA", f"#{node.value}>>8")
            self.output.add_instruction("STA", f"{temp_var}+1")
        elif node.data_type == DataType.FLOAT32:
            # For floats, conversion to Apple II format would be needed
            self.output.add_line(f"    ; Float literal: {node.value}")

        return temp_var

    def visit_identifier(self, node: Identifier) -> Any:
        """Visits an identifier node."""
        var = self.symbol_table.lookup_variable(node.name)
        if not var:
            raise CompilerError(f"Undefined variable: {node.name}")
        
        temp_var = self._get_temp_var()
        self.output.add_instruction("LDA", f"{var.name}")
        self.output.add_instruction("STA", f"{temp_var}")
        self.output.add_instruction("LDA", f"{var.name}+1")
        self.output.add_instruction("STA", f"{temp_var}+1")

        return temp_var

    def visit_binary_operation(self, node: BinaryOperation) -> Any:
        """Visits a binary operation node."""
        left_result = node.left.accept(self)
        right_result = node.right.accept(self)
        result_var = self._get_temp_var()

        if node.operation == OperationType.ADD:
            self._generate_add_int16(left_result, right_result, result_var)
        elif node.operation == OperationType.SUB:
            self._generate_sub_int16(left_result, right_result, result_var)
        elif node.operation == OperationType.MUL:
            self._generate_mul_int16(left_result, right_result, result_var)
            self.used_routines.add("multiply16x16")
        # ... other operators ...

        return result_var

    def visit_function_call(self, node: FunctionCall) -> Any:
        """Visits a function call node."""
        if node.name == "print":
            # Special handling for print
            if node.arguments:
                arg_result = node.arguments[0].accept(self)
                self.output.add_instruction("LDA", f"{arg_result}")
                self.output.add_instruction("STA", "PRINT_VALUE")
                self.output.add_instruction("LDA", f"{arg_result}+1")
                self.output.add_instruction("STA", "PRINT_VALUE+1")
                self.output.add_instruction("JSR", "PRINT_INT16")
                self.used_routines.add("print_int16")
        else:
            # Normal function call
            func = self.symbol_table.lookup_function(node.name)
            if not func:
                raise CompilerError(f"Undefined function: {node.name}")

            # Parameter handling and call
            for i, arg in enumerate(node.arguments):
                arg_result = arg.accept(self)
                self.output.add_instruction("LDA", f"{arg_result}")
                self.output.add_instruction("PHA")
                self.output.add_instruction("LDA", f"{arg_result}+1")
                self.output.add_instruction("PHA")

            self.output.add_instruction("JSR", f"FUNC_{node.name}")

    def visit_assignment(self, node: Assignment) -> Any:
        """Visits an assignment node."""
        value_result = node.value.accept(self)

        # Lookup or declare variable
        var = self.symbol_table.lookup_variable(node.target)
        if not var:
            # Infer type from expression (simplified)
            var = self.symbol_table.declare_variable(node.target, DataType.INT16)

        self.output.add_instruction("LDA", f"{value_result}")
        self.output.add_instruction("STA", f"{var.name}")
        self.output.add_instruction("LDA", f"{value_result}+1")
        self.output.add_instruction("STA", f"{var.name}+1")

    def visit_if_statement(self, node: IfStatement) -> Any:
        """Visits an if statement node."""
        condition_result = node.condition.accept(self)
        else_label = self.label_manager.generate_label("ELSE")
        end_label = self.label_manager.generate_label("END_IF")

        # Condition test (simplified: != 0)
        self.output.add_instruction("LDA", f"{condition_result}")
        self.output.add_instruction("ORA", f"{condition_result}+1")
        self.output.add_instruction("BEQ", else_label)

        # Then body
        for stmt in node.then_body:
            stmt.accept(self)

        self.output.add_instruction("JMP", end_label)

        # Else body
        self.output.add_label(else_label)
        for stmt in node.else_body:
            stmt.accept(self)

        self.output.add_label(end_label)

    def visit_while_statement(self, node: WhileStatement) -> Any:
        """Visits a while statement node."""
        loop_label = self.label_manager.generate_label("WHILE_LOOP")
        end_label = self.label_manager.generate_label("END_WHILE")

        self.output.add_label(loop_label)

        # Condition test
        condition_result = node.condition.accept(self)
        self.output.add_instruction("LDA", f"{condition_result}")
        self.output.add_instruction("ORA", f"{condition_result}+1")
        self.output.add_instruction("BEQ", end_label)

        # Body
        for stmt in node.body:
            stmt.accept(self)

        self.output.add_instruction("JMP", loop_label)
        self.output.add_label(end_label)

    def visit_for_statement(self, node: ForStatement) -> Any:
        """Visits a for statement node."""
        # Simplified implementation for: for i in range(start, end, step)
        loop_label = self.label_manager.generate_label("FOR_LOOP")
        end_label = self.label_manager.generate_label("END_FOR")

        # Initialization
        start_result = node.start.accept(self)
        var = self.symbol_table.declare_variable(node.var, DataType.INT16)

        self.output.add_instruction("LDA", f"{start_result}")
        self.output.add_instruction("STA", f"{var.name}")
        self.output.add_instruction("LDA", f"{start_result}+1")
        self.output.add_instruction("STA", f"{var.name}+1")

        # Loop
        self.output.add_label(loop_label)

        # Condition test (var < end)
        end_result = node.end.accept(self)
        self._generate_compare_int16(var.name, end_result, "LT")
        self.output.add_instruction("BEQ", end_label)

        # Body
        for stmt in node.body:
            stmt.accept(self)

        # Increment
        step_result = node.step.accept(self)
        self._generate_add_int16(var.name, step_result, var.name)
        self.output.add_instruction("JMP", loop_label)
        self.output.add_label(end_label)

    def visit_function_definition(self, node: FunctionDefinition) -> Any:
        """Visits a function definition node."""
        func = self.symbol_table.declare_function(node.name, node.parameters, node.return_type)
        func.entry_label = f"FUNC_{node.name}"

        self.symbol_table.enter_scope(node.name)

        # Declare parameters
        for param in node.parameters:
            self.symbol_table.declare_variable(param.name, param.data_type)

        # Code generation
        self.output.add_label(func.entry_label)
        