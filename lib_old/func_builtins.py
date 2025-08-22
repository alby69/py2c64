# /workspaces/py2c64/lib/func_builtins.py

import ast

import V1.globals as globals
from lib_old import func_core
from lib_old import func_expressions
from lib_old.builtin_function_specs import BUILTIN_FUNCTION_SPECS

# Aliases
gen_code = globals.generated_code
variables = globals.variables
used_routines = globals.used_routines
report_error = globals.report_compiler_error

# --- Special Handlers ---

def _handle_print(call_node, spec, current_func_info, target_var_name=None):
    """
    Generates code for the print() function.
    Handles multiple arguments of different types.
    """
    if not call_node.args:
        gen_code.append("jsr print_newline")
        used_routines.add('print_newline')
        return

    for i, arg_node in enumerate(call_node.args):
        if i > 0:
            gen_code.append("jsr print_space")
            used_routines.add('print_space')

        temp_arg_var = func_core.get_temp_var()
        func_expressions.translate_expression_recursive(temp_arg_var, arg_node, func_core.get_current_func_name(current_func_info))
        arg_type = variables.get(temp_arg_var, {}).get('type', 'int')

        if arg_type == 'float':
            func_core.load_fp1_from_var(temp_arg_var)
            gen_code.append("jsr print_float")
            used_routines.add('print_float')
        elif arg_type == 'pointer': # Assumes string pointer
            func_core.load_ax_from_var(temp_arg_var)
            gen_code.append(f"sta ${globals.PRINT_STRING_ZP_BASE_PTR:02x}")
            gen_code.append(f"stx ${globals.PRINT_STRING_ZP_BASE_PTR+1:02x}")
            gen_code.append("jsr print_string_from_zp")
            used_routines.add('print_string_from_zp')
        else: # int
            func_core.load_ax_from_var(temp_arg_var)
            gen_code.append("jsr print_integer")
            used_routines.add('print_integer')

        func_core.release_temp_var(temp_arg_var)

    gen_code.append("jsr print_newline")
    used_routines.add('print_newline')

def _handle_abs(call_node, spec, current_func_info, target_var_name):
    """
    Generates code for abs(x). Handles both integer and float types.
    """
    if len(call_node.args) != 1:
        report_error(f"abs() expects 1 argument, got {len(call_node.args)}.", call_node.lineno)
        return

    resolved_target_name = func_core.resolve_variable_name(target_var_name, func_core.get_current_func_name(current_func_info))
    temp_arg_var = func_core.get_temp_var()
    func_expressions.translate_expression_recursive(temp_arg_var, call_node.args[0], func_core.get_current_func_name(current_func_info))
    arg_type = variables.get(temp_arg_var, {}).get('type', 'int')

    if arg_type == 'float':
        func_core.handle_variable(resolved_target_name, size=4, var_type='float')
        func_core.load_fp1_from_var(temp_arg_var)
        gen_code.append("jsr FP_ABS")
        used_routines.add('FP_ABS')
        func_core.store_fp1_in_var(resolved_target_name)
    else: # int
        func_core.handle_variable(resolved_target_name, size=2, var_type='int')
        func_core.load_ax_from_var(temp_arg_var)
        gen_code.append("jsr integer_abs")
        used_routines.add('integer_abs')
        func_core.store_ax_in_var(resolved_target_name)

    func_core.release_temp_var(temp_arg_var)

def _handle_len(call_node, spec, current_func_info, target_var_name):
    """
    Generates code for len(obj). Currently supports strings.
    """
    if len(call_node.args) != 1:
        report_error(f"len() expects 1 argument, got {len(call_node.args)}.", call_node.lineno)
        return

    resolved_target_name = func_core.resolve_variable_name(target_var_name, func_core.get_current_func_name(current_func_info))
    func_core.handle_variable(resolved_target_name, size=2, var_type='int')

    temp_arg_var = func_core.get_temp_var()
    func_expressions.translate_expression_recursive(temp_arg_var, call_node.args[0], func_core.get_current_func_name(current_func_info))
    arg_type = variables.get(temp_arg_var, {}).get('type', 'unknown')

    if arg_type != 'pointer':
        report_error(f"len() is only supported for strings, but got type '{arg_type}'.", call_node.lineno)
        func_core.release_temp_var(temp_arg_var)
        return

    func_core.load_ax_from_var(temp_arg_var) # Load string pointer into AX
    gen_code.append("jsr strlen")
    used_routines.add('strlen')
    func_core.store_ax_in_var(resolved_target_name) # Store resulting length
    func_core.release_temp_var(temp_arg_var)

