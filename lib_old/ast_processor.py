# py2c64/lib/ast_processor.py
import ast
import V1.globals as globals
from . import func_expressions
from . import func_core
from . import func_dict
from . import func_c64
from . import func_builtins
from . import func_structures

# Aliases
gen_code = globals.generated_code
variables = globals.variables
used_routines = globals.used_routines
report_error = globals.report_compiler_error

def _evaluate_expression_to_ax(node, error_handler_func, current_func_info=None):
    """
    Wrapper per la logica di valutazione delle espressioni.
    """
    temp_result_var = func_core.get_temp_var()
    func_expressions.translate_expression_recursive(temp_result_var, node, current_func_info.get('name') if current_func_info else None)

    is_float_result = variables.get(temp_result_var, {}).get('type') == 'float'

    if is_float_result:
        # Convert float to int for pushing onto the 16-bit stack.
        # This is a temporary simplification. Proper float argument handling is needed.
        func_core._generate_float_to_int_conversion(temp_result_var, temp_result_var)
        # Now temp_result_var holds the 16-bit integer representation.
        gen_code.append(f"    LDA {temp_result_var}+1") # High byte
        gen_code.append(f"    LDX {temp_result_var}")   # Low byte
    else:
        gen_code.append(f"    LDA {temp_result_var}+1") # High byte
        gen_code.append(f"    LDX {temp_result_var}")   # Low byte

    func_core.release_temp_var(temp_result_var)

def process_expr_node(node, error_handler_func, current_func_info=None):
    """Processes an ast.Expr node, which is a wrapper for standalone expressions like function calls."""
    if not isinstance(node, ast.Expr):
        return

    if isinstance(node.value, ast.Call):
        call_node = node.value

        # --- REFACTORED: Delegate function calls to dedicated handlers ---

        # 1. Delegate to dict method handler (e.g., my_dict.clear())
        if func_dict.handle_dict_method_call(call_node, current_func_info):
            return

        # If it wasn't a dict method, it must be a simple function name to be handled further.
        if not isinstance(call_node.func, ast.Name):
            report_error("Calling methods on objects other than dictionaries is not supported.", node=call_node)
            return

        # 2. Delegate to C64 hardware function handler
        if func_c64.handle_c64_call(call_node, current_func_info):
            return

        # 3. Delegate to built-in function handler
        if func_builtins.handle_builtin_call(call_node, current_func_info):
            return

        # --- Handle user-defined functions (Stack-based calling convention) ---
        func_name = call_node.func.id
        if func_name in globals.defined_functions:
            # This is a standalone call, so the return value is discarded.
            func_info = globals.defined_functions[func_name]

            # Check argument count
            if len(call_node.args) != len(func_info['params']):
                report_error(f"Function '{func_name}' called with {len(call_node.args)} arguments, but expected {len(func_info['params'])}.", node=call_node)
                return

            gen_code.append(f"    ; --- Preparazione chiamata a {func_name} ---")

            # 1. Evaluate and push arguments onto the stack (in reverse order)
            total_arg_size = 0
            for arg_node in reversed(call_node.args):
                _evaluate_expression_to_ax(arg_node, error_handler_func, current_func_info)
                gen_code.append("    JSR push_word_ax")
                used_routines.add('push_word_ax')
                total_arg_size += 2

            # 2. Call the function
            gen_code.append(f"    JSR {func_info['label']}")

            # 3. Clean up the stack (caller's responsibility)
            if total_arg_size > 0:
                gen_code.extend([
                    f"    ; Caller pulisce {total_arg_size} byte di argomenti dallo stack",
                    "    CLC",
                    f"    LDA ${globals.STACK_POINTER_ZP:02X}",
                    f"    ADC #{total_arg_size}",
                    f"    STA ${globals.STACK_POINTER_ZP:02X}",
                    f"    LDA ${globals.STACK_POINTER_ZP+1:02X}",
                    f"    ADC #0",
                    f"    STA ${globals.STACK_POINTER_ZP+1:02X}"
                ])

            # The return value is now in A/X, but since this is a standalone expression, it's discarded.
            gen_code.append(f"    ; --- Fine chiamata a {func_name} (valore di ritorno in A/X scartato) ---")

        else:
            report_error(f"Chiamata a funzione non definita '{func_name}'.", node=call_node)
    else:
        # For other standalone expressions (e.g., a line with just `5`), evaluate and discard the result.
        _evaluate_expression_to_ax(node.value, error_handler_func, current_func_info)


def process_assign_node(node, current_func_info=None):
    """Processes an ast.Assign node."""
    # --- REFACTORED: Delegate assignments from function calls ---
    if isinstance(node.value, ast.Call):
        # 1. Delegate to dict method handler (e.g., x = my_dict.get('k'))
        if func_dict.handle_dict_assignment(node, current_func_info):
            return

        # 1. Delegate to C64 hardware function handler
        if func_c64.handle_c64_assignment(node, current_func_info):
            return

        # 2. Delegate to built-in function handler
        if func_builtins.handle_builtin_assignment(node, current_func_info):
            return

        # 3. Handle user-defined functions that return a value
        # (This logic would go here if user-defined functions are implemented)

    # --- Logic for regular assignments (not from function calls) ---
    if len(node.targets) > 1:
        report_error("Multiple assignment targets not supported.", node=node)
        return

    target = node.targets[0]
    if isinstance(target, ast.Name):
        var_name = target.id
        current_func_name = current_func_info.get('name') if current_func_info else None
        resolved_var_name = func_core.resolve_variable_name(var_name, current_func_name)
        func_expressions.translate_expression_recursive(resolved_var_name, node.value, current_func_name)
    elif isinstance(target, ast.Subscript):
        # This handles my_dict['key'] = value. This is not yet implemented.
        # The old call to handle_dict_assignment was incorrect for this case.
        report_error(f"Assignment to a dictionary key (e.g., my_dict['key'] = value) is not yet supported.", node=target)
    else:
        report_error(f"Assignment to target of type {type(target).__name__} not supported.", node=target)

