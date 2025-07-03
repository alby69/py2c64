# func_expressions.py
# Functions for parsing expression structures from the AST.
# This module handles the high-level logic of expression translation,
# including recursion, function calls, and constant folding.

import ast # pyright: ignore[reportMissingModuleSource]
from .. import globals as py2asm_globals
from .func_core import (
    type_value, handle_variable, get_temp_var, release_temp_var, 
    create_label, _copy_variable_content, _generate_int_to_float_conversion,
    _generate_store_float_from_fp1, _generate_load_float_to_fp1
)
# Import low-level operation handlers
from .func_operations import binop_handler, handle_comparison

# Alias per accesso più breve
gen_code = py2asm_globals.generated_code
variables = py2asm_globals.variables
used_routines = py2asm_globals.used_routines
report_error = py2asm_globals.report_compiler_error


def get_value(node, current_func_name=None):
    """
    Resolves a node to a variable name or evaluates it into a temporary variable.
    Returns the name of the variable holding the result.
    """
    if isinstance(node, ast.Constant):
        temp_var = get_temp_var()
        type_value(temp_var, node)
        return temp_var
    elif isinstance(node, ast.Name):
        resolved = node.id
        if current_func_name:
            mangled = f"__{current_func_name}_{node.id}"
            if mangled in variables:
                resolved = mangled
        if resolved not in variables:
            report_error(f"Variable '{node.id}' not defined.", node=node)
            return None # Should handle this error case
        return resolved
    elif isinstance(node, (ast.BinOp, ast.Compare, ast.Call)):
        temp_var = get_temp_var()
        translate_expression_recursive(temp_var, node, current_func_name)
        return temp_var
    else:
        report_error(f"Node type {type(node).__name__} not resolvable to a value.", node=node)
        return None


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


def _handle_integer_abs(source, target):
    """Handle integer absolute value."""
    pos_label = create_label("abs_pos")
    done_label = create_label("abs_done")
    
    gen_code.extend([
        f"    LDA {source}+1",
        f"    BPL {pos_label}",
        # Negative: two's complement
        f"    LDA {source}",
        f"    EOR #$FF",
        f"    STA {target}",
        f"    LDA {source}+1",
        f"    EOR #$FF",
        f"    STA {target}+1",
        f"    LDA {target}",
        f"    CLC",
        f"    ADC #1",
        f"    STA {target}",
        f"    LDA {target}+1",
        f"    ADC #0",
        f"    STA {target}+1",
        f"    JMP {done_label}",
        f"{pos_label}:",
        f"    LDA {source}",
        f"    STA {target}",
        f"    LDA {source}+1",
        f"    STA {target}+1",
        f"{done_label}:"
    ])


def _handle_builtin_functions(func_name, args, target_var, current_func_name):
    """Handle built-in function calls in expressions."""
    if func_name == 'float' and len(args) == 1:
        arg_var = get_value(args[0], current_func_name)
        handle_variable(target_var, size=4, var_type='float')
        _generate_int_to_float_conversion(arg_var, target_var)
        release_temp_var(arg_var) # if it was a temporary
        return True
    
    elif func_name == 'int' and len(args) == 1:
        # Note: This simplifies float-to-int conversion.
        arg_var = get_value(args[0], current_func_name)
        handle_variable(target_var, size=2, var_type='int')
        _copy_variable_content(arg_var, target_var, is_8bit_source=False, size=2)
        release_temp_var(arg_var) # if it was a temporary
        return True
    
    elif func_name == 'abs' and len(args) == 1:
        arg_var = get_value(args[0], current_func_name)
        handle_variable(target_var)
        
        if variables.get(arg_var, {}).get('is_float', False):
            variables[target_var].update({'is_float': True, 'size': 4})
            gen_code.extend(_generate_load_float_to_fp1(arg_var))
            gen_code.append("    JSR FP_ABS")
            gen_code.extend(_generate_store_float_from_fp1(target_var))
            used_routines.add('FP_ABS')
        else:
            _handle_integer_abs(arg_var, target_var)
        
        release_temp_var(arg_var) # if it was a temporary
        return True
    
    return False


