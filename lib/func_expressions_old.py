# func_expressions.py
# Functions for handling expressions and binary operations.

import ast
from .. import globals as _globals
from .func_core import (
    type_value, handle_variable, get_temp_var, release_temp_var, 
    create_label, _copy_variable_content
)
from .func_core import (
    _generate_int_to_float_conversion, _generate_float_to_int_conversion,
    _generate_load_float_to_fp1, _generate_load_float_to_fp2, 
    _generate_store_float_from_fp1, _generate_copy_2_bytes
)

# Alias per accesso più breve
gen_code = _globals.generated_code
variables = _globals.variables
used_routines = _globals.used_routines
report_error = _globals.report_compiler_error


def _handle_binop_multiply_16bit(left_op, right_op, target):
    """Handles 16-bit multiplication."""
    mul_vars = ['m16_arg1_l', 'm16_arg1_h', 'm16_arg2_l', 'm16_arg2_h',
                'm16_res_l', 'm16_res_h', 'm16_p0_l', 'm16_p0_h',
                'm16_term2', 'm16_term3', 'm16_mul8_val1', 'm16_mul8_val2']
    
    for var in mul_vars:
        handle_variable(var)

    gen_code.extend([
        f"    LDA {left_op}",
        f"    STA m16_arg1_l",
        f"    LDA {left_op}+1",
        f"    STA m16_arg1_h",
        f"    LDA {right_op}",
        f"    STA m16_arg2_l",
        f"    LDA {right_op}+1",
        f"    STA m16_arg2_h",
        f"    JSR multiply16x16_16",
        f"    LDA m16_res_l",
        f"    STA {target}",
        f"    LDA m16_res_h",
        f"    STA {target}+1"
    ])
    used_routines.add('multiply16x16_16')


def _handle_binop_divide_16bit(left_op, right_op, target):
    """Handles 16-bit integer division."""
    div_vars = ['d16_orig_dividend_l', 'd16_orig_dividend_h', 'd16_divisor_l', 'd16_divisor_h',
                'd16_quotient_l', 'd16_quotient_h', 'd16_rem_l', 'd16_rem_h']
    
    for var in div_vars:
        handle_variable(var)

    gen_code.extend([
        f"    LDA {left_op}",
        f"    STA d16_orig_dividend_l",
        f"    LDA {left_op}+1",
        f"    STA d16_orig_dividend_h",
        f"    LDA {right_op}",
        f"    STA d16_divisor_l",
        f"    LDA {right_op}+1",
        f"    STA d16_divisor_h",
        f"    JSR divide16x16_16",
        f"    LDA d16_quotient_l",
        f"    STA {target}",
        f"    LDA d16_quotient_h",
        f"    STA {target}+1"
    ])
    used_routines.add('divide16x16_16')


def _handle_integer_operation(left_op, right_op, target, operator):
    """Handle integer arithmetic operations."""
    if operator == "add":
        gen_code.extend([
            f"    LDA {left_op}",
            "    CLC",
            f"    ADC {right_op}",
            f"    STA {target}",
            f"    LDA {left_op}+1",
            f"    ADC {right_op}+1",
            "    JSR check_overflow",
            f"    STA {target}+1"
        ])
        used_routines.add('check_overflow')
    
    elif operator == "sub":
        gen_code.extend([
            f"    LDA {left_op}",
            "    SEC",
            f"    SBC {right_op}",
            f"    STA {target}",
            f"    LDA {left_op}+1",
            f"    SBC {right_op}+1",
            "    JSR check_overflow",
            f"    STA {target}+1"
        ])
        used_routines.add('check_overflow')
    
    elif operator == "mult":
        _handle_binop_multiply_16bit(left_op, right_op, target)
    
    elif operator == "div":
        _handle_binop_divide_16bit(left_op, right_op, target)
    
    elif operator == "xor":
        gen_code.extend([
            f"    LDA {left_op}",
            f"    EOR {right_op}",
            f"    STA {target}",
            f"    LDA {left_op}+1",
            f"    EOR {right_op}+1",
            f"    STA {target}+1"
        ])


def _handle_float_operation(left_op, right_op, target, operator):
    """Handle floating-point arithmetic operations."""
    fp_ops = {
        "add": ("FP_FADD", _generate_load_float_to_fp1, _generate_load_float_to_fp2),
        "sub": ("FP_FSUB", _generate_load_float_to_fp1, _generate_load_float_to_fp2),
        "mult": ("FP_FMUL", _generate_load_float_to_fp1, _generate_load_float_to_fp2),
        "div": ("FP_FDIV", _generate_load_float_to_fp2, _generate_load_float_to_fp1)  # Note: order reversed for div
    }
    
    if operator not in fp_ops:
        report_error(f"Floating point operator '{operator}' not supported.", level="ERROR")
        return
    
    routine, load_func1, load_func2 = fp_ops[operator]
    
    gen_code.extend(load_func1(left_op))
    gen_code.extend(load_func2(right_op))
    gen_code.append(f"    JSR {routine}")
    gen_code.extend(_generate_store_float_from_fp1(target))
    used_routines.add(routine)


