# func_operations.py
# Low-level implementation for binary and comparison operations.
# This module generates specific assembly code for arithmetic (int/float)
# and comparisons.

import ast
from .. import globals as py2asm_globals
from .func_core import (
    handle_variable, get_temp_var, release_temp_var, create_label,
    _generate_int_to_float_conversion, _generate_load_float_to_fp1, 
    _generate_load_float_to_fp2, _generate_store_float_from_fp1
)

# Alias per accesso più breve
gen_code = py2asm_globals.generated_code
variables = py2asm_globals.variables
used_routines = py2asm_globals.used_routines
report_error = py2asm_globals.report_compiler_error


def _handle_binop_multiply_16bit(left_op, right_op, target):
    """Handles 16-bit multiplication."""
    # Ensure multiplication routine variables are declared
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
    # Ensure division routine variables are declared
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
        gen_code.extend([f"    LDA {left_op}", "    CLC", f"    ADC {right_op}", f"    STA {target}",
                         f"    LDA {left_op}+1", f"    ADC {right_op}+1", "    JSR check_overflow", f"    STA {target}+1"])
        used_routines.add('check_overflow')
    elif operator == "sub":
        gen_code.extend([f"    LDA {left_op}", "    SEC", f"    SBC {right_op}", f"    STA {target}",
                         f"    LDA {left_op}+1", f"    SBC {right_op}+1", "    JSR check_overflow", f"    STA {target}+1"])
        used_routines.add('check_overflow')
    elif operator == "mult":
        _handle_binop_multiply_16bit(left_op, right_op, target)
    elif operator == "div":
        _handle_binop_divide_16bit(left_op, right_op, target)
    elif operator == "xor":
        gen_code.extend([f"    LDA {left_op}", f"    EOR {right_op}", f"    STA {target}",
                         f"    LDA {left_op}+1", f"    EOR {right_op}+1", f"    STA {target}+1"])


def _handle_float_operation(left_op, right_op, target, operator):
    """Handle floating-point arithmetic operations."""
    fp_ops = {
        "add": "FP_FADD", "sub": "FP_FSUB", "mult": "FP_FMUL", "div": "FP_FDIV"
    }
    routine = fp_ops.get(operator)
    if not routine:
        report_error(f"Floating point operator '{operator}' not supported.", level="ERROR")
        return

    # For division, the operands must be swapped in the FP registers
    if operator == "div":
        gen_code.extend(_generate_load_float_to_fp2(left_op))
        gen_code.extend(_generate_load_float_to_fp1(right_op))
    else:
        gen_code.extend(_generate_load_float_to_fp1(left_op))
        gen_code.extend(_generate_load_float_to_fp2(right_op))

    gen_code.append(f"    JSR {routine}")
    gen_code.extend(_generate_store_float_from_fp1(target))
    used_routines.add(routine)


def binop_handler(left_op_name, op, right_op_name, target_variable_name):
    """Handles binary operations (add, sub, mult, div, xor)."""
    left_is_float = variables.get(left_op_name, {}).get('is_float', False)
    right_is_float = variables.get(right_op_name, {}).get('is_float', False)
    is_fp_op = left_is_float or right_is_float

    op_map = {ast.Add: "add", ast.Sub: "sub", ast.Mult: "mult", ast.FloorDiv: "div", ast.BitXor: "xor"}
    operator = op_map.get(type(op))
    if not operator:
        report_error(f"Operator {type(op).__name__} not supported.", node=op, level="ERROR")
        return

    # Handle type coercion: if one operand is float, convert the other.
    coerced_temps = []
    if is_fp_op and not (left_is_float and right_is_float):
        if not left_is_float:
            coerced_left = get_temp_var()
            _generate_int_to_float_conversion(left_op_name, coerced_left)
            left_op_name = coerced_left
            coerced_temps.append(coerced_left)
        else: # right is not float
            coerced_right = get_temp_var()
            _generate_int_to_float_conversion(right_op_name, coerced_right)
            right_op_name = coerced_right
            coerced_temps.append(coerced_right)

    # Ensure target variable is properly configured
    handle_variable(target_variable_name)
    if is_fp_op:
        variables[target_variable_name].update({'is_float': True, 'size': 4, 'is_8bit_semantic': False})
        _handle_float_operation(left_op_name, right_op_name, target_variable_name, operator)
    else:
        variables[target_variable_name].update({'is_float': False, 'size': 2, 'is_8bit_semantic': False})
        _handle_integer_operation(left_op_name, right_op_name, target_variable_name, operator)

    # Clean up temporary variables created for coercion
    for temp in coerced_temps:
        release_temp_var(temp)


