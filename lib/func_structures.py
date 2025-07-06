# lib/func_structures.py
"""
Handles the processing of high-level control flow structures like if, for, and while.
"""

import ast
from .. import globals
from . import func_core
from . import func_expressions
from . import ast_processor # For recursive calls to process statement bodies

# Aliases
gen_code = globals.generated_code
report_error = globals.report_compiler_error

def process_if_node(node, error_handler_func, current_func_info=None):
    """Processes an ast.If node, including those inside functions."""
    else_label = func_core.create_label("if_else", str(globals.label_counter))
    end_if_label = func_core.create_label("if_end", str(globals.label_counter))
    globals.label_counter += 1

    # Evaluate the condition
    ast_processor._evaluate_expression_to_ax(node.test, error_handler_func, current_func_info)

    # Check if the result in A/X is zero (False)
    gen_code.append("    ORA X")

    if node.orelse:
        gen_code.append(f"    BEQ {else_label}")
    else:
        gen_code.append(f"    BEQ {end_if_label}")

    # Process the 'if' body
    for statement in node.body:
        # This should be replaced by a central dispatcher call in the future.
        if isinstance(statement, ast.Assign):
            ast_processor.process_assign_node(statement, current_func_info)
        elif isinstance(statement, ast.Expr):
            ast_processor.process_expr_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.If):
            process_if_node(statement, error_handler_func, current_func_info) # Recursive call
        elif isinstance(statement, ast.For):
            process_for_node(statement, error_handler_func, current_func_info) # Cross-call
        elif isinstance(statement, ast.While):
            process_while_node(statement, error_handler_func, current_func_info) # Cross-call
        elif isinstance(statement, ast.Return):
            if not current_func_info: continue
            func_info = globals.defined_functions[current_func_info['name']]
            ast_processor._evaluate_expression_to_ax(statement.value, error_handler_func, current_func_info)
            gen_code.append(f"    JMP {func_info['ret_label']}")
        else:
            report_error(f"Unhandled statement type in if-body: {type(statement).__name__}", node=statement, level="WARNING")

    if node.orelse:
        gen_code.append(f"    JMP {end_if_label}")
        gen_code.append(f"{else_label}:")
        for statement in node.orelse:
            # Dispatch statement processing for else block
            if isinstance(statement, ast.Assign):
                ast_processor.process_assign_node(statement, current_func_info)
            elif isinstance(statement, ast.Expr):
                ast_processor.process_expr_node(statement, error_handler_func, current_func_info)
            elif isinstance(statement, ast.If):
                process_if_node(statement, error_handler_func, current_func_info)
            elif isinstance(statement, ast.For):
                process_for_node(statement, error_handler_func, current_func_info)
            elif isinstance(statement, ast.While):
                process_while_node(statement, error_handler_func, current_func_info)
            else:
                report_error(f"Unhandled statement type in else-body: {type(statement).__name__}", node=statement, level="WARNING")

    gen_code.append(f"{end_if_label}:")


