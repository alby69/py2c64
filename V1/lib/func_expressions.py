# py2c64/lib/func_expressions.py
# Functions for handling expressions, constant folding, and function calls.

import ast
import V1.globals as _globals
from lib.func_core import (
    type_value, handle_variable, get_temp_var, release_temp_var,
    _generate_int_to_float_conversion, _generate_float_to_int_conversion,
    _generate_load_float_to_fp1, _generate_store_float_from_fp1, _copy_variable_content,
    resolve_variable_name
)
from lib.func_strings import join_str_value

# Aliases
gen_code = _globals.generated_code
variables = _globals.variables
used_routines = _globals.used_routines
report_error = _globals.report_compiler_error


def _perform_constant_folding(node):
    """Perform constant folding optimization."""
    if not (isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant)):
        return None
    
    try:
        left_val, right_val = node.left.value, node.right.value
        
        fold_ops = {
            ast.Add: lambda a, b: a + b,
            ast.Sub: lambda a, b: a - b,
            ast.Mult: lambda a, b: a * b,
            ast.Div: lambda a, b: a / b if b != 0 else None,
            ast.FloorDiv: lambda a, b: a // b if b != 0 else None,
            ast.Mod: lambda a, b: a % b if b != 0 else None,
            ast.Pow: lambda a, b: a ** b,
            ast.BitXor: lambda a, b: a ^ b,
            ast.BitAnd: lambda a, b: a & b,
            ast.BitOr: lambda a, b: a | b
        }
        
        op_func = fold_ops.get(type(node.op))
        if op_func:
            result = op_func(left_val, right_val)
            return ast.Constant(value=result) if result is not None else None
            
    except (ZeroDivisionError, Exception) as e:
        if isinstance(e, ZeroDivisionError):
            report_error(f"Compile-time division by zero", node=node, level="ERROR")
        else:
            report_error(f"Constant folding error: {e}", node=node, level="WARNING")
    
    return None


def _handle_builtin_functions(func_name, args, var_name, current_func_name):
    """Handle built-in function calls in expressions."""
    arg_count = len(args)
    
    if func_name == 'float' and arg_count == 1:
        temp_arg = get_temp_var()
        translate_expression_recursive(temp_arg, args[0], current_func_name)
        handle_variable(var_name, size=4, var_type='float')
        _generate_int_to_float_conversion(temp_arg, var_name)
        release_temp_var(temp_arg)
        return True
    
    elif func_name == 'int' and arg_count == 1:
        temp_arg = get_temp_var()
        translate_expression_recursive(temp_arg, args[0], current_func_name)
        handle_variable(var_name, size=2, var_type='int')
        _copy_variable_content(temp_arg, var_name, current_func_name)
        release_temp_var(temp_arg)
        return True
    
    elif func_name == 'abs' and arg_count == 1:
        temp_arg = get_temp_var()
        translate_expression_recursive(temp_arg, args[0], current_func_name)
        handle_variable(var_name)
        
        if variables.get(temp_arg, {}).get('is_float', False):
            variables[var_name].update({'is_float': True, 'size': 4})
            gen_code.extend(_generate_load_float_to_fp1(temp_arg))
            gen_code.append("    JSR FP_ABS")
            gen_code.extend(_generate_store_float_from_fp1(var_name))
            used_routines.add('FP_ABS')
        else:
            # Import to avoid circular dependency
            from .func_operations import _handle_integer_abs
            _handle_integer_abs(temp_arg, var_name)
        
        release_temp_var(temp_arg)
        return True
    
    return False


def translate_expression(var_name, node, current_func_name=None):
    """Translate a BinOp expression to assembly code."""
    handle_variable('temp_0')
    
    op = node.value.op
    left = node.value.left
    right = node.value.right

    left_id = _resolve_operand(left, current_func_name)
    right_id = _resolve_operand(right, current_func_name)
    
    temp_vars = []
    if isinstance(left, (ast.Constant, ast.BinOp)):
        temp_vars.append(left_id)
    if isinstance(right, (ast.Constant, ast.BinOp)):
        temp_vars.append(right_id)

    left_id, right_id, coerced_temps = _handle_type_coercion(left_id, right_id)
    temp_vars.extend(coerced_temps)

    # Import to avoid circular dependency
    from .func_operations import binop_handler
    binop_handler(left_id, op, right_id, var_name)

    for temp in temp_vars:
        release_temp_var(temp)


def _resolve_operand(operand, current_func_name):
    """Resolve an operand to a variable name."""
    if isinstance(operand, ast.Constant):
        temp_var = get_temp_var()
        type_value(temp_var, operand)
        return temp_var
    elif isinstance(operand, ast.Name):
        resolved = resolve_variable_name(operand.id, current_func_name)
        return resolved
    else:
        temp_var = get_temp_var()
        translate_expression_recursive(temp_var, operand, current_func_name)
        return temp_var


