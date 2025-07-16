# py2c64/lib/func_operations.py
# Functions for handling binary operations and arithmetic.

import ast
import V1.globals as _globals
from lib_old.func_core import (
    handle_variable, get_temp_var, release_temp_var, create_label,
    _generate_int_to_float_conversion, _generate_load_float_to_fp1,
    _generate_load_float_to_fp2, _generate_store_float_from_fp1
)

# Aliases
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
        f"    LDA {left_op}", f"    STA m16_arg1_l",
        f"    LDA {left_op}+1", f"    STA m16_arg1_h",
        f"    LDA {right_op}", f"    STA m16_arg2_l",
        f"    LDA {right_op}+1", f"    STA m16_arg2_h",
        f"    JSR multiply16x16_16",
        f"    LDA m16_res_l", f"    STA {target}",
        f"    LDA m16_res_h", f"    STA {target}+1"
    ])
    used_routines.add('multiply16x16_16')


def _handle_binop_divide_16bit(left_op, right_op, target):
    """Handles 16-bit integer division."""
    div_vars = ['d16_orig_dividend_l', 'd16_orig_dividend_h', 'd16_divisor_l', 'd16_divisor_h',
                'd16_quotient_l', 'd16_quotient_h', 'd16_rem_l', 'd16_rem_h']
    
    for var in div_vars:
        handle_variable(var)

    gen_code.extend([
        f"    LDA {left_op}", f"    STA d16_orig_dividend_l",
        f"    LDA {left_op}+1", f"    STA d16_orig_dividend_h",
        f"    LDA {right_op}", f"    STA d16_divisor_l",
        f"    LDA {right_op}+1", f"    STA d16_divisor_h",
        f"    JSR divide16x16_16",
        f"    LDA d16_quotient_l", f"    STA {target}",
        f"    LDA d16_quotient_h", f"    STA {target}+1"
    ])
    used_routines.add('divide16x16_16')


def _handle_integer_operation(left_op, right_op, target, operator):
    """Handle integer arithmetic operations."""
    ops = {
        "add": ([
            f"    LDA {left_op}", "    CLC", f"    ADC {right_op}", f"    STA {target}",
            f"    LDA {left_op}+1", f"    ADC {right_op}+1", "    JSR check_overflow", f"    STA {target}+1"
        ], 'check_overflow'),
        "sub": ([
            f"    LDA {left_op}", "    SEC", f"    SBC {right_op}", f"    STA {target}",
            f"    LDA {left_op}+1", f"    SBC {right_op}+1", "    JSR check_overflow", f"    STA {target}+1"
        ], 'check_overflow'),
        "xor": ([
            f"    LDA {left_op}", f"    EOR {right_op}", f"    STA {target}",
            f"    LDA {left_op}+1", f"    EOR {right_op}+1", f"    STA {target}+1"
        ], None)
    }
    
    if operator == "mult":
        _handle_binop_multiply_16bit(left_op, right_op, target)
    elif operator == "div":
        _handle_binop_divide_16bit(left_op, right_op, target)
    elif operator in ops:
        code, routine = ops[operator]
        gen_code.extend(code)
        if routine:
            used_routines.add(routine)


def _handle_float_operation(left_op, right_op, target, operator):
    """Handle floating-point arithmetic operations."""
    fp_ops = {
        "add": ("FP_FADD", _generate_load_float_to_fp1, _generate_load_float_to_fp2),
        "sub": ("FP_FSUB", _generate_load_float_to_fp1, _generate_load_float_to_fp2),
        "mult": ("FP_FMUL", _generate_load_float_to_fp1, _generate_load_float_to_fp2),
        "div": ("FP_FDIV", _generate_load_float_to_fp2, _generate_load_float_to_fp1)
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
    left_is_float = variables.get(left_operand_name, {}).get('is_float', False)
    right_is_float = variables.get(right_operand_name, {}).get('is_float', False)
    is_fp_op = left_is_float or right_is_float

    op_map = {
        ast.Add: "add", ast.Sub: "sub", ast.Mult: "mult",
        ast.FloorDiv: "div", ast.BitXor: "xor"
    }
    
    operator = op_map.get(type(op))
    if not operator:
        report_error(f"Operator {type(op).__name__} not supported.", node=op, level="ERROR")
        return

    handle_variable(target_variable_name)
    if is_fp_op:
        variables[target_variable_name].update({
            'is_float': True, 'size': 4, 'is_8bit_semantic': False
        })
        
        if not (left_is_float and right_is_float):
            report_error("Internal Error: binop_handler called for FP op but operands not both float.", level="ERROR")
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
        ast.Eq: ("BEQ", "FP_EQ"), ast.NotEq: ("BNE", "FP_NE"),
        ast.Lt: ("BCC", "FP_LT"), ast.LtE: ("BCS", "FP_GE"),
        ast.Gt: ("BCC", "FP_LT"), ast.GtE: ("BCS", "FP_GE")
    } # Added closing parenthesis
    
    if isinstance(op, (ast.Gt, ast.GtE)):
        gen_code.extend(_generate_load_float_to_fp1(right_op))
        gen_code.extend(_generate_load_float_to_fp2(left_op))
    
    gen_code.append("    JSR FP_FCMP")
    used_routines.add('FP_FCMP')
    used_routines.add('FP_FSUB') # FP_COMPARE calls FP_FSUB
    
    branch_op, flag = comp_ops.get(type(op), ("BEQ", "FP_EQ"))
    gen_code.extend([f"    {branch_op} {flag}", f"    JMP {true_label}"])