def process_function_def_node(node, error_handler_func):
    func_name = node.name
    func_info = globals.defined_functions[func_name]
    func_label = func_info['label']
    ret_label = func_info['ret_label']

    gen_code.append(f"\n{func_label}:")
    gen_code.append(f"    ; --- Function Prologue for {func_name} ---")

    # 1. Save old Frame Pointer (FP) onto the stack
    gen_code.extend([
        f"    LDA #<{globals.FRAME_POINTER_ZP:04X}",
        f"    STA ${globals.TEMP_PTR1:02X}",
        f"    LDA #>{globals.FRAME_POINTER_ZP:04X}",
        f"    STA ${globals.TEMP_PTR1+1:02X}",
        f"    JSR push_word_from_addr"
    ])
    used_routines.add('push_word_from_addr')

    # 2. Set new Frame Pointer (FP) to current Stack Pointer (SP)
    gen_code.extend(func_core._generate_copy_2_bytes(
        globals.STACK_POINTER_ZP, globals.FRAME_POINTER_ZP
    ))

    # 3. Allocate space for local variables
    total_locals_size = func_info.get('total_locals_size', 0)
    if total_locals_size > 0:
        gen_code.append(f"    ; Allocate {total_locals_size} bytes for local variables")
        gen_code.extend([
            f"    SEC",
            f"    LDA ${globals.STACK_POINTER_ZP:02X}",
            f"    SBC #{total_locals_size & 0xFF}",
            f"    STA ${globals.STACK_POINTER_ZP:02X}",
            f"    LDA ${globals.STACK_POINTER_ZP+1:02X}",
            f"    SBC #{(total_locals_size >> 8) & 0xFF}",
            f"    STA ${globals.STACK_POINTER_ZP+1:02X}"
        ])

    gen_code.append(f"    ; --- End Function Prologue ---")

    # Process function body
    current_func_info = {'name': func_name, 'params': func_info['params']}
    for statement in node.body:
        if isinstance(statement, ast.Expr):
            process_expr_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.Assign):
            process_assign_node(statement, current_func_info)
        elif isinstance(statement, ast.Return):
            if statement.value:
                # Determine the type of the return expression to use the correct return register(s)
                temp_return_var = func_core.get_temp_var()
                func_expressions.translate_expression_recursive(
                    temp_return_var, statement.value, current_func_info.get('name')
                )
                return_type = variables.get(temp_return_var, {}).get('type', 'int')

                if return_type == 'float':
                    # Load float value into FP1 for return
                    func_core.load_fp1_from_var(temp_return_var)
                else:
                    # Load integer/pointer value into A/X for return
                    func_core.load_ax_from_var(temp_return_var)

                func_core.release_temp_var(temp_return_var)
            else:
                # No return value (or `return None`), so return 0 in A/X
                gen_code.extend(["    LDA #0", "    LDX #0"])
            gen_code.append(f"    JMP {ret_label}")
        # --- MODIFIED: Call functions from the new module ---
        if isinstance(statement, ast.If):
            func_structures.process_if_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.For):
            func_structures.process_for_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.While):
            func_structures.process_while_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.Global):
            pass # Handled in collection pass
        else:
            report_error(f"Unhandled statement type in function '{func_name}': {type(statement).__name__}", node=statement, level="WARNING")

    # Function Epilogue
    gen_code.append(f"\n{ret_label}:")
    gen_code.append(f"    ; --- Function Epilogue for {func_name} ---")

    # 1. Deallocate local variables (restore SP from FP)
    gen_code.extend(func_core._generate_copy_2_bytes(
        globals.FRAME_POINTER_ZP, globals.STACK_POINTER_ZP
    ))

    # 2. Restore old Frame Pointer (FP) from stack
    gen_code.extend([
        f"    LDA #<{globals.FRAME_POINTER_ZP:04X}",
        f"    STA ${globals.TEMP_PTR1:02X}",
        f"    LDA #>{globals.FRAME_POINTER_ZP:04X}",
        f"    STA ${globals.TEMP_PTR1+1:02X}",
        f"    JSR pop_word_to_addr"
    ])
    used_routines.add('pop_word_to_addr')

    # 3. Return from subroutine
    gen_code.append(f"    RTS")
    gen_code.append(f"    ; --- End Function Epilogue ---")

# --- Placeholder functions for other AST nodes ---

def process_delete_node(node):
    gen_code.append(f"; Placeholder per Delete")

def process_try_node(node, error_handler_func):
    gen_code.append(f"; Placeholder per Try block")

class AstProcessor:  # Add the class definition here
    def __init__(self, func_expressions, func_core, func_dict, func_c64, func_builtins):
        self.func_expressions = func_expressions
        self.func_core = func_core
        self.func_dict = func_dict
        self.func_c64 = func_c64
        self.func_builtins = func_builtins
    def process_node(self, node, error_handler_func, current_func_info=None):
        if isinstance(node, ast.Assign):
            self.process_assign_node(node, current_func_info)
        elif isinstance(node, ast.Expr):
            self.process_expr_node(node, error_handler_func, current_func_info)
        else:
            report_error(f"Unhandled node type: {type(node).__name__}", node=node)

    def process_assign_node(self, node, current_func_info=None):
        process_assign_node(node, current_func_info)

    def process_expr_node(self, node, error_handler_func, current_func_info=None):
        process_expr_node(node, error_handler_func, current_func_info)
