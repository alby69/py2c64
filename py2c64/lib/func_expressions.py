# func_expressions.py
# Functions for handling expressions and binary operations.

import ast  # Importa il modulo ast per la gestione dell'Abstract Syntax Tree
from .. import globals as py2c64_globals  # Importa le variabili globali dal modulo 'globals'
from .func_core import type_value, handle_variable, get_temp_var, release_temp_var, _generate_int_to_float_conversion, _generate_float_to_int_conversion, _copy_variable_content, create_label, \
    _generate_load_float_to_fp1, _generate_load_float_to_fp2, _generate_store_float_from_fp1, _generate_copy_2_bytes
from . import routines


def _handle_binop_multiply_16bit(left_operand_name, right_operand_name, target_variable_name):
    """Handles 16-bit multiplication."""
    for var in ['m16_arg1_l', 'm16_arg1_h', 'm16_arg2_l', 'm16_arg2_h',
                'm16_res_l', 'm16_res_h', 'm16_p0_l', 'm16_p0_h',
                'm16_term2', 'm16_term3', 'm16_mul8_val1', 'm16_mul8_val2']:
        handle_variable(var) # These will be bytes

    py2c64_globals.generated_code.append(f"    LDA {left_operand_name}")
    py2c64_globals.generated_code.append(f"    STA m16_arg1_l")
    py2c64_globals.generated_code.append(f"    LDA {left_operand_name}+1")
    py2c64_globals.generated_code.append(f"    STA m16_arg1_h")
    py2c64_globals.generated_code.append(f"    LDA {right_operand_name}")
    py2c64_globals.generated_code.append(f"    STA m16_arg2_l")
    py2c64_globals.generated_code.append(f"    LDA {right_operand_name}+1")
    py2c64_globals.generated_code.append(f"    STA m16_arg2_h")
    py2c64_globals.used_routines.add('multiply16x16_16')
    py2c64_globals.generated_code.append(f"    JSR multiply16x16_16")
    py2c64_globals.generated_code.append(f"    LDA m16_res_l")
    py2c64_globals.generated_code.append(f"    STA {target_variable_name}")
    py2c64_globals.generated_code.append(f"    LDA m16_res_h")
    py2c64_globals.generated_code.append(f"    STA {target_variable_name}+1")

def _handle_binop_divide_16bit(left_operand_name, right_operand_name, target_variable_name):
    """Handles 16-bit integer division."""
    for var in ['d16_orig_dividend_l', 'd16_orig_dividend_h', 'd16_divisor_l', 'd16_divisor_h',
                'd16_quotient_l', 'd16_quotient_h', 'd16_rem_l', 'd16_rem_h']:
        handle_variable(var) # These will be bytes
    py2c64_globals.generated_code.append(f"    LDA {left_operand_name}")
    py2c64_globals.generated_code.append(f"    STA d16_orig_dividend_l")
    py2c64_globals.generated_code.append(f"    LDA {left_operand_name}+1")
    py2c64_globals.generated_code.append(f"    STA d16_orig_dividend_h")
    py2c64_globals.generated_code.append(f"    LDA {right_operand_name}")
    py2c64_globals.generated_code.append(f"    STA d16_divisor_l")
    py2c64_globals.generated_code.append(f"    LDA {right_operand_name}+1")
    py2c64_globals.generated_code.append(f"    STA d16_divisor_h")
    py2c64_globals.used_routines.add('divide16x16_16')
    py2c64_globals.generated_code.append(f"    JSR divide16x16_16")
    py2c64_globals.generated_code.append(f"    LDA d16_quotient_l")
    py2c64_globals.generated_code.append(f"    STA {target_variable_name}")
    py2c64_globals.generated_code.append(f"    LDA d16_quotient_h")
    py2c64_globals.generated_code.append(f"    STA {target_variable_name}+1")