def process_for_node(node, error_handler_func, current_func_info=None):
    """
    Processes an ast.For node.
    Supports 'for i in range(stop)', 'for i in range(start, stop)',
    and 'for i in range(start, stop, step)'.
    """
    # 1. Validate the loop structure
    if not isinstance(node.iter, ast.Call) or not isinstance(node.iter.func, ast.Name) or node.iter.func.id != 'range':
        report_error("For loops are only supported with range()", node=node.iter)
        return

    num_args = len(node.iter.args)
    if not (1 <= num_args <= 3):
        report_error(f"range() expects 1, 2, or 3 arguments, got {num_args}", node=node.iter)
        return

    if not isinstance(node.target, ast.Name):
        report_error("For loop target must be a simple variable name", node=node.target)
        return

    # 2. Setup and argument parsing
    loop_var_name = node.target.id
    current_func_name = current_func_info.get('name') if current_func_info else None
    resolved_loop_var_name = func_core.resolve_variable_name(loop_var_name, current_func_name)

    # Allocate temp vars for start, stop, step
    start_val_var = func_core.get_temp_var()
    stop_val_var = func_core.get_temp_var()
    step_val_var = func_core.get_temp_var()

    # Get expression nodes for start, stop, step based on number of arguments
    if num_args == 1:
        start_node = ast.Constant(value=0)
        stop_node = node.iter.args[0]
        step_node = ast.Constant(value=1)
    elif num_args == 2:
        start_node = node.iter.args[0]
        stop_node = node.iter.args[1]
        step_node = ast.Constant(value=1)
    else:  # num_args == 3
        start_node = node.iter.args[0]
        stop_node = node.iter.args[1]
        step_node = node.iter.args[2]

    # Create labels
    for_start_label = func_core.create_label("for_start", str(globals.label_counter))
    for_end_label = func_core.create_label("for_end", str(globals.label_counter))
    for_pos_step_loop_label = func_core.create_label("for_pos_step_loop", str(globals.label_counter))
    globals.label_counter += 1

    gen_code.append(f"\n    ; --- For loop for '{loop_var_name}' with extended range() ---")

    # 3. Evaluate start, stop, step values
    gen_code.append(f"    ; Evaluate range() arguments")
    func_expressions.translate_expression_recursive(start_val_var, start_node, current_func_name)
    func_expressions.translate_expression_recursive(stop_val_var, stop_node, current_func_name)
    func_expressions.translate_expression_recursive(step_val_var, step_node, current_func_name)

    # 4. Initialize loop variable
    gen_code.append(f"    ; Initialize loop variable '{resolved_loop_var_name}' from start value")
    gen_code.extend(func_core._generate_copy_2_bytes(start_val_var, resolved_loop_var_name))

    # 5. Loop Start and condition check
    gen_code.append(f"\n{for_start_label}:")
    # Check if step is negative
    gen_code.append(f"    LDA {step_val_var}+1 ; Check sign of step value")
    gen_code.append(f"    BPL {for_pos_step_loop_label} ; If positive or zero, jump to positive step logic")

    # --- Negative Step Logic (step < 0) ---
    # Condition: loop_var > stop_var. Exit if loop_var <= stop_var
    gen_code.append(f"    ; Negative step condition: check if {resolved_loop_var_name} <= {stop_val_var}")
    gen_code.extend([
        f"    LDA {resolved_loop_var_name}+1",
        f"    CMP {stop_val_var}+1",
        f"    BCC {for_end_label}",          # if loop_h < stop_h, then loop_var < stop_var, so exit.
        f"    BNE {for_start_label}_continue", # if loop_h > stop_h, then loop_var > stop_var, so continue.
        # High bytes are equal, check low bytes
        f"    LDA {resolved_loop_var_name}",
        f"    CMP {stop_val_var}",
        f"    BCC {for_end_label}",          # if loop_l < stop_l, then loop_var < stop_var, so exit.
        f"    BEQ {for_end_label}",          # if loop_l == stop_l, then loop_var == stop_var, so exit.
    ])
    gen_code.append(f"    JMP {for_start_label}_continue") # loop_var > stop_var, continue

    # --- Positive Step Logic (step >= 0) ---
    gen_code.append(f"\n{for_pos_step_loop_label}:")
    # Condition: loop_var < stop_var. Exit if loop_var >= stop_var
    gen_code.append(f"    ; Positive step condition: check if {resolved_loop_var_name} >= {stop_val_var}")
    gen_code.extend([
        f"    LDA {resolved_loop_var_name}+1",
        f"    CMP {stop_val_var}+1",
        f"    BCC {for_start_label}_continue", # if loop_h < stop_h, continue
        f"    BNE {for_end_label}",          # if loop_h > stop_h, exit
        f"    LDA {resolved_loop_var_name}",
        f"    CMP {stop_val_var}",
        f"    BCS {for_end_label}"           # if loop_l >= stop_l, exit
    ])

    gen_code.append(f"\n{for_start_label}_continue:")

    # 6. Process loop body
    for statement in node.body:
        # Dispatch statement processing
        if isinstance(statement, ast.Assign): ast_processor.process_assign_node(statement, current_func_info)
        elif isinstance(statement, ast.Expr): ast_processor.process_expr_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.If): process_if_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.While): process_while_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.For): process_for_node(statement, error_handler_func, current_func_info)
        else:
            report_error(f"Unhandled statement type in for-loop body: {type(statement).__name__}", node=statement, level="WARNING")

    # 7. Update loop variable by adding step
    gen_code.append(f"    ; Update loop variable: {resolved_loop_var_name} += step")
    gen_code.extend([
        "    CLC",
        f"    LDA {resolved_loop_var_name}",
        f"    ADC {step_val_var}",
        f"    STA {resolved_loop_var_name}",
        f"    LDA {resolved_loop_var_name}+1",
        f"    ADC {step_val_var}+1",
        f"    STA {resolved_loop_var_name}+1"
    ])

    # 8. Jump back to start
    gen_code.append(f"    JMP {for_start_label}")

    # 9. End of loop
    gen_code.append(f"\n{for_end_label}:")
    gen_code.append(f"    ; --- End For loop ---")

    # 10. Cleanup
    func_core.release_temp_var(start_val_var)
    func_core.release_temp_var(stop_val_var)
    func_core.release_temp_var(step_val_var)

def process_while_node(node, error_handler_func, current_func_info=None):
    """Processes an ast.While node."""
    while_start_label = func_core.create_label("while_start", str(globals.label_counter))
    while_end_label = func_core.create_label("while_end", str(globals.label_counter))
    globals.label_counter += 1

    gen_code.append(f"\n{while_start_label}:")
    ast_processor._evaluate_expression_to_ax(node.test, error_handler_func, current_func_info)
    gen_code.append("    ORA X") # Check if A/X is zero
    gen_code.append(f"    BEQ {while_end_label}")

    for statement in node.body:
        if isinstance(statement, ast.Assign): ast_processor.process_assign_node(statement, current_func_info)
        elif isinstance(statement, ast.Expr): ast_processor.process_expr_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.If): process_if_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.While): process_while_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.For): process_for_node(statement, error_handler_func, current_func_info)
        else:
            report_error(f"Unhandled statement type in while-loop body: {type(statement).__name__}", node=statement, level="WARNING")

    gen_code.append(f"    JMP {while_start_label}")
    gen_code.append(f"{while_end_label}:")
