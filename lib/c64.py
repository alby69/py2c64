# lib/c64.py
"""6502 code generator for the Commodore 64."""

from typing import Any, Set

from .abc import CodeGenerator
from .symbols import SymbolTable, DataType, OperationType, UnaryOperationType, BoolOpType
from .labels import LabelManager
from .output import AssemblyOutput
from .errors import CompilerError
from .ast_nodes import (
    Program, Literal, Identifier, BinaryOperation, UnaryOperation, BoolOperation,
    FunctionCall, Assignment, IfStatement, WhileStatement, ForStatement,
    FunctionDefinition, ReturnStatement, ListLiteral, Subscript
)

class C64CodeGenerator(CodeGenerator):
    """Generates 6502 assembly code for the Commodore 64."""

    def __init__(self, symbol_table: SymbolTable, label_manager: LabelManager, output: AssemblyOutput):
        super().__init__(symbol_table, label_manager, output)
        self.temp_var_counter = 0
        self.used_routines: Set[str] = set()
        self.list_support_initialized = False

    def visit_program(self, node: Program) -> Any:
        """Visits the main program node."""
        self.output.add_line("; py2c64 - Generated 6502 Assembly")
        self.output.add_line("; Target: Commodore 64")
        self.output.add_line("")

        for stmt in node.statements:
            stmt.accept(self)

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
        elif node.operation == OperationType.XOR:
            self._generate_xor_int16(left_result, right_result, result_var)

        return result_var

    def visit_unary_operation(self, node: UnaryOperation) -> Any:
        """Visits a unary operation node."""
        operand_result = node.operand.accept(self)
        result_var = self._get_temp_var()

        if node.operation == UnaryOperationType.NEG:
            # 0 - operand
            zero_var = self._get_temp_var()
            self.output.add_instruction("LDA", "#<0")
            self.output.add_instruction("STA", f"{zero_var}")
            self.output.add_instruction("LDA", "#0>>8")
            self.output.add_instruction("STA", f"{zero_var}+1")
            self._generate_sub_int16(zero_var, operand_result, result_var)
        elif node.operation == UnaryOperationType.NOT:
            # if operand is 0, result is 1, else result is 0
            is_not_zero_label = self.label_manager.generate_label("IS_NOT_ZERO")
            end_not_label = self.label_manager.generate_label("END_NOT")

            # Check if operand is zero. If not, branch.
            self.output.add_instruction("LDA", f"{operand_result}")
            self.output.add_instruction("ORA", f"{operand_result}+1")
            self.output.add_instruction("BNE", is_not_zero_label)

            # Code for when operand IS zero (is not not-zero)
            # Set result to 1
            self.output.add_instruction("LDA", "#<1")
            self.output.add_instruction("STA", f"{result_var}")
            self.output.add_instruction("LDA", "#1>>8")
            self.output.add_instruction("STA", f"{result_var}+1")
            self.output.add_instruction("JMP", end_not_label)

            # Code for when operand is NOT zero
            self.output.add_label(is_not_zero_label)
            # Set result to 0
            self.output.add_instruction("LDA", "#<0")
            self.output.add_instruction("STA", f"{result_var}")
            self.output.add_instruction("LDA", "#0>>8")
            self.output.add_instruction("STA", f"{result_var}+1")

            self.output.add_label(end_not_label)

        return result_var

    def visit_bool_operation(self, node: BoolOperation) -> Any:
        """Visits a boolean operation node with short-circuiting."""
        result_var = self._get_temp_var()
        end_label = self.label_manager.generate_label("BOOL_END")

        if node.op == BoolOpType.AND:
            # For AND, short-circuit if any value is false (0)
            set_false_label = self.label_manager.generate_label("BOOL_SET_FALSE")
            for value_node in node.values:
                value_result = value_node.accept(self)
                self.output.add_instruction("LDA", f"{value_result}")
                self.output.add_instruction("ORA", f"{value_result}+1")
                self.output.add_instruction("BEQ", set_false_label)

            # All were true, so result is true (1)
            self.output.add_instruction("LDA", "#<1")
            self.output.add_instruction("STA", f"{result_var}")
            self.output.add_instruction("LDA", "#1>>8")
            self.output.add_instruction("STA", f"{result_var}+1")
            self.output.add_instruction("JMP", end_label)

            # Set result to false (0)
            self.output.add_label(set_false_label)
            self.output.add_instruction("LDA", "#<0")
            self.output.add_instruction("STA", f"{result_var}")
            self.output.add_instruction("LDA", "#0>>8")
            self.output.add_instruction("STA", f"{result_var}+1")

        elif node.op == BoolOpType.OR:
            # For OR, short-circuit if any value is true (non-zero)
            set_true_label = self.label_manager.generate_label("BOOL_SET_TRUE")
            for value_node in node.values:
                value_result = value_node.accept(self)
                self.output.add_instruction("LDA", f"{value_result}")
                self.output.add_instruction("ORA", f"{value_result}+1")
                self.output.add_instruction("BNE", set_true_label)

            # All were false, so result is false (0)
            self.output.add_instruction("LDA", "#<0")
            self.output.add_instruction("STA", f"{result_var}")
            self.output.add_instruction("LDA", "#0>>8")
            self.output.add_instruction("STA", f"{result_var}+1")
            self.output.add_instruction("JMP", end_label)

            # Set result to true (1)
            self.output.add_label(set_true_label)
            self.output.add_instruction("LDA", "#<1")
            self.output.add_instruction("STA", f"{result_var}")
            self.output.add_instruction("LDA", "#1>>8")
            self.output.add_instruction("STA", f"{result_var}+1")

        self.output.add_label(end_label)
        return result_var

    def visit_function_call(self, node: FunctionCall) -> Any:
        """Visits a function call node."""
        if node.name == "print":
            if node.arguments:
                arg_result = node.arguments[0].accept(self)
                self.output.add_instruction("LDA", f"{arg_result}")
                self.output.add_instruction("STA", "PRINT_VALUE")
                self.output.add_instruction("LDA", f"{arg_result}+1")
                self.output.add_instruction("STA", "PRINT_VALUE+1")
                self.output.add_instruction("JSR", "PRINT_INT16")
                self.used_routines.add("print_int16")
            return

        func = self.symbol_table.lookup_function(node.name)
        if not func:
            raise CompilerError(f"Undefined function: {node.name}")

        # If it's a built-in, mark its routine as used
        if not func.entry_label.startswith("FUNC_"):
            self.used_routines.add(func.entry_label)

        for arg in reversed(node.arguments):
            arg_result = arg.accept(self)
            self.output.add_instruction("LDA", f"{arg_result}+1")
            self.output.add_instruction("PHA")
            self.output.add_instruction("LDA", f"{arg_result}")
            self.output.add_instruction("PHA")

        self.output.add_instruction("JSR", func.entry_label)

    def visit_assignment(self, node: Assignment) -> Any:
        """Visits an assignment node."""
        value_result = node.value.accept(self)

        var = self.symbol_table.lookup_variable(node.target)
        if not var:
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

        self.output.add_instruction("LDA", f"{condition_result}")
        self.output.add_instruction("ORA", f"{condition_result}+1")
        self.output.add_instruction("BEQ", else_label if node.else_body else end_label)

        for stmt in node.then_body:
            stmt.accept(self)

        if node.else_body:
            self.output.add_instruction("JMP", end_label)
            self.output.add_label(else_label)
            for stmt in node.else_body:
                stmt.accept(self)

        self.output.add_label(end_label)

    def visit_while_statement(self, node: WhileStatement) -> Any:
        """Visits a while statement node."""
        loop_label = self.label_manager.generate_label("WHILE_LOOP")
        end_label = self.label_manager.generate_label("END_WHILE")

        self.output.add_label(loop_label)
        condition_result = node.condition.accept(self)
        self.output.add_instruction("LDA", f"{condition_result}")
        self.output.add_instruction("ORA", f"{condition_result}+1")
        self.output.add_instruction("BEQ", end_label)

        for stmt in node.body:
            stmt.accept(self)

        self.output.add_instruction("JMP", loop_label)
        self.output.add_label(end_label)

    def visit_for_statement(self, node: ForStatement) -> Any:
        """Visits a for statement node."""
        loop_label = self.label_manager.generate_label("FOR_LOOP")
        end_label = self.label_manager.generate_label("END_FOR")

        start_result = node.start.accept(self)
        var = self.symbol_table.declare_variable(node.var, DataType.INT16)

        self.output.add_instruction("LDA", f"{start_result}")
        self.output.add_instruction("STA", f"{var.name}")
        self.output.add_instruction("LDA", f"{start_result}+1")
        self.output.add_instruction("STA", f"{var.name}+1")

        self.output.add_label(loop_label)
        end_result = node.end.accept(self)
        self._generate_compare_int16(var.name, end_result, "LT")
        self.output.add_instruction("BNE", end_label)

        for stmt in node.body:
            stmt.accept(self)

        step_result = node.step.accept(self)
        self._generate_add_int16(var.name, step_result, var.name)
        self.output.add_instruction("JMP", loop_label)
        self.output.add_label(end_label)

    def visit_function_definition(self, node: FunctionDefinition) -> Any:
        """Visits a function definition node."""
        func = self.symbol_table.declare_function(node.name, node.parameters, node.return_type)
        func.entry_label = f"FUNC_{node.name}"
        self.output.add_label(func.entry_label)

        self.symbol_table.enter_scope(node.name)
        for param in node.parameters:
            self.symbol_table.declare_variable(param.name, param.data_type)

        for stmt in node.body:
            stmt.accept(self)

        self.output.add_instruction("RTS")
        self.symbol_table.exit_scope()

    def visit_return_statement(self, node: ReturnStatement) -> Any:
        """Visits a return statement node."""
        if node.value:
            result = node.value.accept(self)
            self.output.add_instruction("LDA", f"{result}")
            self.output.add_instruction("STA", "RETURN_VALUE")
            self.output.add_instruction("LDA", f"{result}+1")
            self.output.add_instruction("STA", "RETURN_VALUE+1")

        self.output.add_instruction("RTS")

    def visit_list_literal(self, node: ListLiteral) -> Any:
        """Visits a list literal node and generates code to create it in memory."""
        if not self.list_support_initialized:
            self.list_support_initialized = True

        list_ptr_var = self._get_temp_var()
        list_size = 1 + len(node.elements) * 2  # 1 byte for length, 2 for each element

        # 1. The result of this expression is the pointer to the new list.
        #    Copy the current heap pointer to our result variable.
        self.output.add_instruction("LDA", "HEAP_POINTER")
        self.output.add_instruction("STA", f"{list_ptr_var}")
        self.output.add_instruction("LDA", "HEAP_POINTER+1")
        self.output.add_instruction("STA", f"{list_ptr_var}+1")

        # 2. Store the length of the list at the first byte of the list structure.
        self.output.add_instruction("LDY", "#0")
        self.output.add_instruction("LDA", f"#{len(node.elements)}")
        self.output.add_instruction("STA", f"({list_ptr_var}),Y")

        # 3. Store each element in the list.
        current_offset = 1
        for element_expr in node.elements:
            element_var = element_expr.accept(self)

            # Load value of element into A
            self.output.add_instruction("LDA", f"{element_var}")
            self.output.add_instruction("LDY", f"#{current_offset}")
            self.output.add_instruction("STA", f"({list_ptr_var}),Y")

            # Load high byte of element into A
            self.output.add_instruction("LDA", f"{element_var}+1")
            self.output.add_instruction("INY")
            self.output.add_instruction("STA", f"({list_ptr_var}),Y")

            current_offset += 2

        # 4. Update the heap pointer by adding the size of the list.
        size_var = self._get_temp_var()
        self.output.add_instruction("LDA", f"#<{list_size}")
        self.output.add_instruction("STA", f"{size_var}")
        self.output.add_instruction("LDA", f"#{list_size}>>8")
        self.output.add_instruction("STA", f"{size_var}+1")

        self._generate_add_int16("HEAP_POINTER", size_var, "HEAP_POINTER")

        return list_ptr_var

    def visit_subscript(self, node: Subscript) -> Any:
        """Visits a subscript access node."""
        # 1. Get the pointer to the list and the index value.
        list_ptr_var = node.name.accept(self)
        index_var = node.index.accept(self)

        # 2. Pass arguments to the routine.
        self.output.add_instruction("LDA", f"{list_ptr_var}")
        self.output.add_instruction("STA", "LIST_ROUTINE_ARG1")
        self.output.add_instruction("LDA", f"{list_ptr_var}+1")
        self.output.add_instruction("STA", "LIST_ROUTINE_ARG1+1")

        self.output.add_instruction("LDA", f"{index_var}")
        self.output.add_instruction("STA", "LIST_ROUTINE_ARG2")
        self.output.add_instruction("LDA", f"{index_var}+1")
        self.output.add_instruction("STA", "LIST_ROUTINE_ARG2+1")

        # 3. Call the routine.
        self.output.add_instruction("JSR", "GET_LIST_ELEMENT")
        self.used_routines.add("get_list_element")

        # 4. The result is in LIST_ROUTINE_RET1. Copy it to a temp var.
        result_var = self._get_temp_var()
        self.output.add_instruction("LDA", "LIST_ROUTINE_RET1")
        self.output.add_instruction("STA", f"{result_var}")
        self.output.add_instruction("LDA", "LIST_ROUTINE_RET1+1")
        self.output.add_instruction("STA", f"{result_var}+1")

        return result_var

    def _get_temp_var(self) -> str:
        """Generates a temporary variable name."""
        temp_name = f"TEMP_{self.temp_var_counter}"
        self.temp_var_counter += 1
        return temp_name

    def _generate_add_int16(self, left: str, right: str, result: str):
        """Generates code for 16-bit addition."""
        self.output.add_instruction("CLC")
        self.output.add_instruction("LDA", f"{left}")
        self.output.add_instruction("ADC", f"{right}")
        self.output.add_instruction("STA", f"{result}")
        self.output.add_instruction("LDA", f"{left}+1")
        self.output.add_instruction("ADC", f"{right}+1")
        self.output.add_instruction("STA", f"{result}+1")

    def _generate_sub_int16(self, left: str, right: str, result: str):
        """Generates code for 16-bit subtraction."""
        self.output.add_instruction("SEC")
        self.output.add_instruction("LDA", f"{left}")
        self.output.add_instruction("SBC", f"{right}")
        self.output.add_instruction("STA", f"{result}")
        self.output.add_instruction("LDA", f"{left}+1")
        self.output.add_instruction("SBC", f"{right}+1")
        self.output.add_instruction("STA", f"{result}+1")

    def _generate_mul_int16(self, left: str, right: str, result: str):
        """Generates code for 16-bit multiplication."""
        self.output.add_instruction("LDA", f"{left}")
        self.output.add_instruction("STA", "MULT_ARG1")
        self.output.add_instruction("LDA", f"{left}+1")
        self.output.add_instruction("STA", "MULT_ARG1+1")
        self.output.add_instruction("LDA", f"{right}")
        self.output.add_instruction("STA", "MULT_ARG2")
        self.output.add_instruction("LDA", f"{right}+1")
        self.output.add_instruction("STA", "MULT_ARG2+1")
        self.output.add_instruction("JSR", "multiply16x16")
        self.output.add_instruction("LDA", "MULT_RESULT")
        self.output.add_instruction("STA", f"{result}")
        self.output.add_instruction("LDA", "MULT_RESULT+1")
        self.output.add_instruction("STA", f"{result}+1")

    def _generate_compare_int16(self, left: str, right: str, op: str):
        """Generates code for 16-bit comparison."""
        self.output.add_instruction("LDA", f"{left}+1")
        self.output.add_instruction("CMP", f"{right}+1")
        self.output.add_instruction("BNE", "SKIP_LO_CMP")
        self.output.add_instruction("LDA", f"{left}")
        self.output.add_instruction("CMP", f"{right}")
        self.output.add_label("SKIP_LO_CMP")

    def _generate_xor_int16(self, left: str, right: str, result: str):
        """Generates code for 16-bit bitwise XOR."""
        self.output.add_instruction("LDA", f"{left}")
        self.output.add_instruction("EOR", f"{right}")
        self.output.add_instruction("STA", f"{result}")
        self.output.add_instruction("LDA", f"{left}+1")
        self.output.add_instruction("EOR", f"{right}+1")
        self.output.add_instruction("STA", f"{result}+1")
        