def binop_handler(left_operand_name, op, right_operand_name, target_variable_name):
    """Handles binary operations (add, sub, mult, div).
       Assumes operands are variable names and are 16-bit words.
       Result is stored directly in target_variable_name and target_variable_name+1.

    Args:
        left_operand_name (str): The name of the left operand variable.
        op (ast.operator): The operator.
        right_operand_name (str): The name of the right operand variable.
        target_variable_name (str): The name of the variable to store the result.

    """
    # Determine if this is a floating-point operation
    # This is a simplification. A more robust way would be type checking/inference.
    # For now, assume if any operand is float, the operation is float.
    left_is_float = py2c64_globals.variables.get(left_operand_name, {}).get('is_float', False)
    right_is_float = py2c64_globals.variables.get(right_operand_name, {}).get('is_float', False)

    is_fp_op = left_is_float or right_is_float  # Operazione in virgola mobile se almeno un operando è

    # The target variable will also be float if either operand is float.
    # Ensure target_variable_name is allocated and marked as float if needed.
    handle_variable(target_variable_name)
    if is_fp_op:
        py2c64_globals.variables[target_variable_name]['is_float'] = True
        py2c64_globals.variables[target_variable_name]['size'] = 4
        py2c64_globals.variables[target_variable_name]['is_8bit_semantic'] = False

        # Coercion logic handled by translate_expression before calling binop_handler.
        # binop_handler now assumes left_operand_name and right_operand_name are
        # of the correct type (both float if is_fp_op is true).

        # Ensure operands passed to binop_handler are indeed float if is_fp_op
        # This is more of an assertion based on prior coercion in translate_expression
        if not py2c64_globals.variables.get(left_operand_name, {}).get('is_float', False) or \
           not py2c64_globals.variables.get(right_operand_name, {}).get('is_float', False):
            py2c64_globals.report_compiler_error(
                f"Internal Error: binop_handler called for FP op but operands '{left_operand_name}' or '{right_operand_name}' are not float.",
                level="ERROR"
            )
            return None
        # If one operand is int and other is float, the int must be converted to float first.
        # This logic should ideally be in translate_expression before calling binop_handler.
        # For now, binop_handler will assume both operands are already in the correct FP format if is_fp_op is true.

    if isinstance(op, ast.Add):
        operator = "add" # Corresponds to FADD
    elif isinstance(op, ast.Sub):
        operator = "sub"
    elif isinstance(op, ast.Mult):
        # TODO: Ensure _handle_binop_multiply_16bit is not called for floats
        operator = "mult"
    elif isinstance(op, ast.FloorDiv):
        operator = "div"
    elif isinstance(op, ast.BitXor):
        operator = "xor"
    else:
        print("Error: operator not supported")
        # Use report_compiler_error for consistency
        py2c64_globals.report_compiler_error(f"Operator {type(op).__name__} not supported.", node=op, level="ERROR")
        # Fallback to a generic error routine if needed, or let the error count stop compilation.
        return None

    # Perform the operation
    if is_fp_op:
        if operator == "add":
            # Load left_operand_name (4 bytes) into ZP X1/M1
            py2c64_globals.generated_code.extend(_generate_load_float_to_fp1(left_operand_name))
            # Load right_operand_name (4 bytes) into ZP X2/M2
            py2c64_globals.generated_code.extend(_generate_load_float_to_fp2(right_operand_name))
            py2c64_globals.generated_code.append(f"    JSR FP_FADD")
            py2c64_globals.used_routines.add('FP_FADD')
            # Store result from ZP X1/M1 into target_variable_name (4 bytes)
            py2c64_globals.generated_code.extend(_generate_store_float_from_fp1(target_variable_name))

        elif operator == "sub":
            # FP1 = left, FP2 = right. FSUB calculates FP1 = FP1 - FP2.
            py2c64_globals.generated_code.extend(_generate_load_float_to_fp1(left_operand_name))
            py2c64_globals.generated_code.extend(_generate_load_float_to_fp2(right_operand_name))
            py2c64_globals.generated_code.append(f"    JSR FP_FSUB")
            py2c64_globals.used_routines.add('FP_FSUB')
            py2c64_globals.generated_code.extend(_generate_store_float_from_fp1(target_variable_name))

        elif operator == "mult":
            # FP1 = left (multiplicand), FP2 = right (multiplier). FMUL calculates FP1 = FP1 * FP2.
            py2c64_globals.generated_code.extend(_generate_load_float_to_fp1(left_operand_name))
            py2c64_globals.generated_code.extend(_generate_load_float_to_fp2(right_operand_name))
            py2c64_globals.generated_code.append(f"    JSR FP_FMUL")
            py2c64_globals.used_routines.add('FP_FMUL')
            py2c64_globals.generated_code.extend(_generate_store_float_from_fp1(target_variable_name))

        elif operator == "div":
            # FDIV expects Dividend in FP2 and Divisor in FP1. Result in FP1.
            # So, left_operand_name (dividend) -> FP2 (X2/M2)
            # right_operand_name (divisor) -> FP1 (X1/M1)
            py2c64_globals.generated_code.extend(_generate_load_float_to_fp2(left_operand_name))
            py2c64_globals.generated_code.extend(_generate_load_float_to_fp1(right_operand_name))
            py2c64_globals.generated_code.append(f"    JSR FP_FDIV")
            py2c64_globals.used_routines.add('FP_FDIV')
            py2c64_globals.generated_code.extend(_generate_store_float_from_fp1(target_variable_name))
        else:
            py2c64_globals.report_compiler_error(f"Floating point operator '{operator}' not supported.", level="ERROR")
    elif operator == "add": # Integer operations
        py2c64_globals.generated_code.append(f"    LDA {left_operand_name}")
        py2c64_globals.generated_code.append("    CLC")
        py2c64_globals.generated_code.append(f"    ADC {right_operand_name}")      # LSB of right_operand
        py2c64_globals.generated_code.append(f"    STA {target_variable_name}")     # Store LSB of result

        py2c64_globals.generated_code.append(f"    LDA {left_operand_name}+1")     # MSB of left_operand
        py2c64_globals.generated_code.append(f"    ADC {right_operand_name}+1")    # MSB of right_operand + Carry
        py2c64_globals.used_routines.add('check_overflow')
        py2c64_globals.generated_code.append("    JSR check_overflow")
        py2c64_globals.generated_code.append(f"    STA {target_variable_name}+1")   # Store MSB of result

    elif operator == "sub":
        py2c64_globals.generated_code.append(f"    LDA {left_operand_name}")       # LSB of left_operand
        py2c64_globals.generated_code.append("    SEC")
        py2c64_globals.generated_code.append(f"    SBC {right_operand_name}")      # LSB of right_operand
        py2c64_globals.generated_code.append(f"    STA {target_variable_name}")     # Store LSB of result

        py2c64_globals.generated_code.append(f"    LDA {left_operand_name}+1")     # MSB of left_operand
        py2c64_globals.generated_code.append(f"    SBC {right_operand_name}+1")    # MSB of right_operand - Borrow
        py2c64_globals.used_routines.add('check_overflow')
        py2c64_globals.generated_code.append("    JSR check_overflow")
        py2c64_globals.generated_code.append(f"    STA {target_variable_name}+1")   # Store MSB of result

    elif operator == "mult":
        _handle_binop_multiply_16bit(left_operand_name, right_operand_name, target_variable_name)

    elif operator == "div":
        _handle_binop_divide_16bit(left_operand_name, right_operand_name, target_variable_name)

    elif operator == "xor":
        py2c64_globals.generated_code.append(f"    LDA {left_operand_name}")       # LSB of left_operand
        py2c64_globals.generated_code.append(f"    EOR {right_operand_name}")      # LSB of right_operand
        py2c64_globals.generated_code.append(f"    STA {target_variable_name}")     # Store LSB of result

        py2c64_globals.generated_code.append(f"    LDA {left_operand_name}+1")     # MSB of left_operand
        py2c64_globals.generated_code.append(f"    EOR {right_operand_name}+1")    # MSB of right_operand
        py2c64_globals.generated_code.append(f"    STA {target_variable_name}+1")   # Store MSB of result

    # binop_handler now directly stores the result, so it doesn't return a register name.
    return None