def _handle_input(call_node, spec, current_func_info, target_var_name):
    """
    Generates code for input([prompt]).
    """
    if len(call_node.args) > 1:
        report_error(f"input() expects at most 1 argument, got {len(call_node.args)}.", call_node.lineno)
        return

    if call_node.args:
        prompt_node = call_node.args[0]
        temp_prompt_var = func_core.get_temp_var()
        func_expressions.translate_expression_recursive(temp_prompt_var, prompt_node, func_core.get_current_func_name(current_func_info))
        if variables.get(temp_prompt_var, {}).get('type') != 'pointer':
            report_error(f"input() prompt must be a string.", call_node.lineno)
            func_core.release_temp_var(temp_prompt_var)
            return
        func_core.load_ax_from_var(temp_prompt_var)
        gen_code.append(f"sta ${globals.PRINT_STRING_ZP_BASE_PTR:02x}")
        gen_code.append(f"stx ${globals.PRINT_STRING_ZP_BASE_PTR+1:02x}")
        gen_code.append("jsr print_string_from_zp")
        used_routines.add('print_string_from_zp')
        func_core.release_temp_var(temp_prompt_var)

    resolved_target_name = func_core.resolve_variable_name(target_var_name, func_core.get_current_func_name(current_func_info))
    func_core.handle_variable(resolved_target_name, size=2, var_type='pointer')
    gen_code.append("jsr read_string_input")
    used_routines.add('read_string_input')
    func_core.store_ax_in_var(resolved_target_name)

SPECIAL_HANDLERS = {
    'print': _handle_print,
    'abs': _handle_abs,
    'len': _handle_len,
    'input': _handle_input,
}

def _process_builtin_call(call_node, spec, current_func_info, target_var_name=None):
    func_name = call_node.func.id
    if 'special_handling' in spec:
        handler_func = SPECIAL_HANDLERS.get(spec['special_handling'])
        if handler_func:
            handler_func(call_node, spec, current_func_info, target_var_name)
            return
        report_error(f"Internal Error: No special handler for '{spec['special_handling']}'.", call_node.lineno)
        return

    args = call_node.args
    if len(args) != len(spec.get('params', [])):
        report_error(f"Incorrect args for '{func_name}'. Expected {len(spec.get('params', []))}, got {len(args)}.", call_node.lineno)
        return

    if args:
        temp_arg_var = func_core.get_temp_var()
        func_expressions.translate_expression_recursive(temp_arg_var, args[0], func_core.get_current_func_name(current_func_info))
        if variables.get(temp_arg_var, {}).get('type') == 'float':
            func_core.load_fp1_from_var(temp_arg_var)
        else:
            func_core.load_ax_from_var(temp_arg_var)
        func_core.release_temp_var(temp_arg_var)

    gen_code.append(f"jsr {spec['routine']}")
    used_routines.add(spec['routine'])

    if target_var_name:
        resolved_target_name = func_core.resolve_variable_name(target_var_name, func_core.get_current_func_name(current_func_info))
        return_type = spec.get('return', {}).get('type', 'int')
        func_core.handle_variable(resolved_target_name, size=4 if return_type == 'float' else 2, var_type=return_type)
        if return_type == 'float':
            func_core.store_fp1_in_var(resolved_target_name)
        else:
            func_core.store_ax_in_var(resolved_target_name)

def handle_builtin_call(call_node, current_func_info=None):
    if not hasattr(call_node.func, 'id'): return False
    spec = BUILTIN_FUNCTION_SPECS.get(call_node.func.id)
    if not spec: return False
    _process_builtin_call(call_node, spec, current_func_info, target_var_name=None)
    return True

def handle_builtin_assignment(assign_node, current_func_info=None):
    if not isinstance(assign_node.value, ast.Call) or not hasattr(assign_node.value.func, 'id'): return False
    call_node = assign_node.value
    spec = BUILTIN_FUNCTION_SPECS.get(call_node.func.id)
    if not spec or 'return' not in spec or spec['return'] is None: return False
    if len(assign_node.targets) != 1 or not isinstance(assign_node.targets[0], ast.Name):
        report_error(f"Assignment from '{call_node.func.id}' must be to a single variable.", assign_node.lineno)
        return True
    _process_builtin_call(call_node, spec, current_func_info, assign_node.targets[0].id)
    return True