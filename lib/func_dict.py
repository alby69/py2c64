# py2c64/lib/func_dict.py

import ast

import globals
import lib.func_core
import lib.func_expressions
from lib.dict_method_specs import DICT_METHOD_SPECS

# Aliases
gen_code = globals.generated_code
variables = globals.variables
used_routines = globals.used_routines
report_error = globals.report_compiler_error

# --- Calling Convention for Dictionary Runtime Routines ---
# These ZP locations are used to pass arguments to the assembly routines.
ZP_DICT_PTR = "$f0"  # Pointer to the dictionary object struct
ZP_ARG1_PTR = "$f2"  # Pointer to the variable holding the first argument
ZP_ARG2_PTR = "$f4"  # Pointer to the variable holding the second argument

def _process_dict_method_call(call_node, spec, dict_var_name, current_func_info, target_var_name=None):
    """
    Shared logic to process arguments and generate the JSR for a dictionary method call.
    This function implements the standard calling convention for dictionary methods.
    """
    method_name = call_node.func.attr
    params = spec.get('params', [])
    args = call_node.args
    current_func_name = func_core.get_current_func_name(current_func_info)

    # --- 1. Validate Arguments ---
    required_params = [p for p in params if p.get('required', False)]
    if len(args) < len(required_params) or len(args) > len(params):
        report_error(f"Incorrect args for '{method_name}'. Expected between {len(required_params)} and {len(params)}, got {len(args)}.", call_node.lineno)
        return

    # --- 2. Prepare Dictionary Pointer ---
    # The runtime routine needs to know which dictionary to operate on.
    resolved_dict_name = func_core.resolve_variable_name(dict_var_name, current_func_name)
    dict_info = variables.get(resolved_dict_name)
    if not dict_info or dict_info.get('type') != 'dict':
        report_error(f"Variable '{dict_var_name}' is not a dictionary.", call_node.lineno)
        return

    gen_code.append(f"; --- Preparing call to dict.{method_name} on '{resolved_dict_name}' ---")
    gen_code.append(f"lda #<{resolved_dict_name}")
    gen_code.append(f"ldx #>{resolved_dict_name}")
    gen_code.append(f"sta {ZP_DICT_PTR}")
    gen_code.append(f"stx {ZP_DICT_PTR}+1")

    # --- 3. Process and Pass Arguments ---
    arg_zp_locs = [ZP_ARG1_PTR, ZP_ARG2_PTR]
    temp_vars_to_release = []
    for i, arg_node in enumerate(args):
        if i >= len(arg_zp_locs):
            report_error(f"Internal Compiler Error: Too many arguments for dict method handler.", call_node.lineno)
            break

        temp_arg_var = func_core.get_temp_var() # Use size 4 to accommodate any type
        temp_vars_to_release.append(temp_arg_var)
        func_expressions.translate_expression_recursive(temp_arg_var, arg_node, current_func_name)

        # Pass a pointer to the *variable* that holds the argument's value
        zp_loc = arg_zp_locs[i]
        gen_code.append(f"lda #<{temp_arg_var}")
        gen_code.append(f"ldx #>{temp_arg_var}")
        gen_code.append(f"sta {zp_loc}")
        gen_code.append(f"stx {zp_loc}+1")

    # --- 4. Call the Routine ---
    routine_name = spec['routine']
    gen_code.append(f"jsr {routine_name}")
    used_routines.add(routine_name)

    # --- 5. Handle Return Value ---
    if target_var_name:
        resolved_target_name = func_core.resolve_variable_name(target_var_name, current_func_name)
        return_spec = spec.get('return', {})
        return_type = return_spec.get('type', 'any')

        # The result of dict operations is typically a pointer in AX
        # (e.g., to a value, or to a new list object).
        # For 'any', we can't know the size, but for pointers to other structures (like lists from .keys()) it's a 2-byte pointer.
        size = 2 if return_type == 'pointer' else 4 # Default to larger size for 'any'
        func_core.handle_variable(resolved_target_name, size=size, var_type=return_type)
        func_core.store_ax_in_var(resolved_target_name)

    # --- 6. Cleanup ---
    for temp_var in temp_vars_to_release:
        func_core.release_temp_var(temp_var)
    gen_code.append(f"; --- End call to dict.{method_name} ---")


def handle_dict_method_call(call_node, current_func_info=None):
    """
    Handles a standalone dictionary method call (e.g., my_dict.clear()).
    Returns True if the call was handled, False otherwise.
    """
    if not isinstance(call_node.func, ast.Attribute) or not isinstance(call_node.func.value, ast.Name):
        return False

    method_name = call_node.func.attr
    spec = DICT_METHOD_SPECS.get(method_name)
    if not spec:
        return False # Not a recognized dictionary method

    dict_var_name = call_node.func.value.id
    _process_dict_method_call(call_node, spec, dict_var_name, current_func_info, target_var_name=None)
    return True

def handle_dict_assignment(assign_node, current_func_info=None):
    """
    Handles an assignment from a dictionary method call (e.g., x = my_dict.get('key')).
    Returns True if the assignment was handled, False otherwise.
    """
    if not isinstance(assign_node.value, ast.Call):
        return False
    
    call_node = assign_node.value
    if not isinstance(call_node.func, ast.Attribute) or not isinstance(call_node.func.value, ast.Name):
        return False

    method_name = call_node.func.attr
    spec = DICT_METHOD_SPECS.get(method_name)
    if not spec or 'return' not in spec or spec['return'] is None:
        return False # Not a method that returns a value

    if len(assign_node.targets) != 1 or not isinstance(assign_node.targets[0], ast.Name):
        report_error(f"Assignment from 'dict.{method_name}' must be to a single variable.", assign_node.lineno)
        return True # We've handled it by reporting an error

    dict_var_name = call_node.func.value.id
    target_var_name = assign_node.targets[0].id
    _process_dict_method_call(call_node, spec, dict_var_name, current_func_info, target_var_name)
    return True

def process_dict_literal(dict_node, target_var_name, current_func_info):
    """
    Processes a dictionary literal e.g. my_dict = {'a': 1, 'b': 2}
    This is a placeholder for future implementation.
    """
    report_error("Dictionary literals are not yet supported.", dict_node.lineno)
    # In the future, this would:
    # 1. Call a runtime routine to initialize an empty dictionary structure.
    # 2. For each key-value pair, call a 'dict_set_value' routine.
    # 3. Store the pointer to the new dictionary in target_var_name.
    pass