def _handle_comparison(target_var_name, node, current_func_name):
    """
    Handles an ast.Compare node.
    Generates code to evaluate the comparison and store a boolean result (0 or 1)
    in the target_var_name.
    """
    if len(node.ops) > 1 or len(node.comparators) > 1:
        py2c64_globals.report_compiler_error("Chained comparisons (e.g., a < b < c) are not supported.", node=node)
        return

    op = node.ops[0]
    left_node = node.left
    right_node = node.comparators[0]

    left_op_name = get_value(left_node, current_func_name)
    right_op_name = get_value(right_node, current_func_name)

    # Type coercion logic
    left_type = py2c64_globals.variables.get(left_op_name, {}).get('type', 'int')
    right_type = py2c64_globals.variables.get(right_op_name, {}).get('type', 'int')

    is_float_comparison = left_type == 'float' or right_type == 'float'
    coerced_left_temp = None
    coerced_right_temp = None

    if is_float_comparison:
        if left_type == 'int':
            coerced_left_temp = get_temp_var()
            _generate_int_to_float_conversion(left_op_name, coerced_left_temp)
            left_op_name = coerced_left_temp
        if right_type == 'int':
            coerced_right_temp = get_temp_var()
            _generate_int_to_float_conversion(right_op_name, coerced_right_temp)
            right_op_name = coerced_right_temp

    # Generate labels for branching
    true_label = create_label("cmp_true", str(py2c64_globals.label_counter))
    end_label = create_label("cmp_end", str(py2c64_globals.label_counter))
    py2c64_globals.label_counter += 1

    # --- Comparison Logic ---
    if is_float_comparison:
        py2c64_globals.generated_code.extend(_generate_load_float_to_fp1(left_op_name))
        py2c64_globals.generated_code.extend(_generate_load_float_to_fp2(right_op_name))

        if isinstance(op, ast.Eq):
            py2c64_globals.generated_code.append("    JSR FP_FCMP")
            py2c64_globals.used_routines.add('FP_FCMP')
            py2c64_globals.generated_code.append("    BEQ FP_EQ")  # Jump if equal
            py2c64_globals.generated_code.append(f"    JMP {true_label}") # If not equal, set flag

        elif isinstance(op, ast.NotEq):
            py2c64_globals.generated_code.append("    JSR FP_FCMP")
            py2c64_globals.used_routines.add('FP_FCMP')
            py2c64_globals.generated_code.append("    BNE FP_NE")    # Jump if not equal
            py2c64_globals.generated_code.append(f"    JMP {true_label}") # If equal, set flag

        elif isinstance(op, ast.Lt):
            py2c64_globals.generated_code.append("    JSR FP_FCMP")
            py2c64_globals.used_routines.add('FP_FCMP')
            py2c64_globals.generated_code.append("    BCC FP_LT")  # Jump if less than
            py2c64_globals.generated_code.append(f"    JMP {true_label}")

        elif isinstance(op, ast.LtE):
            py2c64_globals.generated_code.append("    JSR FP_FCMP")
            py2c64_globals.used_routines.add('FP_FCMP')
            py2c64_globals.generated_code.append("    BCS FP_GE") # Jump if >= (Not (less than or equal))
            py2c64_globals.generated_code.append(f"    JMP {true_label}")

        elif isinstance(op, ast.Gt):
            # a > b  is implemented by checking b < a. Swap and reuse less-than logic
            py2c64_globals.generated_code.extend(_generate_load_float_to_fp1(right_op_name))
            py2c64_globals.generated_code.extend(_generate_load_float_to_fp2(left_op_name))
            py2c64_globals.generated_code.append("    JSR FP_FCMP")
            py2c64_globals.used_routines.add('FP_FCMP')
            py2c64_globals.generated_code.append("    BCC FP_LT") # Jump if b < a (meaning a > b)
            py2c64_globals.generated_code.append(f"    JMP {true_label}")

        elif isinstance(op, ast.GtE):
            # a >= b is implemented by checking b <= a. Swap and reuse the <= logic
            py2c64_globals.generated_code.extend(_generate_load_float_to_fp1(right_op_name))
            py2c64_globals.generated_code.extend(_generate_load_float_to_fp2(left_op_name))
            py2c64_globals.generated_code.append("    JSR FP_FCMP")
            py2c64_globals.used_routines.add('FP_FCMP')
            py2c64_globals.generated_code.append("    BCS FP_GE") # Jump if b >= a (meaning a <= b. Negate >= for <=)
            py2c64_globals.generated_code.append(f"    JMP {true_label}")

        else:
            py2c64_globals.report_compiler_error(f"Unsupported comparison operator '{type(op).__name__}' for floats.", node=node)
            return

    else:  # integer comparisons
        py2c64_globals.generated_code.append(f"    LDA {left_op_name}")       # LSB of left
        py2c64_globals.generated_code.append(f"    CMP {right_op_name}")      # Compare with LSB of right

        if isinstance(op, ast.Eq):
            py2c64_globals.generated_code.append(f"    BNE {true_label}")  # Jump if not equal (LSB)
            py2c64_globals.generated_code.append(f"    LDA {left_op_name}+1")   # MSB of left
            py2c64_globals.generated_code.append(f"    CMP {right_op_name}+1")  # Compare MSB
            py2c64_globals.generated_code.append(f"    BNE {true_label}")  # Jump if not equal (MSB)

        elif isinstance(op, ast.NotEq):
            py2c64_globals.generated_code.append(f"    BNE {end_label}_set_true") # Jump if not equal (LSB)
            py2c64_globals.generated_code.append(f"    LDA {left_op_name}+1")   # MSB of left
            py2c64_globals.generated_code.append(f"    CMP {right_op_name}+1")  # Compare MSB
            py2c64_globals.generated_code.append(f"    BNE {end_label}_set_true") # Jump if not equal (MSB)
            py2c64_globals.generated_code.append(f"    JMP {true_label}")     # If both equal, skip the true setting
            py2c64_globals.generated_code.append(f"{end_label}_set_true:")

        elif isinstance(op, ast.Lt):
            py2c64_globals.generated_code.append(f"    BCC {true_label}")      # Jump if less than (LSB)
            py2c64_globals.generated_code.append(f"    BEQ {end_label}_check_msb") # If LSB equal, check MSB
            py2c64_globals.generated_code.append(f"    JMP {true_label}") # Otherwise, result is true
            py2c64_globals.generated_code.append(f"{end_label}_check_msb:")
            py2c64_globals.generated_code.append(f"    LDA {left_op_name}+1")
            py2c64_globals.generated_code.append(f"    CMP {right_op_name}+1")
            py2c64_globals.generated_code.append(f"    BCC {true_label}")      # Jump if less than (MSB)

        elif isinstance(op, ast.Gt):
            py2c64_globals.generated_code.append(f"    BCS {true_label}")      # Jump if greater than (LSB: Carry Set)
            py2c64_globals.generated_code.append(f"    BEQ {end_label}_check_msb_gt") # If equal LSB, check MSB
            py2c64_globals.generated_code.append(f"    JMP {true_label}")
            py2c64_globals.generated_code.append(f"{end_label}_check_msb_gt:")
            py2c64_globals.generated_code.append(f"    LDA {left_op_name}+1")
            py2c64_globals.generated_code.append(f"    CMP {right_op_name}+1")
            py2c64_globals.generated_code.append(f"    BCS {true_label}")      # Jump if greater than (MSB: Carry Set)

        elif isinstance(op, ast.LtE):
            py2c64_globals.generated_code.append(f"    BCC {true_label}")  # Jump if less than (LSB: Carry Clear)
            py2c64_globals.generated_code.append(f"    BEQ {end_label}_check_msb_lte") # Jump if equal to check MSB
            py2c64_globals.generated_code.append(f"    JMP {true_label}")
            py2c64_globals.generated_code.append(f"{end_label}_check_msb_lte:")
            py2c64_globals.generated_code.append(f"    LDA {left_op_name}+1")
            py2c64_globals.generated_code.append(f"    CMP {right_op_name}+1")
            py2c64_globals.generated_code.append(f"    BCC {true_label}")      # Jump if less than or equal (MSB)
            py2c64_globals.generated_code.append(f"    BEQ {true_label}")

        elif isinstance(op, ast.GtE):
            py2c64_globals.generated_code.append(f"    BCS {true_label}")  # Jump if greater than (LSB: Carry Set)
            py2c64_globals.generated_code.append(f"    BEQ {end_label}_check_msb_gte") # If LSB is equal, check MSB
            py2c64_globals.generated_code.append(f"    JMP {true_label}")
            py2c64_globals.generated_code.append(f"{end_label}_check_msb_gte:")
            py2c64_globals.generated_code.append(f"    LDA {left_op_name}+1")
            py2c64_globals.generated_code.append(f"    CMP {right_op_name}+1")
            py2c64_globals.generated_code.append(f"    BCS {true_label}")      # Jump if greater than or equal (MSB: Carry Set)
            py2c64_globals.generated_code.append(f"    BEQ {true_label}")

        else:
            py2c64_globals.report_compiler_error(f"Unsupported comparison operator '{type(op).__name__}' for integers.", node=node)
            return

    # Store the result (True = 0, False = 1), branching as needed
    py2c64_globals.generated_code.append(f"    LDA #0")         # False (0) if condition is not met
    py2c64_globals.generated_code.append(f"    JMP {end_label}")     # Skip setting to True
    py2c64_globals.generated_code.append(f"{true_label}:")
    py2c64_globals.generated_code.append(f"    LDA #1")         # True (1) if condition is met
    py2c64_globals.generated_code.append(f"{end_label}:")
    py2c64_globals.generated_code.append(f"    STA {target_var_name}")  # Store result (0 or 1) in target
    py2c64_globals.generated_code.append(f"    LDA #0") # Ensure MSB is clear (though comparison result is just 0 or 1)
    py2c64_globals.generated_code.append(f"    STA {target_var_name}+1")

    # Release temporary variables used for coercion if needed.
    if coerced_left_temp:
        release_temp_var(coerced_left_temp)
    if coerced_right_temp:
        release_temp_var(coerced_right_temp)