def _handle_integer_comparison(left_op, right_op, op, true_label, end_label):
    """Handle 16-bit signed integer comparisons using N and V flags."""
    # Perform 16-bit subtraction: left - right
    gen_code.extend([
        f"    SEC",  # Set carry for subtraction
        f"    LDA {left_op}",
        f"    SBC {right_op}",
        f"    STA temp_0",  # Store low byte difference (temporary)
        f"    LDA {left_op}+1",
        f"    SBC {right_op}+1"
    ])
    
    # Handle different comparison operators
    if isinstance(op, ast.Eq):  # ==
        gen_code.extend([
            f"    BNE {end_label}_false",  # High byte not equal -> false
            f"    LDA temp_0",
            f"    BNE {end_label}_false",  # Low byte not equal -> false
            f"    JMP {true_label}",  # Both equal -> true
            f"{end_label}_false:"
        ])
    elif isinstance(op, ast.NotEq):  # !=
        gen_code.extend([
            f"    BNE {true_label}",  # High byte not equal -> true
            f"    LDA temp_0",
            f"    BEQ {end_label}_false",  # Both bytes equal -> false
            f"    JMP {true_label}",  # Low byte not equal -> true
            f"{end_label}_false:"
        ])
    elif isinstance(op, ast.Lt):  # <
        # For signed: (N != V) indicates left < right
        gen_code.extend([
            f"    BVC no_overflow_{end_label}",
            f"    EOR #$80",  # Invert sign bit if overflow occurred
            f"no_overflow_{end_label}:",
            f"    BMI {true_label}"  # If negative after adjustment, left < right
        ])
    elif isinstance(op, ast.LtE):  # <=
        gen_code.extend([
            f"    BVC no_overflow_{end_label}",
            f"    EOR #$80",  # Invert sign bit if overflow occurred
            f"no_overflow_{end_label}:",
            f"    BMI {true_label}",  # Negative -> left < right
            f"    LDA temp_0",
            f"    ORA {left_op}+1",  # Check if both bytes are zero
            f"    BEQ {true_label}"  # Zero means equal -> true
        ])
    elif isinstance(op, ast.Gt):  # >
        # For signed: (N == V) and (Z == 0) indicates left > right
        gen_code.extend([
            f"    BEQ {end_label}_check_zero",  # Check if high byte equal
            f"    BVC no_overflow_{end_label}",
            f"    EOR #$80",  # Invert sign bit if overflow occurred
            f"no_overflow_{end_label}:",
            f"    BPL {true_label}",  # Positive after adjustment -> left > right
            f"    JMP {end_label}_done",
            f"{end_label}_check_zero:",
            f"    LDA temp_0",
            f"    BEQ {end_label}_done",  # Both zero -> not greater
            f"    JMP {true_label}",  # Low byte not zero -> greater
            f"{end_label}_done:"
        ])
    elif isinstance(op, ast.GtE):  # >=
        # For signed: (N == V) indicates left >= right
        gen_code.extend([
            f"    BVC no_overflow_{end_label}",
            f"    EOR #$80",  # Invert sign bit if overflow occurred
            f"no_overflow_{end_label}:",
            f"    BPL {true_label}"  # Positive after adjustment -> left >= right
        ])
    else:
        report_error(f"Unsupported integer comparison operator: {type(op).__name__}", level="ERROR")