def binop_handler(left_operand_name, op, right_operand_name, target_variable_name):
    """Handles binary operations (add, sub, mult, div)."""
    # Determine operation type
    left_is_float = variables.get(left_operand_name, {}).get('is_float', False)
    right_is_float = variables.get(right_operand_name, {}).get('is_float', False)
    is_fp_op = left_is_float or right_is_float

    # Map operators
    op_map = {
        ast.Add: "add",
        ast.Sub: "sub", 
        ast.Mult: "mult",
        ast.FloorDiv: "div",
        ast.BitXor: "xor"
    }
    
    operator = op_map.get(type(op))
    if not operator:
        report_error(f"Operator {type(op).__name__} not supported.", node=op, level="ERROR")
        return

    # Ensure target variable is properly configured
    handle_variable(target_variable_name)
    if is_fp_op:
        variables[target_variable_name].update({
            'is_float': True,
            'size': 4,
            'is_8bit_semantic': False
        })
        
        # Validate float operands
        if not (left_is_float and right_is_float):
            report_error(
                f"Internal Error: binop_handler called for FP op but operands not both float.",
                level="ERROR"
            )
            return
        
        _handle_float_operation(left_operand_name, right_operand_name, target_variable_name, operator)
    else:
        _handle_integer_operation(left_operand_name, right_operand_name, target_variable_name, operator)


def _generate_comparison_labels():
    """Generate unique labels for comparison operations."""
    true_label = create_label("cmp_true", str(_globals.label_counter))
    end_label = create_label("cmp_end", str(_globals.label_counter))
    _globals.label_counter += 1
    return true_label, end_label


def _handle_float_comparison(left_op, right_op, op, true_label):
    """Handle floating-point comparisons."""
    gen_code.extend(_generate_load_float_to_fp1(left_op))
    gen_code.extend(_generate_load_float_to_fp2(right_op))
    
    comp_ops = {
        ast.Eq: ("BEQ", "FP_EQ"),
        ast.NotEq: ("BNE", "FP_NE"),
        ast.Lt: ("BCC", "FP_LT"),
        ast.LtE: ("BCS", "FP_GE"),  # Negated logic
        ast.Gt: ("BCC", "FP_LT"),   # Swap operands
        ast.GtE: ("BCS", "FP_GE")   # Swap operands
    }
    
    if isinstance(op, (ast.Gt, ast.GtE)):
        # Swap operands for > and >=
        gen_code.extend(_generate_load_float_to_fp1(right_op))
        gen_code.extend(_generate_load_float_to_fp2(left_op))
    
    gen_code.append("    JSR FP_FCMP")
    used_routines.add('FP_FCMP')
    
    branch_op, flag = comp_ops.get(type(op), ("BEQ", "FP_EQ"))
    gen_code.extend([
        f"    {branch_op} {flag}",
        f"    JMP {true_label}"
    ])


def _handle_integer_comparison(left_op, right_op, op, true_label, end_label):
    """Handle integer comparisons."""
    gen_code.extend([
        f"    LDA {left_op}",
        f"    CMP {right_op}"
    ])
    
    # Simplified comparison logic - can be expanded based on specific needs
    if isinstance(op, ast.Eq):
        gen_code.extend([
            f"    BNE {true_label}",
            f"    LDA {left_op}+1",
            f"    CMP {right_op}+1",
            f"    BNE {true_label}"
        ])
    elif isinstance(op, ast.NotEq):
        gen_code.extend([
            f"    BNE {end_label}_set_true",
            f"    LDA {left_op}+1",
            f"    CMP {right_op}+1",
            f"    BNE {end_label}_set_true",
            f"    JMP {true_label}",
            f"{end_label}_set_true:"
        ])
    # Add other comparison operators as needed...