def translate_expression(var_name, node, current_func_name=None):
    """Translate a BinOp expression to assembly code.

    Args:
        var_name (str): The name of the variable to store the result.
        node (ast.Assign): The AST node representing the assignment.
        current_func_name (str, optional): The name of the current function, if in one.
    """
    # global generated_code
    op = node.value.op
    left = node.value.left
    right = node.value.right

    # Ensure temp_vars are allocated
    handle_variable('temp_0') # Used by overflow_error_msg, division_by_zero_msg, generic_error_msg

    # Determine if the target variable 'var_name' is intended to be a float.
    # This is tricky. If the expression involves float literals or float variables,
    # var_name should become float.
    # For now, if var_name was already float, or if the expression is float, it's float.
    # This needs a more robust type inference system.
    target_is_float = py2c64_globals.variables.get(var_name, {}).get('is_float', False)
    # If left is a constant or a sub-expression, store it in a temporary variable.
    left_is_temp = False
    left_id_resolved = ""
    if isinstance(left, ast.Constant):
        left_id_resolved = get_temp_var()
        type_value(left_id_resolved, left) # type_value now handles 16-bit assignment
        # If the constant was float, left_id_resolved is now marked as float by type_value
        left_is_temp = True
    elif not isinstance(left, ast.Name):
        left_id_resolved = get_temp_var()
        # If the sub-expression results in a float, translate_expression_recursive
        # should ensure left_id_resolved is marked as float.
        translate_expression_recursive(left_id_resolved, left, current_func_name) # Result in left_id and left_id+1
        left_is_temp = True
    else: # It's an ast.Name
        original_left_id = left.id
        left_id_resolved = original_left_id
        # TODO: Handle mangled names for function local scope
        if current_func_name:
            mangled_name = f"__{current_func_name}_{original_left_id}"
            if mangled_name in py2c64_globals.variables:
                left_id_resolved = mangled_name

    right_is_temp = False
    right_id_resolved = ""
    if isinstance(right, ast.Constant):
        right_id_resolved = get_temp_var()
        type_value(right_id_resolved, right) # type_value now handles 16-bit assignment
        # If the constant was float, right_id_resolved is now marked as float
        right_is_temp = True
    elif not isinstance(right, ast.Name):
        right_id_resolved = get_temp_var()
        # If the sub-expression results in a float, translate_expression_recursive
        # should ensure right_id_resolved is marked as float.
        translate_expression_recursive(right_id_resolved, right, current_func_name) # Result in right_id and right_id+1
        right_is_temp = True
    else: # It's an ast.Name
        original_right_id = right.id
        right_id_resolved = original_right_id
        # TODO: Handle mangled names
        if current_func_name:
            mangled_name = f"__{current_func_name}_{original_right_id}"
            if mangled_name in py2c64_globals.variables:
                right_id_resolved = mangled_name

    # --- Coercion Logic ---
    left_is_float_type = py2c64_globals.variables.get(left_id_resolved, {}).get('is_float', False)
    right_is_float_type = py2c64_globals.variables.get(right_id_resolved, {}).get('is_float', False)

    final_left_operand_for_binop = left_id_resolved
    final_right_operand_for_binop = right_id_resolved
    coerced_left_temp_storage = None
    coerced_right_temp_storage = None

    is_fp_operation_overall = left_is_float_type or right_is_float_type

    if is_fp_operation_overall:
        handle_variable(var_name) # Ensure target 'var_name' is allocated
        py2c64_globals.variables[var_name]['is_float'] = True
        py2c64_globals.variables[var_name]['size'] = 4
        py2c64_globals.variables[var_name]['is_8bit_semantic'] = False

        if left_is_float_type and not right_is_float_type: # Right (int) needs coercion
            coerced_right_temp_storage = get_temp_var()
            handle_variable(coerced_right_temp_storage)
            py2c64_globals.variables[coerced_right_temp_storage]['is_float'] = True
            py2c64_globals.variables[coerced_right_temp_storage]['size'] = 4
            py2c64_globals.variables[coerced_right_temp_storage]['is_8bit_semantic'] = False
            _generate_int_to_float_conversion(right_id_resolved, coerced_right_temp_storage)
            final_right_operand_for_binop = coerced_right_temp_storage
        elif not left_is_float_type and right_is_float_type: # Left (int) needs coercion
            coerced_left_temp_storage = get_temp_var()
            handle_variable(coerced_left_temp_storage)
            py2c64_globals.variables[coerced_left_temp_storage]['is_float'] = True
            py2c64_globals.variables[coerced_left_temp_storage]['size'] = 4
            py2c64_globals.variables[coerced_left_temp_storage]['is_8bit_semantic'] = False
            _generate_int_to_float_conversion(left_id_resolved, coerced_left_temp_storage)
            final_left_operand_for_binop = coerced_left_temp_storage

    # Perform binary operation
    # binop_handler will store the result directly into var_name and var_name+1
    binop_handler(final_left_operand_for_binop, op, final_right_operand_for_binop, var_name)

    # Release temporary variables
    if left_is_temp:
        release_temp_var(left_id_resolved)
    if right_is_temp:
        release_temp_var(right_id_resolved)
    if coerced_left_temp_storage:
        release_temp_var(coerced_left_temp_storage)
    if coerced_right_temp_storage:
        release_temp_var(coerced_right_temp_storage)