def handle_comparison(target_var_name, node, current_func_name):
    """Handles an ast.Compare node with proper type coercion and flag-based comparisons."""
    if len(node.ops) > 1 or len(node.comparators) > 1:
        report_error("Chained comparisons not supported.", node=node)
        return

    op = node.ops[0]
    left_op_name = get_value(node.left, current_func_name)
    right_op_name = get_value(node.comparators[0], current_func_name)

    left_type = variables.get(left_op_name, {}).get('type', 'int')
    right_type = variables.get(right_op_name, {}).get('type', 'int')
    is_float_comparison = left_type == 'float' or right_type == 'float'

    coerced_temps = []
    if is_float_comparison:
        # Coerce integers to floats when necessary
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

    true_label, end_label = _generate_comparison_labels()
    
    if is_float_comparison:
        # Handle float comparisons using FP_COMPARE routine
        _handle_float_comparison(left_op_name, right_op_name, op, true_label)
    else:
        # Handle 16-bit signed integer comparisons
        _handle_integer_comparison(left_op_name, right_op_name, op, true_label, end_label)

    # Store boolean result (1 for True, 0 for False) in target variable
    gen_code.extend([
        f"    LDA #0",  # Default to False
        f"    JMP {end_label}",  # Jump to end
        f"{true_label}:",
        f"    LDA #1",  # Set to True if condition met
        f"{end_label}:",
        f"    STA {target_var_name}",  # Store LSB
        f"    LDA #0",
        f"    STA {target_var_name}+1"  # Clear MSB for 16-bit boolean
    ])

    # Release any temporary variables used for coercion
    for temp in coerced_temps:
        release_temp_var(temp)


def _handle_comparison_for_branching(left_op, right_op, op, true_branch_label, current_func_name, negate=False):
    """
    Handles a comparison for branching purposes. It generates the necessary
    assembly code to compare two values (int or float) and branch to a
    specified label if the comparison is true.

    Args:
        left_op (str): Variable name for the left operand.
        right_op (str): Variable name for the right operand.
        op (ast.cmpop): Comparison operator (e.g., ast.Eq, ast.Lt).
        true_branch_label (str): Label to jump to if the comparison is true.
        current_func_name (str, optional): Name of the current function, if any.
        negate (bool, optional): If True, negates the comparison result (for
                                 not ... conditions).
    """
    left_type = variables.get(left_op, {}).get('type', 'int')
    right_type = variables.get(right_op, {}).get('type', 'int')
    is_float_comparison = left_type == 'float' or right_type == 'float'

    # --- Integer Comparison ---
    if not is_float_comparison:
        branch_ops = {
            ast.Eq: "BEQ", ast.NotEq: "BNE",
            ast.Lt: "BLT", ast.LtE: "BLE",
            ast.Gt: "BGT", ast.GtE: "BGE"
        }
        branch_op = branch_ops.get(type(op))
        if not branch_op:
            report_error(f"Unsupported integer comparison operator: {type(op).__name__}", node=op)
            return
        if negate:
            # Invert the condition by using the opposite branch instruction
            branch_op = branch_op[0] + 'rev' # e.g. BEQ becomes BREV
        
        # Compare integers by subtracting right from left.
        # The Carry (C), Zero (Z), Negative (N), and Overflow (V) flags will be used.
        gen_code.extend([
            f"    LDA {left_op}",
            f"    SEC",      # Initialize carry for subtraction
            f"    SBC {right_op}",
            f"    STA temp_0",   # Store the LSB of the result (not used, but needed for carry in next operation)
            f"    LDA {left_op}+1",
            f"    SBC {right_op}+1"
        ])
        gen_code.append(f"    {branch_op} {true_branch_label}")


def _handle_integer_abs(source, target): # Note: This function isn't directly used in the diff but is provided for context.
    """Handle integer absolute value."""
    pos_label = create_label("abs_pos", str(_globals.label_counter))
    done_label = create_label("abs_done", str(_globals.label_counter))
    _globals.label_counter += 1
    
    gen_code.extend([
        f"    LDA {source}+1", f"    BPL {pos_label}",
        f"    LDA {source}", f"    EOR #$FF", f"    STA {target}",
        f"    LDA {source}+1", f"    EOR #$FF", f"    STA {target}+1",
        f"    LDA {target}", "    CLC", "    ADC #1", f"    STA {target}",
        f"    LDA {target}+1", "    ADC #0", f"    STA {target}+1",
        f"    JMP {done_label}", f"{pos_label}:",
        f"    LDA {source}", f"    STA {target}",
        f"    LDA {source}+1", f"    STA {target}+1", f"{done_label}:"
    ])


# Import from func_expressions to avoid circular imports
from .func_expressions import get_value
