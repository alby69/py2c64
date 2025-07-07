# py2c64/lib/func_c64.py

from .. import globals
from . import func_core
from . import func_expressions
from .c64_function_specs import C64_FUNCTION_SPECS, C64_HARDWARE_ALIASES

# Aliases
gen_code = globals.generated_code
variables = globals.variables
used_routines = globals.used_routines
report_error = globals.report_compiler_error

def _get_spec(func_name):
    """
    Retrieves the function specification, resolving aliases.
    """
    if func_name in C64_HARDWARE_ALIASES:
        func_name = C64_HARDWARE_ALIASES[func_name]
    return C64_FUNCTION_SPECS.get(func_name)

def _process_c64_call(call_node, spec, current_func_info=None):
    """
    Shared logic to process arguments and generate the JSR for a C64 function call.
    """
    func_name = call_node.func.id
    params = spec.get('params', [])
    args = call_node.args

    if len(args) != len(params):
        report_error(f"Incorrect number of arguments for C64 function '{func_name}'. Expected {len(params)}, got {len(args)}.", call_node.lineno)
        return

    # Process arguments
    for arg_node, param_spec in zip(args, params):
        temp_var = func_core.get_temp_var(size=param_spec['size'])
        func_expressions.translate_expression_recursive(temp_var, arg_node, current_func_info.get('name') if current_func_info else None)

        if param_spec['store'] == 'ax':
            func_core.load_ax_from_var(temp_var)
        elif param_spec['store'] == 'a':
            func_core.load_a_from_var(temp_var)
        elif param_spec['store'] == 'x':
            func_core.load_x_from_var(temp_var)
        elif param_spec['store'] == 'y':
            func_core.load_y_from_var(temp_var)
        elif param_spec['store'] == 'zp':
            # Assumes the ZP address is specified in the spec
            zp_addr = param_spec['address']
            func_core.load_ax_from_var(temp_var)
            gen_code.add_code(f"sta ${zp_addr:02x}")
            if param_spec['size'] == 16:
                gen_code.add_code(f"stx ${zp_addr+1:02x}")
        
        func_core.release_temp_var(temp_var)

    # Call the routine
    routine_name = spec['routine']
    gen_code.add_code(f"jsr {routine_name}")
    used_routines.add(routine_name)

def handle_c64_call(call_node, current_func_info=None):
    """
    Handles a standalone call to a C64 hardware function (e.g., in an ast.Expr node).
    Returns True if the call was handled, False otherwise.
    """
    if not hasattr(call_node.func, 'id'):
        return False # Not a simple function call like name()

    func_name = call_node.func.id
    spec = _get_spec(func_name)

    if not spec:
        return False # Not a C64 hardware function

    _process_c64_call(call_node, spec, current_func_info)
    return True

def handle_c64_assignment(assign_node, current_func_info=None):
    """
    Handles an assignment from a C64 hardware function that returns a value.
    Returns True if the assignment was handled, False otherwise.
    """
    if not isinstance(assign_node.value, globals.ast.Call) or not hasattr(assign_node.value.func, 'id'):
        return False

    call_node = assign_node.value
    func_name = call_node.func.id
    spec = _get_spec(func_name)

    if not spec or 'return' not in spec:
        return False # Not a C64 function or doesn't return a value

    # Process the function call itself
    _process_c64_call(call_node, spec, current_func_info)

    # Handle the return value
    if len(assign_node.targets) != 1 or not isinstance(assign_node.targets[0], globals.ast.Name):
        report_error(f"Assignment from C64 function '{func_name}' must be to a single variable.", assign_node.lineno)
        return True

    target_var_name = assign_node.targets[0].id
    resolved_var_name = func_core.resolve_variable_name(target_var_name, current_func_info.get('name') if current_func_info else None)
    
    return_spec = spec['return']
    if return_spec['size'] == 8:
        if return_spec['reg'] == 'a':
            func_core.store_a_in_var(resolved_var_name)
        else:
            report_error(f"Unsupported 8-bit return register '{return_spec['reg']}' for C64 function '{func_name}'.", call_node.lineno)
    elif return_spec['size'] == 16:
        if return_spec['reg'] == 'ax':
            func_core.store_ax_in_var(resolved_var_name)
        else:
            report_error(f"Unsupported 16-bit return register '{return_spec['reg']}' for C64 function '{func_name}'.", call_node.lineno)
    
    return True
