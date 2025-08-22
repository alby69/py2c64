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
        self.symbol_table = symbol_table
        self.label_manager = label_manager
        self.output = output
        self.temp_var_counter = 0
        self.used_routines: Set[str] = set()
        self.list_support_initialized = False
        self.loop_stack: list[tuple[str, str]] = []

    def visit_break(self, node) -> Any:
        if not self.loop_stack:
            raise CompilerError("'break' outside loop")
        _, end_label = self.loop_stack[-1]
        self.output.add_instruction("JMP", end_label)

    def visit_continue(self, node) -> Any:
        if not self.loop_stack:
            raise CompilerError("'continue' outside loop")
        start_label, _ = self.loop_stack[-1]
        self.output.add_instruction("JMP", start_label)

    def visit_functions(self, program_node: Program):
        for stmt in program_node.statements:
            if isinstance(stmt, FunctionDefinition):
                stmt.accept(self)

    def visit_main(self, program_node: Program):
        for stmt in program_node.statements:
            if not isinstance(stmt, FunctionDefinition):
                stmt.accept(self)

    def setup_interrupts(self, program_node: Program):
        for stmt in program_node.statements:
            if isinstance(stmt, FunctionDefinition) and stmt.is_interrupt_handler:
                func_label = f"FUNC_{stmt.name}"
                self.output.add_instruction("LDA", f"#<{func_label}")
                self.output.add_instruction("STA", "IRQ_USER_ROUTINE")
                self.output.add_instruction("LDA", f"#{func_label}>>8")
                self.output.add_instruction("STA", "IRQ_USER_ROUTINE+1")
                self.output.add_instruction("JSR", "setup_raster_irq")
                self.used_routines.add("setup_raster_irq")

    def visit_literal(self, node: Literal) -> Any:
        temp_var = self._get_temp_var()
        if node.data_type == DataType.INT16:
            self.output.add_instruction("LDA", f"#<{node.value}")
            self.output.add_instruction("STA", f"{temp_var}")
            self.output.add_instruction("LDA", f"#{node.value}>>8")
            self.output.add_instruction("STA", f"{temp_var}+1")
        elif node.data_type == DataType.STRING:
            string_label = self.label_manager.generate_label("STRING_LITERAL")
            self.output.switch_to_data_section()
            self.output.add_line(f'{string_label}: .asciiz "{node.value}"')
            self.output.switch_to_code_section()
            self.output.add_instruction("LDA", f"#<{string_label}")
            self.output.add_instruction("STA", f"{temp_var}")
            self.output.add_instruction("LDA", f"#{string_label}>>8")
            self.output.add_instruction("STA", f"{temp_var}+1")
        return temp_var, node.data_type

    def visit_identifier(self, node: Identifier) -> Any:
        var = self.symbol_table.lookup_variable(node.name)
        if not var:
            raise CompilerError(f"Undefined variable: {node.name}")
        temp_var = self._get_temp_var()
        self.output.add_instruction("LDA", f"{var.name}")
        self.output.add_instruction("STA", f"{temp_var}")
        self.output.add_instruction("LDA", f"{var.name}+1")
        self.output.add_instruction("STA", f"{temp_var}+1")
        return temp_var, var.data_type

    def visit_binary_operation(self, node: BinaryOperation) -> Any:
        left_result, left_type = node.left.accept(self)
        right_result, right_type = node.right.accept(self)
        result_var = self._get_temp_var()
        result_type = left_type
        if node.operation == OperationType.ADD:
            self._generate_add_int16(left_result, right_result, result_var)
        elif node.operation == OperationType.SUB:
            self._generate_sub_int16(left_result, right_result, result_var)
        elif node.operation == OperationType.MUL:
            self._generate_mul_int16(left_result, right_result, result_var)
        elif node.operation == OperationType.XOR:
            self._generate_xor_int16(left_result, right_result, result_var)
        return result_var, result_type

    def visit_unary_operation(self, node: UnaryOperation) -> Any:
        operand_result, operand_type = node.operand.accept(self)
        result_var = self._get_temp_var()
        if node.operation == UnaryOperationType.NEG:
            zero_var = self._get_temp_var_with_value(0)
            self._generate_sub_int16(zero_var, operand_result, result_var)
        elif node.operation == UnaryOperationType.NOT:
            self._generate_not_op(operand_result, result_var)
        return result_var, operand_type

    def visit_bool_operation(self, node: BoolOperation) -> Any:
        result_var = self._get_temp_var()
        end_label = self.label_manager.generate_label("BOOL_END")
        if node.op == BoolOpType.AND:
            set_false_label = self.label_manager.generate_label("BOOL_SET_FALSE")
            for value_node in node.values:
                value_result, _ = value_node.accept(self)
                self.output.add_instruction("LDA", f"{value_result}")
                self.output.add_instruction("ORA", f"{value_result}+1")
                self.output.add_instruction("BEQ", set_false_label)
            self._get_temp_var_with_value(1, result_var)
            self.output.add_instruction("JMP", end_label)
            self.output.add_label(set_false_label)
            self._get_temp_var_with_value(0, result_var)
        elif node.op == BoolOpType.OR:
            set_true_label = self.label_manager.generate_label("BOOL_SET_TRUE")
            for value_node in node.values:
                value_result, _ = value_node.accept(self)
                self.output.add_instruction("LDA", f"{value_result}")
                self.output.add_instruction("ORA", f"{value_result}+1")
                self.output.add_instruction("BNE", set_true_label)
            self._get_temp_var_with_value(0, result_var)
            self.output.add_instruction("JMP", end_label)
            self.output.add_label(set_true_label)
            self._get_temp_var_with_value(1, result_var)
        self.output.add_label(end_label)
        return result_var, DataType.INT16

    def visit_function_call(self, node: FunctionCall) -> Any:
        if node.name == "print":
            if node.arguments:
                arg_result, _ = node.arguments[0].accept(self)
                self.output.add_instruction("LDA", f"{arg_result}")
                self.output.add_instruction("STA", "PRINT_VALUE")
                self.output.add_instruction("LDA", f"{arg_result}+1")
                self.output.add_instruction("STA", "PRINT_VALUE+1")
                self.output.add_instruction("JSR", "print_int16")
                self.used_routines.add("print_int16")
            return None, DataType.VOID

        func = self.symbol_table.lookup_function(node.name)
        if not func:
            raise CompilerError(f"Undefined function: {node.name}")
        if not func.entry_label.startswith("FUNC_"):
            self.used_routines.add(func.entry_label)
        for arg in reversed(node.arguments):
            arg_result, _ = arg.accept(self)
            self.output.add_instruction("LDA", f"{arg_result}+1")
            self.output.add_instruction("PHA")
            self.output.add_instruction("LDA", f"{arg_result}")
            self.output.add_instruction("PHA")
        self.output.add_instruction("JSR", func.entry_label)
        if func.return_type != DataType.VOID:
            return "RETURN_VALUE", func.return_type
        return None, DataType.VOID

    def visit_assignment(self, node: Assignment) -> Any:
        value_result, value_type = node.value.accept(self)
        if isinstance(node.target, str):
            var = self.symbol_table.lookup_variable(node.target) or self.symbol_table.declare_variable(node.target, value_type)
            self.output.add_instruction("LDA", f"{value_result}")
            self.output.add_instruction("STA", f"{var.name}")
            self.output.add_instruction("LDA", f"{value_result}+1")
            self.output.add_instruction("STA", f"{var.name}+1")

    def visit_if_statement(self, node: IfStatement) -> Any:
        condition_result, _ = node.condition.accept(self)
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
        loop_label = self.label_manager.generate_label("WHILE_LOOP")
        end_label = self.label_manager.generate_label("END_WHILE")
        self.loop_stack.append((loop_label, end_label))
        self.output.add_label(loop_label)
        condition_result, _ = node.condition.accept(self)
        self.output.add_instruction("LDA", f"{condition_result}")
        self.output.add_instruction("ORA", f"{condition_result}+1")
        self.output.add_instruction("BEQ", end_label)
        for stmt in node.body:
            stmt.accept(self)
        self.output.add_instruction("JMP", loop_label)
        self.output.add_label(end_label)
        self.loop_stack.pop()

    def visit_for_statement(self, node: ForStatement) -> Any:
        if node.iterable:
            loop_label = self.label_manager.generate_label("FOR_LIST_LOOP")
            end_label = self.label_manager.generate_label("END_FOR_LIST")
            self.loop_stack.append((loop_label, end_label))
            list_ptr_var, _ = node.iterable.accept(self)
            loop_var = self.symbol_table.declare_variable(node.var, DataType.INT16)
            index_var = self._get_temp_var_with_value(0)
            length_var = self._get_temp_var()

            # Get list length (simplified)
            self.output.add_instruction("LDA", f"({list_ptr_var})")
            self.output.add_instruction("STA", f"{length_var}")
            self.output.add_instruction("LDA", "#0")
            self.output.add_instruction("STA", f"{length_var}+1")

            loop_label = self.label_manager.generate_label("FOR_LIST_LOOP")
            end_label = self.label_manager.generate_label("END_FOR_LIST")
            self.output.add_label(loop_label)

            self._generate_compare_int16(index_var, length_var)
            self.output.add_instruction("BNE", end_label)

            # Get element (simplified)
            # ...

            for stmt in node.body:
                stmt.accept(self)

            self._generate_add_int16(index_var, self._get_temp_var_with_value(1), index_var)
            self.output.add_instruction("JMP", loop_label)
            self.output.add_label(end_label)
            self.loop_stack.pop()
        else: # range
            loop_label = self.label_manager.generate_label("FOR_LOOP")
            end_label = self.label_manager.generate_label("END_FOR")
            self.loop_stack.append((loop_label, end_label))
            start_result, _ = node.start.accept(self)
            var = self.symbol_table.declare_variable(node.var, DataType.INT16)
            self.output.add_instruction("LDA", f"{start_result}")
            self.output.add_instruction("STA", f"{var.name}")
            self.output.add_instruction("LDA", f"{start_result}+1")
            self.output.add_instruction("STA", f"{var.name}+1")
            loop_label = self.label_manager.generate_label("FOR_LOOP")
            end_label = self.label_manager.generate_label("END_FOR")
            self.output.add_label(loop_label)
            end_result, _ = node.end.accept(self)
            self._generate_compare_int16(var.name, end_result)
            self.output.add_instruction("BNE", end_label)
            for stmt in node.body:
                stmt.accept(self)
            step_result, _ = node.step.accept(self)
            self._generate_add_int16(var.name, step_result, var.name)
            self.output.add_instruction("JMP", loop_label)
            self.output.add_label(end_label)
            self.loop_stack.pop()

    def visit_function_definition(self, node: FunctionDefinition) -> Any:
        func = self.symbol_table.lookup_function(node.name)
        func.entry_label = f"FUNC_{node.name}"
        self.output.add_label(func.entry_label)
        self.symbol_table.enter_scope(node.name)
        for param in func.parameters:
            self.symbol_table.declare_variable(param.name, param.data_type, is_parameter=True)
        for stmt in node.body:
            stmt.accept(self)
        self.output.add_instruction("RTS")
        self.symbol_table.exit_scope()

    def visit_return_statement(self, node: ReturnStatement) -> Any:
        if node.value:
            result, _ = node.value.accept(self)
            self.output.add_instruction("LDA", f"{result}")
            self.output.add_instruction("STA", "RETURN_VALUE")
            self.output.add_instruction("LDA", f"{result}+1")
            self.output.add_instruction("STA", "RETURN_VALUE+1")
        self.output.add_instruction("RTS")

    def visit_list_literal(self, node: ListLiteral) -> Any:
        if not self.list_support_initialized:
            self.list_support_initialized = True
        list_ptr_var = self._get_temp_var()
        list_size = 1 + len(node.elements) * 2
        self.output.add_instruction("LDA", "HEAP_POINTER")
        self.output.add_instruction("STA", f"{list_ptr_var}")
        self.output.add_instruction("LDA", "HEAP_POINTER+1")
        self.output.add_instruction("STA", f"{list_ptr_var}+1")
        self.output.add_instruction("LDY", "#0")
        self.output.add_instruction("LDA", f"#{len(node.elements)}")
        self.output.add_instruction("STA", f"({list_ptr_var}),Y")
        current_offset = 1
        for element_expr in node.elements:
            element_var, _ = element_expr.accept(self)
            self.output.add_instruction("LDA", f"{element_var}")
            self.output.add_instruction("LDY", f"#{current_offset}")
            self.output.add_instruction("STA", f"({list_ptr_var}),Y")
            self.output.add_instruction("LDA", f"{element_var}+1")
            self.output.add_instruction("INY")
            self.output.add_instruction("STA", f"({list_ptr_var}),Y")
            current_offset += 2
        size_var = self._get_temp_var_with_value(list_size)
        self._generate_add_int16("HEAP_POINTER", size_var, "HEAP_POINTER")
        return list_ptr_var, DataType.LIST

    def visit_subscript(self, node: Subscript) -> Any:
        list_ptr_var, _ = node.name.accept(self)
        index_var, _ = node.index.accept(self)
        self.used_routines.add("get_list_element")
        # Simplified argument passing
        self.output.add_instruction("LDA", f"{list_ptr_var}")
        self.output.add_instruction("STA", "LIST_ROUTINE_ARG1")
        self.output.add_instruction("LDA", f"{list_ptr_var}+1")
        self.output.add_instruction("STA", "LIST_ROUTINE_ARG1+1")
        self.output.add_instruction("LDA", f"{index_var}")
        self.output.add_instruction("STA", "LIST_ROUTINE_ARG2")
        self.output.add_instruction("LDA", f"{index_var}+1")
        self.output.add_instruction("STA", "LIST_ROUTINE_ARG2+1")
        self.output.add_instruction("JSR", "get_list_element")
        result_var = self._get_temp_var()
        self.output.add_instruction("LDA", "LIST_ROUTINE_RET1")
        self.output.add_instruction("STA", f"{result_var}")
        self.output.add_instruction("LDA", "LIST_ROUTINE_RET1+1")
        self.output.add_instruction("STA", f"{result_var}+1")
        return result_var, DataType.INT16

    def _get_temp_var(self) -> str:
        temp_name = f"TEMP_{self.temp_var_counter}"
        self.temp_var_counter += 1
        return temp_name

    def _get_temp_var_with_value(self, value: int, var_name: str = None) -> str:
        if not var_name:
            var_name = self._get_temp_var()
        self.output.add_instruction("LDA", f"#<{value}")
        self.output.add_instruction("STA", f"{var_name}")
        self.output.add_instruction("LDA", f"#{value}>>8")
        self.output.add_instruction("STA", f"{var_name}+1")
        return var_name

    def _generate_add_int16(self, left: str, right: str, result: str):
        self.output.add_instruction("CLC")
        self.output.add_instruction("LDA", f"{left}")
        self.output.add_instruction("ADC", f"{right}")
        self.output.add_instruction("STA", f"{result}")
        self.output.add_instruction("LDA", f"{left}+1")
        self.output.add_instruction("ADC", f"{right}+1")
        self.output.add_instruction("STA", f"{result}+1")

    def _generate_sub_int16(self, left: str, right: str, result: str):
        self.output.add_instruction("SEC")
        self.output.add_instruction("LDA", f"{left}")
        self.output.add_instruction("SBC", f"{right}")
        self.output.add_instruction("STA", f"{result}")
        self.output.add_instruction("LDA", f"{left}+1")
        self.output.add_instruction("SBC", f"{right}+1")
        self.output.add_instruction("STA", f"{result}+1")

    def _generate_mul_int16(self, left: str, right: str, result: str):
        self.used_routines.add("multiply16x16")
        self.output.add_instruction("LDA", f"{left}")
        self.output.add_instruction("STA", "MULT_ARG1")
        self.output.add_instruction("LDA", f"{left}+1")
        self.output.add_instruction("STA", "MULT_ARG1+1")
        self.output.add_instruction("LDA", f"{right}")
        self.output.add_instruction("STA", "MULT_ARG2")
        self.output.add_instruction("LDA", f"{right}+1")
        self.output.add_instruction("STA", "MULT_ARG2+1")
        self.output.add_instruction("JSR", "multiply16x16")
        self.output.add_instruction("LDA", "MULT_RESULT+2")
        self.output.add_instruction("STA", f"{result}")
        self.output.add_instruction("LDA", "MULT_RESULT+3")
        self.output.add_instruction("STA", f"{result}+1")

    def _generate_compare_int16(self, left: str, right: str):
        self.output.add_instruction("LDA", f"{left}+1")
        self.output.add_instruction("CMP", f"{right}+1")
        self.output.add_instruction("BNE", "SKIP_LO_CMP")
        self.output.add_instruction("LDA", f"{left}")
        self.output.add_instruction("CMP", f"{right}")
        self.output.add_label("SKIP_LO_CMP")

    def _generate_xor_int16(self, left: str, right: str, result: str):
        self.output.add_instruction("LDA", f"{left}")
        self.output.add_instruction("EOR", f"{right}")
        self.output.add_instruction("STA", f"{result}")
        self.output.add_instruction("LDA", f"{left}+1")
        self.output.add_instruction("EOR", f"{right}+1")
        self.output.add_instruction("STA", f"{result}+1")

    def _generate_not_op(self, operand: str, result: str):
        is_not_zero_label = self.label_manager.generate_label("IS_NOT_ZERO")
        end_not_label = self.label_manager.generate_label("END_NOT")
        self.output.add_instruction("LDA", f"{operand}")
        self.output.add_instruction("ORA", f"{operand}+1")
        self.output.add_instruction("BNE", is_not_zero_label)
        self._get_temp_var_with_value(1, result)
        self.output.add_instruction("JMP", end_not_label)
        self.output.add_label(is_not_zero_label)
        self._get_temp_var_with_value(0, result)
        self.output.add_label(end_not_label)
