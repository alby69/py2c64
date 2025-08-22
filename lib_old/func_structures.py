# py2c64/lib/func_structures.py

import ast
import V1.globals as globals

class FuncStructures:
    def __init__(self, ast_processor, func_core, func_operations, func_expressions, func_strings, func_dict, func_c64, func_builtins, c64_routine_library, globals):
        self.ast_processor = ast_processor
        self.func_core = func_core
        self.func_operations = func_operations
        self.func_expressions = func_expressions
        self.func_strings = func_strings
        self.func_dict = func_dict
        self.func_c64 = func_c64
        self.func_builtins = func_builtins
        self.c64_routine_library = c64_routine_library
        self.globals = globals  # Make sure 'globals' is accessible as an attribute

    def process_if_node(self, node: ast.If, error_handler_func, current_func_info=None):
        """Processes an if statement."""
        # Generate unique labels for the if-else structure
        else_label = self.func_core.create_label("if_else", str(self.globals.label_counter))
        end_if_label = self.func_core.create_label("if_end", str(self.globals.label_counter))
        self.globals.label_counter += 1

        # Process the condition (it might involve a comparison or a boolean expression)
        self._process_condition(node.test, else_label, current_func_info)

        # Process the 'if' block's body
        for statement in node.body:
            self.ast_processor.process_node(statement, error_handler_func, current_func_info)

        # Jump to the end if there's an 'else' block
        if node.orelse:
            self.globals.generated_code.append(f"    JMP {end_if_label}")

        # Label for the 'else' block
        self.globals.generated_code.append(f"{else_label}:")

        # Process the 'else' block's body, if present
        if node.orelse:
            for statement in node.orelse:
                self.ast_processor.process_node(statement, error_handler_func, current_func_info)

        # Label for the end of the 'if' statement
        self.globals.generated_code.append(f"{end_if_label}:")

    def _process_condition(self, condition_node, else_label, current_func_info):
        """Processes the condition of an if statement."""
        if isinstance(condition_node, ast.Compare):
            # Comparisons handled by func_operations (assuming it now includes branching logic)
            # func_operations.handle_comparison_for_branching handles the details
            # and generates appropriate code based on the operator.
            # The negate flag is False for a standard 'if' condition.
            self.func_operations.handle_comparison_for_branching(condition_node, else_label, current_func_info, negate=False)

        elif isinstance(condition_node, ast.UnaryOp) and isinstance(condition_node.op, ast.Not):
            # 'not' operator: negates the result of the inner condition
            if isinstance(condition_node.operand, ast.Compare):
                # Negated comparisons (like `if not x == 5:`)
                self.func_operations.handle_comparison_for_branching(condition_node.operand, else_label, current_func_info, negate=True)
            else:
                self.globals.report_error(f"Unsupported condition structure with 'not': {ast.dump(condition_node)}", condition_node)
                return  # Avoid further processing if unsupported structure

        elif isinstance(condition_node, ast.Name):
            # Existing logic for direct variable names (still treated as "if var:")
            resolved_var_name = self.func_core.resolve_variable_name(condition_node.id, current_func_info.get('name') if current_func_info else None)
            # Check if the variable is not zero (16-bit check, assuming 16-bit integers)
            self.globals.generated_code.extend([
                f"    LDA {resolved_var_name}",
                f"    ORA {resolved_var_name}+1",  # If either byte is non-zero, it's true
                f"    BEQ {else_label}"  # Branch to 'else' if zero (condition is false)
            ])
        else:
            # Use the correct function for reporting errors
            self.globals.report_compiler_error(f"Unsupported condition type: {type(condition_node).__name__}", condition_node)

    def _handle_and(self, node: ast.BoolOp) -> str:
        code = ""
        for i, value in enumerate(node.values):
            code += self._evaluate_condition(value)
            if i < len(node.values) - 1:
                code += f"    beq {self.globals.get_label('end_and')}\n"
        code += f"{self.globals.get_label('end_and')}:\n"
        return code