def _handle_type_coercion(left_id, right_id):
    """Handle type coercion between operands."""
    left_is_float = variables.get(left_id, {}).get('is_float', False)
    right_is_float = variables.get(right_id, {}).get('is_float', False)
    
    coerced_temps = []
    
    if left_is_float != right_is_float:
        if left_is_float and not right_is_float:
            coerced_right = get_temp_var()
            handle_variable(coerced_right, size=4, var_type='float')
            _generate_int_to_float_conversion(right_id, coerced_right)
            right_id = coerced_right
            coerced_temps.append(coerced_right)
        elif not left_is_float and right_is_float:
            coerced_left = get_temp_var()
            handle_variable(coerced_left, size=4, var_type='float')
            _generate_int_to_float_conversion(left_id, coerced_left)
            left_id = coerced_left
            coerced_temps.append(coerced_left)
    
    return left_id, right_id, coerced_temps


def get_value(node, current_func_name=None):
    """Get the value or variable name of a node."""
    if isinstance(node, ast.Constant):
        temp_var = get_temp_var()
        type_value(temp_var, node)
        return temp_var
    elif isinstance(node, ast.Name):
        resolved = resolve_variable_name(node.id, current_func_name)
        return resolved if resolved in variables else None
    elif isinstance(node, ast.BinOp):
        temp_var = get_temp_var()
        translate_expression_recursive(temp_var, node, current_func_name)
        return temp_var
    else:
        report_error(f"Node type {type(node).__name__} not resolvable", node=node)
        return None


def translate_expression_recursive(var_name, node, current_func_name=None):
    """Recursive function for handling expressions."""
    if isinstance(node, ast.BinOp):
        folded = _perform_constant_folding(node)
        if folded:
            type_value(var_name, folded)
            return
        
        fake_assign = ast.Assign(
            targets=[ast.Name(id=var_name, ctx=ast.Store())], 
            value=node
        )
        translate_expression(var_name, fake_assign, current_func_name)
    
    elif isinstance(node, ast.Constant):
        type_value(var_name, node)
    
    elif isinstance(node, ast.Name):
        source_var = resolve_variable_name(node.id, current_func_name)
        _copy_variable_content(source_var, var_name, current_func_name)
    
    elif isinstance(node, ast.Call):
        _handle_function_call_in_expression(var_name, node, current_func_name)
    
    elif isinstance(node, ast.JoinedStr):
        join_str_value(var_name, node)

    elif isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.USub):
            # Implement -x as 0 - x
            zero_node = ast.Constant(value=0)
            sub_node = ast.BinOp(left=zero_node, op=ast.Sub(), right=node.operand)
            # Now process this new BinOp node
            translate_expression_recursive(var_name, sub_node, current_func_name)
        else:
            report_error(f"Unsupported unary operator: {type(node.op).__name__}", node=node)
            type_value(var_name, ast.Constant(value=0))

    elif isinstance(node, ast.Compare):
        # Delegate comparison to a handler in func_operations
        # Import here to avoid circular dependency at module level
        from .func_operations import handle_comparison
        handle_comparison(var_name, node, current_func_name)

    else:
        report_error(f"Unsupported node type {type(node).__name__}", node=node)
        type_value(var_name, ast.Constant(value=0))


def _handle_function_call_in_expression(var_name, node, current_func_name):
    """Handle function calls within expressions."""
    if not isinstance(node.func, ast.Name):
        report_error("Only named function calls supported", node=node)
        type_value(var_name, ast.Constant(value=0))
        return
    
    func_name = node.func.id
    
    if _handle_builtin_functions(func_name, node.args, var_name, current_func_name):
        return
    
    if func_name in _globals.defined_functions:
        _handle_user_function_call(var_name, func_name, node.args, current_func_name)
    else:
        report_error(f"Unknown function '{func_name}'", node=node)
        type_value(var_name, ast.Constant(value=0))


def _handle_user_function_call(var_name, func_name, args, current_func_name):
    """Handle user-defined function calls."""
    func_info = _globals.defined_functions[func_name]
    expected_params = len(func_info.get('params', []))
    
    if len(args) != expected_params:
        report_error(f"Function '{func_name}' expects {expected_params} args, got {len(args)}", level="ERROR")
        type_value(var_name, ast.Constant(value=0))
        return
    
    for i, arg_node in enumerate(args):
        arg_holder = f"__func_arg_{i}"
        handle_variable(arg_holder)
        translate_expression_recursive(arg_holder, arg_node, current_func_name)
    
    gen_code.append(f"    JSR {func_info['label']}")
    
    return_type = func_info.get('return_type', 'int')
    handle_variable(var_name, size=4 if return_type == 'float' else 2, var_type=return_type)
    
    if return_type == 'float':
        gen_code.extend(_generate_store_float_from_fp1(var_name))
    else:
        gen_code.extend([f"    STX {var_name}", f"    STA {var_name}+1"])