def handle_comparison(target_var_name, node, current_func_name):
    """Handles an ast.Compare node."""
    if len(node.ops) > 1 or len(node.comparators) > 1:
        report_error("Chained comparisons not supported.", node=node)
        return

    op = node.ops[0]
    left_op_name = get_value(node.left, current_func_name)
    right_op_name = get_value(node.comparators[0], current_func_name)

    # Type coercion and comparison setup
    left_type = variables.get(left_op_name, {}).get('type', 'int')
    right_type = variables.get(right_op_name, {}).get('type', 'int')
    is_float_comparison = left_type == 'float' or right_type == 'float'

    # Handle type coercion if needed
    coerced_temps = []
    if is_float_comparison:
        if left_type == 'int':
            coerced_left = get_temp_var()
            _generate_int_to_float_conversion(left_op_name, coerced_left)
            left_op_name = coerced_left
            coerced_temps.append(coerced_left)
        if right_type == 'int':
            coerced_right = get_temp_var()
            _generate_int_to_float_conversion(right_op_name, coerced_right)
            right_op_name = coerced_right
            coerced_temps.append(coerced_right)

    # Generate comparison code
    true_label, end_label = _generate_comparison_labels()
    
    if is_float_comparison:
        _handle_float_comparison(left_op_name, right_op_name, op, true_label)
    else:
        _handle_integer_comparison(left_op_name, right_op_name, op, true_label, end_label)

    # Store result
    gen_code.extend([
        f"    LDA #0",
        f"    JMP {end_label}",
        f"{true_label}:",
        f"    LDA #1",
        f"{end_label}:",
        f"    STA {target_var_name}",
        f"    LDA #0",
        f"    STA {target_var_name}+1"
    ])

    # Cleanup
    for temp in coerced_temps:
        release_temp_var(temp)


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
            # Integer abs logic (simplified)
            _handle_integer_abs(temp_arg, var_name)
        
        release_temp_var(temp_arg)
        return True
    
    # Add more built-in functions as needed
    return False


def _handle_integer_abs(source, target):
    """Handle integer absolute value."""
    pos_label = create_label("abs_pos", str(_globals.label_counter))
    done_label = create_label("abs_done", str(_globals.label_counter))
    _globals.label_counter += 1
    
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


def translate_expression(var_name, node, current_func_name=None):
    """Translate a BinOp expression to assembly code."""
    handle_variable('temp_0')  # Used by error routines
    
    op = node.value.op
    left = node.value.left
    right = node.value.right

    # Resolve operands
    left_id = _resolve_operand(left, current_func_name)
    right_id = _resolve_operand(right, current_func_name)
    
    # Track temporary variables for cleanup
    temp_vars = []
    if isinstance(left, (ast.Constant, ast.BinOp)):
        temp_vars.append(left_id)
    if isinstance(right, (ast.Constant, ast.BinOp)):
        temp_vars.append(right_id)

    # Handle type coercion
    left_id, right_id, coerced_temps = _handle_type_coercion(left_id, right_id)
    temp_vars.extend(coerced_temps)

    # Perform operation
    binop_handler(left_id, op, right_id, var_name)

    # Cleanup
    for temp in temp_vars:
        release_temp_var(temp)


def _resolve_operand(operand, current_func_name):
    """Resolve an operand to a variable name."""
    if isinstance(operand, ast.Constant):
        temp_var = get_temp_var()
        type_value(temp_var, operand)
        return temp_var
    elif isinstance(operand, ast.Name):
        resolved = operand.id
        if current_func_name:
            mangled = f"__{current_func_name}_{operand.id}"
            if mangled in variables:
                resolved = mangled
        return resolved
    else:  # ast.BinOp or other complex expression
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
            # Convert right to float
            coerced_right = get_temp_var()
            handle_variable(coerced_right, size=4, var_type='float')
            _generate_int_to_float_conversion(right_id, coerced_right)
            right_id = coerced_right
            coerced_temps.append(coerced_right)
        elif not left_is_float and right_is_float:
            # Convert left to float
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
        resolved = node.id
        if current_func_name:
            mangled = f"__{current_func_name}_{node.id}"
            if mangled in variables:
                resolved = mangled
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
        # Try constant folding first
        folded = _perform_constant_folding(node)
        if folded:
            type_value(var_name, folded)
            return
        
        # Regular expression translation
        fake_assign = ast.Assign(
            targets=[ast.Name(id=var_name, ctx=ast.Store())], 
            value=node
        )
        translate_expression(var_name, fake_assign, current_func_name)
    
    elif isinstance(node, ast.Constant):
        type_value(var_name, node)
    
    elif isinstance(node, ast.Name):
        source_var = node.id
        if current_func_name:
            mangled = f"__{current_func_name}_{source_var}"
            if mangled in variables:
                source_var = mangled
        _copy_variable_content(source_var, var_name, current_func_name)
    
    elif isinstance(node, ast.Call):
        _handle_function_call_in_expression(var_name, node, current_func_name)
    
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
    
    # Try built-in functions first
    if _handle_builtin_functions(func_name, node.args, var_name, current_func_name):
        return
    
    # Handle user-defined functions
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
    
    # Evaluate arguments
    for i, arg_node in enumerate(args):
        arg_holder = f"__func_arg_{i}"
        handle_variable(arg_holder)
        translate_expression_recursive(arg_holder, arg_node, current_func_name)
    
    # Call function
    gen_code.append(f"    JSR {func_info['label']}")
    
    # Handle return value
    return_type = func_info.get('return_type', 'int')
    handle_variable(var_name, size=4 if return_type == 'float' else 2, var_type=return_type)
    
    if return_type == 'float':
        gen_code.extend(_generate_store_float_from_fp1(var_name))
    else:
        gen_code.extend([
            f"    STX {var_name}",      # LSB
            f"    STA {var_name}+1"     # MSB
        ])