def get_value(node, current_func_name=None):
    """Get the value or the var_name of a node.

    Args:
        node (ast.AST): The AST node.
        current_func_name (str, optional): The name of the current function, if in one.

    Returns:
        str: The value (constant) or variable name.
    """
    if isinstance(node, ast.Constant): # Constants are global
        if isinstance(node.value, int):
            # This path is problematic for direct use in binop_handler.
            # Constants should be loaded into temp vars first.
            # If get_value is called for a simple int constant, we create a temp var.
            temp_const_var = get_temp_var()
            type_value(temp_const_var, node)
            return temp_const_var
        elif isinstance(node.value, float): # Python float literal
            temp_float_const_var = get_temp_var()
            type_value(temp_float_const_var, node) # type_value needs to handle this
            return temp_float_const_var
        else:
            return f"{node.value}" # For strings, etc. (not for arithmetic)
    elif isinstance(node, ast.Name):
        original_id = node.id
        resolved_id = original_id
        if current_func_name:
            mangled_name = f"__{current_func_name}_{original_id}"
            if mangled_name in py2c64_globals.variables:
                resolved_id = mangled_name

        if resolved_id in py2c64_globals.variables:
            return resolved_id
        else: # pragma: no cover # Should ideally be caught by first pass or earlier checks
            py2c64_globals.report_compiler_error(f"Variable '{resolved_id}' not found.", node=node, level="ERROR")
            return None
    elif isinstance(node, ast.BinOp):  # if is a binop, it's managed recursively
        temp = get_temp_var()
        translate_expression_recursive(temp, node, current_func_name)
        return temp
    else:
        py2c64_globals.report_compiler_error(f"Node type {type(node).__name__} not directly resolvable by get_value in this context.", node=node, level="ERROR")
        return None