def _handle_float_comparison(left_op, right_op, op, true_label, end_label):
    """Handle floating-point comparisons."""
    # For > and >=, we swap operands and use < and <= logic
    if isinstance(op, (ast.Gt, ast.GtE)):
        left_op, right_op = right_op, left_op
        op = ast.Lt() if isinstance(op, ast.Gt) else ast.LtE()

    gen_code.extend(_generate_load_float_to_fp1(left_op))
    gen_code.extend(_generate_load_float_to_fp2(right_op))
    gen_code.append("    JSR FP_FCMP")
    used_routines.add('FP_FCMP')

    # Logic based on 6502 flags after FP_FCMP
    # N=1 if fp1<fp2, Z=1 if fp1=fp2, C=1 if fp1>=fp2
    if isinstance(op, ast.Eq):
        gen_code.append(f"    BEQ {true_label}") # Branch if Z=1
    elif isinstance(op, ast.NotEq):
        gen_code.append(f"    BNE {true_label}") # Branch if Z=0
    elif isinstance(op, ast.Lt):
        gen_code.append(f"    BMI {true_label}") # Branch if N=1
    elif isinstance(op, ast.LtE):
        gen_code.extend([f"    BMI {true_label}", f"    BEQ {true_label}"])
    elif isinstance(op, ast.Gt): # Already swapped
         gen_code.append(f"    BPL {end_label}") # If N=0 (>=)
         gen_code.append(f"    BEQ {end_label}") # If Z=1 (is equal)
         gen_code.append(f"    JMP {true_label}")
    elif isinstance(op, ast.GtE): # Already swapped
         gen_code.append(f"    BCS {true_label}") # Branch if C=1 (>=)

def _handle_integer_comparison(left_op, right_op, op, true_label, end_label):
    """Handle signed 16-bit integer comparisons."""
    # A standard way is to subtract and check flags.
    # right_op - left_op -> determines left_op <> right_op
    gen_code.extend([
        f"    LDA {right_op}", "    SEC", f"    SBC {left_op}",
        f"    STA _temp_0", # Store low byte of result
        f"    LDA {right_op}+1", f"    SBC {left_op}+1",
        # Now A holds the MSB of the result. N and Z flags are set.
        # V flag (overflow) is crucial for signed comparison.
    ])

    if isinstance(op, ast.Eq):
        gen_code.extend([f"    ORA _temp_0", f"    BEQ {true_label}"]) # If (msb | lsb) == 0
    elif isinstance(op, ast.NotEq):
        gen_code.extend([f"    ORA _temp_0", f"    BNE {true_label}"])
    elif isinstance(op, ast.Lt): # left < right  <=>  right - left > 0
        gen_code.extend(["    BVC +", "    EOR #$80", "+: EOR #$80", f"    BPL {true_label}"])
    elif isinstance(op, ast.GtE): # left >= right <=> right - left <= 0
        gen_code.extend(["    BVC +", "    EOR #$80", "+: EOR #$80", f"    BMI {true_label}"])
    elif isinstance(op, ast.Gt): # left > right <=> right - left < 0
        gen_code.extend(["    ORA _temp_0", f"    BEQ {end_label}", "    BVC +", "    EOR #$80", "+: EOR #$80", f"    BMI {true_label}"])
    elif isinstance(op, ast.LtE): # left <= right <=> right - left >= 0
        gen_code.extend(["    BVC +", "    EOR #$80", "+: EOR #$80", f"    BPL {true_label}"])

def handle_comparison(left_op_name, op, right_op_name, target_var_name):
    """Handles an ast.Compare operation."""
    left_is_float = variables.get(left_op_name, {}).get('is_float', False)
    right_is_float = variables.get(right_op_name, {}).get('is_float', False)
    is_float_comparison = left_is_float or right_is_float

    coerced_temps = []
    if is_float_comparison and not (left_is_float and right_is_float):
        if not left_is_float:
            coerced_left = get_temp_var()
            _generate_int_to_float_conversion(left_op_name, coerced_left)
            left_op_name = coerced_left
            coerced_temps.append(coerced_left)
        else:
            coerced_right = get_temp_var()
            _generate_int_to_float_conversion(right_op_name, coerced_right)
            right_op_name = coerced_right
            coerced_temps.append(coerced_right)

    true_label = create_label("cmp_true")
    end_label = create_label("cmp_end")

    if is_float_comparison:
        _handle_float_comparison(left_op_name, right_op_name, op, true_label, end_label)
    else:
        _handle_integer_comparison(left_op_name, right_op_name, op, true_label, end_label)

    # Branch logic to set result to 1 (true) or 0 (false)
    gen_code.extend([
        f"    JMP {end_label}", # Fall through if condition was false
        f"{true_label}:",
        "    LDA #1",          # Set result to 1
        "    JMP +3",
        f"{end_label}:",
        "    LDA #0",          # Set result to 0
        "+:",
        f"    STA {target_var_name}",
        "    LDA #0",
        f"    STA {target_var_name}+1"
    ])
    handle_variable(target_var_name, size=2, var_type='int') # Comparisons yield integers

    for temp in coerced_temps:
        release_temp_var(temp)