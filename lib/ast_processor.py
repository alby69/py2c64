# py2asm/lib/ast_processor.py
import ast
from .. import globals
from . import func_expressions
from . import func_core
from . import func_dict
from . import func_c64         # NEW: Import for C64 specific functions
from . import func_structures  # NEW: Import for control structures

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
        gen_code.extend(func_core._generate_float_to_int_conversion(temp_result_var, temp_result_var)) # type: ignore
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
        if not isinstance(call_node.func, ast.Name):
            report_error("Calling methods on objects is not supported.", node=call_node)
            return

        func_name = call_node.func.id

        # --- REFACTORED: Delegate C64-specific function calls to the dedicated handler ---
        if func_c64.process_c64_call(call_node, current_func_info):
            return # The call was handled by the C64 module

        # --- Handle other built-in functions ---
        if func_name == 'print':
            func_core.process_print_call(call_node, error_handler_func, current_func_info, func_expressions)
            return
        # ... other built-in function handlers can go here

        # --- Handle user-defined functions (Stack-based calling convention) ---
        if func_name in globals.defined_functions:
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
    # Handle function calls that return a value, e.g., collision checks
    if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Call):
        target_var_name = node.targets[0].id
        call_node = node.value
        if isinstance(call_node.func, ast.Name):
            func_name = call_node.func.id

            if func_name in ['sprite_check_collision_sprite', 'sprite_check_collision_data']:
                if len(call_node.args) != 0:
                    report_error(f"Function '{func_name}' expects 0 arguments, got {len(call_node.args)}.", node=call_node)
                    return

                current_func_name = current_func_info.get('name') if current_func_info else None
                resolved_var_name = func_core.resolve_variable_name(target_var_name, current_func_name)

                gen_code.append(f"    ; --- Chiamata a {func_name} con assegnazione a {resolved_var_name} ---")
                gen_code.append(f"    JSR {func_name}")
                used_routines.add(func_name)
                # The result is in the A register (8-bit)
                gen_code.append(f"    STA {resolved_var_name}      ; Salva il risultato (LSB)")
                gen_code.append(f"    LDA #0")
                gen_code.append(f"    STA {resolved_var_name}+1    ; Pulisce MSB (valore a 8 bit)")
                gen_code.append(f"    ; --- Fine chiamata ---")
                return # Assignment handled

    # --- Original logic for other assignments ---
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
        func_dict.handle_dict_assignment(node)
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
                _evaluate_expression_to_ax(statement.value, error_handler_func, current_func_info)
            gen_code.append(f"    JMP {ret_label}")
        # --- MODIFIED: Call functions from the new module ---
        elif isinstance(statement, ast.If):
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