def translate_expression_recursive(var_name, node, current_func_name=None):
    """Recursive function for handling expressions.

    Args:
        var_name (str): The name of the variable to store the result.
        node (ast.AST): The AST node representing the expression.
        current_func_name (str, optional): The name of the current function, if in one.
    """
    if isinstance(node, ast.BinOp):
        # --- Start Constant Folding ---
        # Check if both operands are constants
        if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
            try:
                left_val = node.left.value
                right_val = node.right.value
                result_val = None

                # Perform the operation based on the operator type
                if isinstance(node.op, ast.Add):
                    result_val = left_val + right_val # type: ignore
                elif isinstance(node.op, ast.Sub):
                    result_val = left_val - right_val # type: ignore
                elif isinstance(node.op, ast.Mult):
                    result_val = left_val * right_val # type: ignore
                elif isinstance(node.op, ast.Div): # True division (results in float)
                    if right_val == 0:
                        raise ZeroDivisionError("Division by zero at compile time.")
                    result_val = left_val / right_val # type: ignore
                elif isinstance(node.op, ast.FloorDiv): # Integer division
                    if right_val == 0:
                        raise ZeroDivisionError("Integer division by zero at compile time.")
                    result_val = left_val // right_val # type: ignore
                elif isinstance(node.op, ast.Mod):
                    if right_val == 0:
                        raise ZeroDivisionError("Modulo by zero at compile time.")
                    result_val = left_val % right_val # type: ignore
                elif isinstance(node.op, ast.Pow):
                    result_val = left_val ** right_val # type: ignore
                elif isinstance(node.op, ast.LShift):
                    result_val = left_val << right_val # type: ignore
                elif isinstance(node.op, ast.RShift):
                    result_val = left_val >> right_val # type: ignore
                elif isinstance(node.op, ast.BitAnd):
                    result_val = left_val & right_val # type: ignore
                elif isinstance(node.op, ast.BitOr):
                    result_val = left_val | right_val # type: ignore
                elif isinstance(node.op, ast.BitXor):
                    result_val = left_val ^ right_val # type: ignore
                # Add more operators as needed

                if result_val is not None:
                    # If constant folding was successful, replace the BinOp with a new Constant node
                    new_constant_node = ast.Constant(value=result_val)
                    type_value(var_name, new_constant_node)
                    return # Constant folded, no further processing for this BinOp

            except ZeroDivisionError as e:
                py2c64_globals.report_compiler_error(f"Compile-time error: {e}", node=node, level="ERROR")
                type_value(var_name, ast.Constant(value=0)) # Assign a default value (e.g., 0)
                return
            except Exception as e:
                py2c64_globals.report_compiler_error(f"Error during constant folding: {e}", node=node, level="WARNING")
                # Fall through to normal code generation if an unexpected error occurs

        # When translating a BinOp recursively, the var_name is the target for this sub-expression.
        # The current_func_name context applies to the operands within this BinOp.
        # We need to determine if this operation will result in a float.
        # This requires inspecting node.left and node.right.
        # For now, assume translate_expression and binop_handler will mark var_name as float if needed.
        translate_expression(var_name, ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=node), current_func_name)
    elif isinstance(node, ast.Constant):
        # Constants are global, no function context needed for type_value itself.
        # type_value will mark var_name as float if node.value is a Python float.
        type_value(var_name, node) # type_value now handles float constants
    elif isinstance(node, ast.Name):
        # If node.id is a local/param, it needs to be resolved to its mangled name
        # before type_value copies it. type_value expects the source var name to be resolvable.
        source_var_name = node.id
        if current_func_name:
            mangled_source_name = f"__{current_func_name}_{source_var_name}"
            if mangled_source_name in py2c64_globals.variables:
                source_var_name = mangled_source_name

        # Copy the content of the source variable to the destination variable
        _copy_variable_content(source_var_name, var_name, current_func_name)

    elif isinstance(node, ast.Call): # Handle function calls as expressions, e.g., in `return myfunc()`
        # This handles cases like `return my_func()` or `x = other_func() + my_func()`
        # The result of the call (from __func_retval) needs to be stored in 'var_name'.
        if isinstance(node.func, ast.Name):
            func_name_called = node.func.id
            actual_args_count = len(node.args) # Get this
            if func_name_called in py2c64_globals.defined_functions:
                func_info = py2c64_globals.defined_functions[func_name_called]
                expected_params = len(func_info.get('params', []))
                actual_args = len(node.args)

                if actual_args != expected_params:
                    py2c64_globals.report_compiler_error(f"Function '{func_name_called}' called with {actual_args} args, expected {expected_params}", node=node, level="ERROR")
                    # Assign default to var_name and return
                    type_value(var_name, ast.Constant(value=0))
                    return

                # Evaluate and pass arguments
                temp_arg_vars = []
                for i, arg_node in enumerate(node.args):
                    # _get_func_arg_var_name is defined in ast_processor.
                    # For now, let's construct the name directly here as it's simple.
                    arg_holder_name = f"__func_arg_{i}"
                    handle_variable(arg_holder_name)
                    # Recursively evaluate the argument expression into the dedicated __func_arg_N
                    translate_expression_recursive(arg_holder_name, arg_node, current_func_name)
                    # No need to add to temp_arg_vars for release, as __func_arg_N are persistent.

                py2c64_globals.generated_code.append(f"    JSR {func_info['label']}")

                # The return value is in A/X (2 bytes) or FP1 (4 bytes for float).
                # We need to copy it to `var_name`.
                # The type inference pass should have determined the return type of the function.
                return_type = func_info.get('return_type', 'unknown')

                # Ensure `var_name` is allocated with the correct type/size.
                handle_variable(var_name, size=2 if return_type == 'int' else 4, var_type=return_type)

                if return_type == 'float':
                    # Result is in FP1 (X1/M1). Copy to var_name.
                    py2c64_globals.generated_code.extend(_generate_store_float_from_fp1(var_name))
                elif return_type == 'int':
                    # Result is in A (MSB) and X (LSB). Copy to var_name.
                    py2c64_globals.generated_code.append(f"    STX {var_name}") # LSB
                    py2c64_globals.generated_code.append(f"    STA {var_name}+1") # MSB
                else:
                    # Fallback for unknown return types, copy 2 bytes (int)
                    py2c64_globals.report_compiler_error(f"Unknown return type for function '{func_name_called}'. Assuming int (2 bytes).", level="WARNING")
                    py2c64_globals.generated_code.append(f"    STX {var_name}") # LSB
                    py2c64_globals.generated_code.append(f"    STA {var_name}+1") # MSB
            # --- Handle built-in functions called in expressions ---
            elif func_name_called == 'float' and actual_args_count == 1:
                arg_node = node.args[0]
                temp_int_arg = get_temp_var()
                translate_expression_recursive(temp_int_arg, arg_node, current_func_name) # Evaluate arg into temp_int_arg
                handle_variable(var_name, size=4, var_type='float') # Ensure target is float
                _generate_int_to_float_conversion(temp_int_arg, var_name) # Convert and copy
                release_temp_var(temp_int_arg)
            elif func_name_called == 'int' and actual_args_count == 1:
                arg_node = node.args[0]
                temp_float_arg = get_temp_var()
                translate_expression_recursive(temp_float_arg, arg_node, current_func_name)
                handle_variable(var_name) # var_name is the target for int() result
                py2c64_globals.variables[var_name]['is_float'] = False
                py2c64_globals.variables[var_name]['size'] = 2 # Ensure size is 2 for int
                py2c64_globals.variables[var_name]['is_8bit_semantic'] = True
                # Use _copy_variable_content to handle potential type coercion
                _copy_variable_content(temp_float_arg, var_name, current_func_name)
                release_temp_var(temp_float_arg)
            elif func_name_called == 'abs' and actual_args_count == 1:
                arg_node = node.args[0]
                temp_arg_for_abs = get_temp_var()
                translate_expression_recursive(temp_arg_for_abs, arg_node, current_func_name)
                arg_is_float = py2c64_globals.variables.get(temp_arg_for_abs, {}).get('is_float', False)
                handle_variable(var_name) # Ensure target 'var_name' is allocated
                if arg_is_float:
                    py2c64_globals.variables[var_name]['is_float'] = True
                    py2c64_globals.variables[var_name]['size'] = 4
                    py2c64_globals.generated_code.extend(_generate_load_float_to_fp1(temp_arg_for_abs))
                    py2c64_globals.generated_code.append(f"    JSR FP_ABS")
                    py2c64_globals.used_routines.add('FP_ABS')
                    py2c64_globals.generated_code.extend(_generate_store_float_from_fp1(var_name))
                else: # Integer abs
                    handle_variable(var_name, size=2, var_type='int') # Ensure target is int
                    # (Integer abs logic from ast_processor, target is var_name)
                    abs_int_positive_label = create_label("abs_int_pos_rec", str(py2c64_globals.label_counter))
                    abs_int_done_label = create_label("abs_int_done_rec", str(py2c64_globals.label_counter))
                    # Ensure temp_arg_for_abs is treated as a 16-bit integer for the following operations
                    # This might involve a float-to-int conversion if temp_arg_for_abs was float
                    if py2c64_globals.variables.get(temp_arg_for_abs, {}).get('type') == 'float':
                        _generate_float_to_int_conversion(temp_arg_for_abs, temp_arg_for_abs)
                    py2c64_globals.label_counter += 1
                    py2c64_globals.generated_code.append(f"    LDA {temp_arg_for_abs}+1")
                    py2c64_globals.generated_code.append(f"    BPL {abs_int_positive_label}")
                    py2c64_globals.generated_code.extend([f"    LDA {temp_arg_for_abs}", f"    EOR #$FF", f"    STA {var_name}",
                                           f"    LDA {temp_arg_for_abs}+1", f"    EOR #$FF", f"    STA {var_name}+1",
                                           f"    LDA {var_name}", f"    CLC", f"    ADC #1", f"    STA {var_name}",
                                           f"    LDA {var_name}+1", f"    ADC #0", f"    STA {var_name}+1"])
                    py2c64_globals.generated_code.append(f"    JMP {abs_int_done_label}")
                    py2c64_globals.generated_code.append(f"{abs_int_positive_label}:")
                    py2c64_globals.generated_code.extend([f"    LDA {temp_arg_for_abs}", f"    STA {var_name}",
                                           f"    LDA {temp_arg_for_abs}+1", f"    STA {var_name}+1"])
                    py2c64_globals.generated_code.append(f"{abs_int_done_label}:")
                release_temp_var(temp_arg_for_abs)
            # Add sgn, log, exp handlers similarly, adapting from ast_processor.py
            # Ensure they target 'var_name' and manage their own temporary variables.
            elif func_name_called == 'sgn' and actual_args_count == 1:
                # (Simplified: adapt full sgn logic from ast_processor.py here)
                # For brevity, this part is conceptual. Full logic would be similar to 'abs' above.
                py2c64_globals.report_compiler_error(f"Recursive sgn call to be fully implemented for {var_name}", node=node, level="INFO")
                type_value(var_name, ast.Constant(value=0)) # Placeholder

            elif func_name_called == 'log' and actual_args_count == 1:
                arg_node = node.args[0]
                temp_arg_for_log = get_temp_var()
                translate_expression_recursive(temp_arg_for_log, arg_node, current_func_name)
                # Ensure target var_name is float
                handle_variable(var_name, size=4, var_type='float')
                # Load argument into FP1 (with potential int-to-float conversion)
                py2c64_globals.generated_code.extend(_generate_load_float_to_fp1(temp_arg_for_log))
                py2c64_globals.generated_code.append(f"    JSR FP_LOG")
                py2c64_globals.used_routines.add('FP_LOG')
                # Store result from FP1 into var_name
                py2c64_globals.generated_code.extend(_generate_store_float_from_fp1(var_name))
                release_temp_var(temp_arg_for_log)

            elif func_name_called == 'exp' and actual_args_count == 1:
                arg_node = node.args[0]
                temp_arg_for_exp = get_temp_var()
                translate_expression_recursive(temp_arg_for_exp, arg_node, current_func_name)
                # Ensure target var_name is float
                handle_variable(var_name, size=4, var_type='float')
                # Load argument into FP1 (with potential int-to-float conversion)
                py2c64_globals.generated_code.extend(_generate_load_float_to_fp1(temp_arg_for_exp))
                py2c64_globals.generated_code.append(f"    JSR FP_EXP")
                py2c64_globals.used_routines.add('FP_EXP')
                # Store result from FP1 into var_name
                py2c64_globals.generated_code.extend(_generate_store_float_from_fp1(var_name))
                release_temp_var(temp_arg_for_exp)

            # --- NEW: Sprite functions that return a value ---
            elif func_name_called in ['sprite_check_collision_sprite', 'sprite_check_collision_data']:
                if actual_args_count != 0:
                    py2c64_globals.report_compiler_error(f"Function '{func_name_called}' expects 0 arguments, got {actual_args_count}.", node=node, level="ERROR")
                    type_value(var_name, ast.Constant(value=0)) # Assign default and return
                    return

                # Ensure target var_name is an integer
                handle_variable(var_name, size=2, var_type='int') # Allocate as 16-bit int for consistency
                py2c64_globals.variables[var_name]['is_8bit_semantic'] = True # But it's semantically 8-bit

                # Call the routine
                py2c64_globals.generated_code.append(f"    JSR {func_name_called}")
                py2c64_globals.used_routines.add(func_name_called)

                # The result is in A. Store it in var_name (LSB), and clear MSB.
                py2c64_globals.generated_code.append(f"    STA {var_name}")
                py2c64_globals.generated_code.append(f"    LDA #0")
                py2c64_globals.generated_code.append(f"    STA {var_name}+1")

            else: # Function not in defined_functions (e.g. built-ins not yet fully handled here)
                py2c64_globals.report_compiler_error(f"Recursive expression translation for ast.Call to unknown function '{func_name_called}' for target '{var_name}' not fully implemented. Assigning 0.", node=node, level="WARNING")
                type_value(var_name, ast.Constant(value=0))
        else:
            py2c64_globals.report_compiler_error(f"Recursive expression translation for ast.Call to non-Name function not supported for target '{var_name}'. Assigning 0.", node=node, level="WARNING")
            type_value(var_name, ast.Constant(value=0))