def _handle_user_function_call(target_var, func_name, args, current_func_name):
    """Handle user-defined function calls."""
    func_info = py2asm_globals.defined_functions[func_name]
    expected_params = len(func_info.get('params', []))
    
    if len(args) != expected_params:
        report_error(f"Function '{func_name}' expects {expected_params} args, got {len(args)}", level="ERROR")
        type_value(target_var, ast.Constant(value=0))
        return

    # Evaluate and store arguments in temporary locations
    arg_vars = []
    for arg_node in args:
        arg_var = get_value(arg_node, current_func_name)
        arg_vars.append(arg_var)

    # TODO: Push arguments to the stack or designated parameter variables
    # This is a simplified placeholder.
    for i, arg_var in enumerate(arg_vars):
        param_name = f"__param_{func_name}_{i}"
        handle_variable(param_name)
        _copy_variable_content(arg_var, param_name, is_8bit_source=False, size=4) # Assume worst case (float)

    # Call function
    gen_code.append(f"    JSR {func_info['label']}")
    
    # Handle return value
    return_type = func_info.get('return_type', 'int')
    handle_variable(target_var, size=4 if return_type == 'float' else 2, var_type=return_type)
    
    if return_type == 'float':
        gen_code.extend(_generate_store_float_from_fp1(target_var))
    else:
        # Standard return convention: MSB in A, LSB in X
        gen_code.extend([
            f"    STX {target_var}",      # LSB
            f"    STA {target_var}+1"     # MSB
        ])

    # Clean up temporary argument variables
    for var in arg_vars:
        if var.startswith("_temp_"):
             release_temp_var(var)


def _handle_function_call_in_expression(target_var, node, current_func_name):
    """Handle function calls within expressions."""
    if not isinstance(node.func, ast.Name):
        report_error("Dynamic function calls are not supported.", node=node)
        type_value(target_var, ast.Constant(value=0))
        return
    
    func_name = node.func.id
    
    # Try built-in functions first
    if _handle_builtin_functions(func_name, node.args, target_var, current_func_name):
        return
    
    # Handle user-defined functions
    if func_name in py2asm_globals.defined_functions:
        _handle_user_function_call(target_var, func_name, node.args, current_func_name)
    else:
        report_error(f"Unknown function '{func_name}' called.", node=node)
        type_value(target_var, ast.Constant(value=0))


def translate_expression_recursive(target_var, node, current_func_name=None):
    """
    Recursively translates an AST expression node and stores the result in target_var.
    """
    if isinstance(node, ast.BinOp):
        folded = _perform_constant_folding(node)
        if folded:
            type_value(target_var, folded)
            return

        left_op_name = get_value(node.left, current_func_name)
        right_op_name = get_value(node.right, current_func_name)
        
        binop_handler(left_op_name, node.op, right_op_name, target_var)
        
        # Release temporary variables used for operands
        if left_op_name and left_op_name.startswith("_temp_"):
            release_temp_var(left_op_name)
        if right_op_name and right_op_name.startswith("_temp_"):
            release_temp_var(right_op_name)
    
    elif isinstance(node, ast.Compare):
        left_op_name = get_value(node.left, current_func_name)
        # Note: only handles single comparators for now
        right_op_name = get_value(node.comparators[0], current_func_name)
        op = node.ops[0]
        
        handle_comparison(left_op_name, op, right_op_name, target_var)

        if left_op_name and left_op_name.startswith("_temp_"):
            release_temp_var(left_op_name)
        if right_op_name and right_op_name.startswith("_temp_"):
            release_temp_var(right_op_name)

    elif isinstance(node, ast.Constant):
        type_value(target_var, node)
    
    elif isinstance(node, ast.Name):
        source_var = get_value(node, current_func_name)
        _copy_variable_content(source_var, target_var, current_func_name)
    
    elif isinstance(node, ast.Call):
        _handle_function_call_in_expression(target_var, node, current_func_name)
    
    else:
        report_error(f"Unsupported node type in expression: {type(node).__name__}", node=node)
        type_value(target_var, ast.Constant(value=0))