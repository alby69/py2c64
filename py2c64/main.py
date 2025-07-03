# main.py
import ast
from . import globals # Module-level import
from .lib import routines
from .lib.func_core import *
from .lib.func_expressions_old import *
from .lib.func_structures import *
from .lib.func_dict import *
from .lib.func_strings import *
from .lib import ast_processor


def _apply_peephole_optimizations(code_list):
    """
    Applies peephole optimizations to the generated assembly code.
    Currently implements:
    1. Removal of redundant JMP instructions where the target label is the very next line.
    """
    optimized_code = []
    i = 0
    while i < len(code_list):
        line = code_list[i].strip()

        # Optimization 1: Remove JMP to the very next instruction
        # Pattern:
        # JMP label
        # label:
        if line.startswith("JMP ") and i + 1 < len(code_list):
            target_label = line[4:].strip()
            if code_list[i+1].strip().startswith(target_label + ":"):
                i += 1 # Skip the JMP instruction, the label will be added in the next iteration
                continue # Continue to process the label line
        optimized_code.append(code_list[i])
        i += 1
    return optimized_code


def _infer_expression_type(expr_node, current_func_name_context=None):
    """
    Recursively infers the type of an expression node.
    Returns a string like 'int', 'float', 'str', 'list', 'dict', or 'unknown'.
    """
    if isinstance(expr_node, ast.Constant):
        if isinstance(expr_node.value, float):
            return 'float'
        elif isinstance(expr_node.value, int):
            return 'int'
        elif isinstance(expr_node.value, str):
            return 'str'
        # bool is a subclass of int, so this handles it correctly for now.
        return 'unknown'

    elif isinstance(expr_node, ast.Name):
        var_id = expr_node.id
        resolved_var_id = var_id
        if current_func_name_context:
            mangled_name = ast_processor._get_mangled_local_var_name(current_func_name_context, var_id)
            if mangled_name in globals.variables:
                resolved_var_id = mangled_name

        if resolved_var_id in globals.variables:
            return globals.variables[resolved_var_id].get('type', 'unknown')
        return 'unknown'

    elif isinstance(expr_node, ast.Call):
        if not isinstance(expr_node.func, ast.Name):
            return 'unknown'  # Cannot handle complex calls like obj.method() yet

        func_id = expr_node.func.id
        # Handle built-in type casting functions
        if func_id == 'float':
            return 'float'
        if func_id == 'int':
            return 'int'
        if func_id == 'str':
            return 'str'

        # Handle other built-ins
        if func_id in ['abs', 'sgn']:  # These return the same type as their argument
            if len(expr_node.args) == 1:
                return _infer_expression_type(expr_node.args[0], current_func_name_context)
        if func_id in ['log', 'exp']:  # These are float-specific
            return 'float'

        # Check user-defined functions
        if func_id in globals.defined_functions:
            return globals.defined_functions[func_id].get('return_type', 'unknown')

        return 'unknown'  # Default for unknown function calls

    elif isinstance(expr_node, ast.BinOp):
        left_type = _infer_expression_type(expr_node.left, current_func_name_context)
        right_type = _infer_expression_type(expr_node.right, current_func_name_context)

        # Type promotion rules (simplified)
        if left_type == 'float' or right_type == 'float':
            # Any arithmetic operation with a float results in a float.
            # Note: This is a simplification. True division '/' would also produce a float.
            # The compiler currently handles '//' as integer division.
            if isinstance(expr_node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
                 return 'float'
        if left_type == 'int' and right_type == 'int':
            # int op int -> int (for most ops supported)
            return 'int'
        if isinstance(expr_node.op, ast.Add) and (left_type == 'str' or right_type == 'str'):
            # Basic string concatenation
            return 'str'
        return 'unknown'

    elif isinstance(expr_node, (ast.List, ast.ListComp)):
        return 'list'
    elif isinstance(expr_node, (ast.Dict, ast.DictComp)):
        return 'dict'
    elif isinstance(expr_node, ast.Tuple):
        return 'tuple'
    elif isinstance(expr_node, (ast.Set, ast.SetComp)):
        return 'set'

    return 'unknown'


def _type_inference_visitor(node, current_func_name=None):
    """
    Recursively visits AST nodes to infer types. This is the core of the type-inference pass.
    Returns True if any type information was changed, False otherwise.
    """
    changed = False

    # --- Handle specific node types that define or change types ---

    if isinstance(node, ast.Assign):
        # Infer type of the right-hand side
        rhs_type = _infer_expression_type(node.value, current_func_name)

        if rhs_type != 'unknown':
            # Update type of the target variable(s)
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    resolved_var_id = var_name
                    if current_func_name:
                        mangled_name = ast_processor._get_mangled_local_var_name(current_func_name, var_name)
                        if mangled_name in globals.variables:
                            resolved_var_id = mangled_name

                    if resolved_var_id in globals.variables:
                        # Check if type is changing from its previous state
                        if globals.variables[resolved_var_id].get('type') != rhs_type:
                            globals.variables[resolved_var_id]['type'] = rhs_type
                            changed = True
        # Recurse on the value to catch nested inferences
        if _type_inference_visitor(node.value, current_func_name):
            changed = True

    elif isinstance(node, ast.FunctionDef):
        func_name = node.name
        # Recursively process the function body with the current function context
        for child_node in node.body:
            if _type_inference_visitor(child_node, func_name):
                changed = True

        # After processing the body, try to infer the function's return type.
        # We take the type of the first return statement found.
        # A more robust system would find a common type or flag mixed types.
        current_return_type = globals.defined_functions[func_name].get('return_type', 'unknown')
        new_return_type = 'unknown'
        for sub_node in ast.walk(node):
            if isinstance(sub_node, ast.Return) and sub_node.value:
                inferred_type = _infer_expression_type(sub_node.value, func_name)
                if inferred_type != 'unknown':
                    # For now, the first typed return statement determines the type.
                    new_return_type = inferred_type
                    break

        if new_return_type != current_return_type:
            globals.defined_functions[func_name]['return_type'] = new_return_type
            changed = True

    # --- Generic recursion for other node types ---
    else:
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        if _type_inference_visitor(item, current_func_name if not isinstance(node, ast.FunctionDef) else node.name):
                            changed = True
            elif isinstance(value, ast.AST):
                if _type_inference_visitor(value, current_func_name if not isinstance(node, ast.FunctionDef) else node.name):
                    changed = True

    return changed


def generate_error_handling_assembly(e):
    """Generates assembly code for error handling based on the exception type."""
    assembly_code_lines = []
    if isinstance(e, OverflowError):
        assembly_code_lines.extend([f"    LDA #{globals.ErrorCodes.OVERFLOW}", "    JSR error_handler"])
    elif isinstance(e, ZeroDivisionError):
        assembly_code_lines.extend([f"    LDA #{globals.ErrorCodes.DIVISION_BY_ZERO}", "    JSR error_handler"])
    elif isinstance(e, KeyError):
        assembly_code_lines.extend([f"    LDA #{globals.ErrorCodes.KEY_NOT_FOUND}", "    JSR error_handler"])
    else:
        assembly_code_lines.extend([f"    LDA #{globals.ErrorCodes.GENERIC_RUNTIME_ERROR_CODE}", "    JSR error_handler"])
    globals.generated_code.extend(assembly_code_lines)
    # No need to return assembly_code_lines if we directly modify globals.generated_code

def _collect_variables_recursive(node, current_func_name=None, local_offset_ptr=None):
    """
    Recursively traverses the AST to find all variable names, and for functions,
    assigns stack offsets to parameters and local variables.
    """
    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
        var_name = node.id
        if current_func_name:
            mangled_name = ast_processor._get_mangled_local_var_name(current_func_name, var_name)
            # Check if it's a new local variable. Parameters are handled in FunctionDef.
            if mangled_name not in globals.variables:
                # This is a new local variable. Assign it a negative offset from FP.
                # The size will be determined by type inference later. Default to 2.
                var_size = 2
                local_offset_ptr[0] -= var_size # Decrement offset for next local
                globals.variables[mangled_name] = {
                    'scope': 'local',
                    'offset': local_offset_ptr[0],
                    'size': var_size,
                    'type': 'unknown'
                }
                # Store local var info in the function's definition as well
                globals.defined_functions[current_func_name]['local_vars'][mangled_name] = {
                    'offset': local_offset_ptr[0],
                    'size': var_size
                }
        else:
            handle_variable(var_name) # Global variable

    elif isinstance(node, ast.FunctionDef):
        func_name = node.name

        # --- Add function to defined_functions if not already there ---
        if func_name not in globals.defined_functions:
            func_label = create_label(f"func_{func_name}", str(globals.label_counter))
            ret_label = create_label(f"func_ret_{func_name}", str(globals.label_counter))
            globals.label_counter += 1
            param_names = [p.arg for p in node.args.args]
            globals.defined_functions[func_name] = {
                'label': func_label, 'params': param_names, 'ret_label': ret_label,
                'name': func_name, 'return_type': 'unknown',
                'total_locals_size': 0, 'local_vars': {}
            }

        # --- Assign offsets for parameters ---
        param_offset_counter = 4
        for arg in node.args.args:
            mangled_param_name = ast_processor._get_mangled_local_var_name(func_name, arg.arg)
            param_size = 2 # Assume all params are 2 bytes for now
            globals.variables[mangled_param_name] = {
                'scope': 'param', 'offset': param_offset_counter,
                'size': param_size, 'type': 'unknown'
            }
            param_offset_counter += param_size

        # --- Process function body for local variables ---
        local_offset_for_func = [0] # Use a list to pass by reference. Start at 0, first local will be at -2.
        for child_node in node.body:
            _collect_variables_recursive(child_node, func_name, local_offset_for_func)

        # --- Calculate total size of local variables ---
        total_size = abs(local_offset_for_func[0])
        globals.defined_functions[func_name]['total_locals_size'] = total_size

    elif isinstance(node, ast.Assign):
         # Check if the assignment target is a Name and process its RHS for variable collection
         if isinstance(node.targets[0], ast.Name):
             _collect_variables_recursive(node.value, current_func_name) # Recurse on the value node

    # Generic recursion for other node types that might contain variable definitions or function defs
    for field, value in ast.iter_fields(node):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ast.AST):
                    _collect_variables_recursive(item, current_func_name, local_offset_ptr)
        elif isinstance(value, ast.AST):
            _collect_variables_recursive(value, current_func_name, local_offset_ptr)

def finalize_assembly(used_routines):
    """Finalizes the assembly code."""
    import sys # Ensure sys is imported for diagnostics
    print(f"DEBUG: Inside finalize_assembly")
    # Check globals here too, although the error is in routines.py
    # print(f"DEBUG: Type of globals in finalize_assembly: {type(globals)}") # This would check built-in globals()
    # print(f"DEBUG: globals() is __builtins__['globals']: {globals() is sys.modules[__name__].__dict__}") # Check if built-in globals() returns current module's dict


    all_needed_routine_names = routines.get_all_required_routines(used_routines)

    final_assembly_code_lines = []
    # The comment ";--------- Start program ---------" is better handled by the caller
    for routine_name in sorted(list(all_needed_routine_names)): # Sort for consistent output
        routine_text = routines.get_routine_by_name(routine_name)
        # Strip leading/trailing whitespace from the whole routine text first
        final_assembly_code_lines.extend(routine_text.strip().splitlines())
    return final_assembly_code_lines

# Note: data_section and end_program are now added by get_all_required_routines
# if they are dependencies of used routines.
# If they should *always* be included, they should be added to the initial set
# passed to finalize_assembly or added unconditionally within finalize_assembly
# after getting dependencies. Let's add them unconditionally here for safety.
def write_assembly_to_file(output_file, assembly_code):
    """Writes the assembly code to a file."""
    if output_file:
        print(f"      Output file specified: {output_file}")
        with open(output_file, "w") as file:
            file.write("\n".join(assembly_code))
            print(f"        Finished writing to {output_file}")
        print(f"Assembly code saved to '{output_file}'.")


def _handle_conversion_error(e, output_file_path, current_used_routines_set):
    """Helper function to handle exceptions during Python to Assembly conversion."""
    import sys # Ensure sys is imported for diagnostics
    import traceback

    # This print confirms the function is entered and shows the original error.
    print(f"DEBUG: _handle_conversion_error received exception: {type(e).__name__}: {e}")

    # Safely check built-in globals() function for debugging purposes if needed later
    # builtins_globals_func = None
    # if hasattr(__builtins__, 'globals'): # For module __builtins__
    #     builtins_globals_func = __builtins__.globals
    # elif isinstance(__builtins__, dict) and 'globals' in __builtins__: # For dict __builtins__
    #     builtins_globals_func = __builtins__['globals']
    #
    # if callable(builtins_globals_func):
    #     # print(f"DEBUG: built-in globals() is available.")
    #     pass
    # else:
    #     print(f"DEBUG: Could not retrieve callable built-in globals(). Type of __builtins__: {type(__builtins__)}")

    error_type_name = type(e).__name__
    # The original error message is already printed by test.py via "Error during execution: {e}"
    # and also by the DEBUG line above.

    print("--- Traceback of the caught error (inside _handle_conversion_error): ---")
    # Use type(e), e, and e.__traceback__ to format the exception that was passed in.
    traceback_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    print(traceback_str)
    print("----------------------------------------------------------------------")

    generate_error_handling_assembly(e)  # Appends to globals.generated_code

    current_used_routines_set.update({
        'error_handler',
        'generic_error_msg',
        'overflow_error_msg',
        'division_by_zero_msg',
        'key_error_msg',
        'print_error_message',
        'global_unhandled_exception_routine' # Aggiungi se può essere chiamata
        # 'data_section' and 'end_program' are added by finalize_assembly
    })

    final_routines_code = finalize_assembly(current_used_routines_set)
    # Use globals.generated_code which now contains main code + error handling lines
    full_assembly_output = [";--------- Start generated code ---------"] + globals.generated_code + final_routines_code
    write_assembly_to_file(output_file_path, full_assembly_output)
    return None


def python_to_assembly(python_code, output_file=None, print_ast=False):
    """Main function for translating Python to Assembly."""
    # local_used_routines is no longer used here; globals.used_routines is used
    globals.clear_variables() # Resets globals like globals.generated_code, globals.memory_pointer etc.

    try:
        tree = ast.parse(python_code)
    except SyntaxError as e:
        globals.report_compiler_error(f"Syntax error: {e}", node=None) # node is not available here
        return None # Or perhaps generate error assembly

    if print_ast:
        print("--- Albero AST ---")
        print(ast.dump(tree, indent=4))
        print("-------------------")

    # total_memory_required = calculate_memory_requirements(tree) # Funzione rimossa o non definita
    # print(f"Memoria totale necessaria: {total_memory_required} bytes")

    try:
        # --- Pass 1: Collect and allocate all variables (globals, params, locals) ---
        for node in tree.body:
            _collect_variables_recursive(node, None, None)


        # --- Pass 1.5: Type Inference ---
        # Initialize all variable and function types before inference.
        # The 'is_float' key is now deprecated in favor of a 'type' string.
        for var_info in globals.variables.values():
            var_info.pop('is_float', None)
            var_info['type'] = 'unknown'
        for func_info in globals.defined_functions.values():
            func_info.pop('is_float_return', None)
            func_info['return_type'] = 'unknown'

        # Run the inference pass in a loop until types stabilize. This handles
        # inter-dependencies between functions.
        max_passes = 10  # Safety break for complex recursive/interdependent types
        for i in range(max_passes):
            types_changed_in_pass = False
            for node in tree.body:
                if _type_inference_visitor(node):
                    types_changed_in_pass = True

            if not types_changed_in_pass:
                break  # Types have stabilized
        else:  # This 'else' belongs to the for-loop, executes if it finishes without break
            globals.report_compiler_error("Type inference did not stabilize. Possible circular type dependency.", level="WARNING")

        # --- Pass 2: Generate Assembly Code --- #
        # Initialize the software stack pointer at the very beginning of the main program.
        globals.generated_code.extend([
            f"    LDA #<{globals.STACK_TOP_ADDRESS:04X}",
            f"    STA ${globals.STACK_POINTER_ZP:02X}",
            f"    LDA #>{globals.STACK_TOP_ADDRESS:04X}",
            f"    STA ${globals.STACK_POINTER_ZP+1:02X}"
        ])
        for node in tree.body:
            if isinstance(node, ast.Assign):
                ast_processor.process_assign_node(node)
            elif isinstance(node, ast.FunctionDef): # NEW ADDITION
                ast_processor.process_function_def_node(node, generate_error_handling_assembly)
            elif isinstance(node, ast.For):
                ast_processor.process_for_node(node, generate_error_handling_assembly)
            elif isinstance(node, ast.While):
                ast_processor.process_while_node(node, generate_error_handling_assembly)
            elif isinstance(node, ast.Delete):
                ast_processor.process_delete_node(node) # Removed error_handler_func, it should handle its own
            elif isinstance(node, ast.Expr):
                ast_processor.process_expr_node(node, generate_error_handling_assembly) # Pass current_func_info if available
            elif isinstance(node, ast.If):
                ast_processor.process_if_node(node, generate_error_handling_assembly)
            elif isinstance(node, ast.Try): # NUOVA AGGIUNTA
                # This is a placeholder for try/except. The current implementation
                # in ast_processor.py only adds a comment.
                # Proper try/except would involve setting up exception handlers.
                ast_processor.process_try_node(node, generate_error_handling_assembly)
            else:
                globals.report_compiler_error(f"Unhandled top-level AST node type: {type(node).__name__}", node=node, level="WARNING")

        # Expand used_routines to include all dependencies BEFORE allocating
        # routine variables and strings.
        expanded_used_routines = routines.get_all_required_routines(globals.used_routines)

        # --- Allocate routine-specific variables and strings based on usage ---
        # This happens after processing all AST nodes to know which routines are used.
        # handle_variable is called to add them to globals.data_definitions.

        # --- Define and initialize floating point constants for routines ---
        fp_constants = {}
        if 'FP_LOG' in expanded_used_routines or 'FP_EXP' in expanded_used_routines:
            fp_constants.update({
                'FP_CONST_ONE': 1.0,
                'FP_CONST_TWO': 2.0,
                'FP_CONST_LN2': 0.693147,
                'FP_CONST_INV_LN2': 1.442695,
            })
        if 'FP_LOG' in expanded_used_routines:
            fp_constants.update({
                'FP_CONST_3': 3.0,
                'FP_CONST_5': 5.0,
                'FP_CONST_7': 7.0,
                'FP_CONST_9': 9.0,
                'FP_CONST_11': 11.0,
            })

        for name, val in fp_constants.items():
            # Ensure the variable is known to the compiler, but don't reserve memory with .res
            # This makes the label available for use in the routines.
            if name not in globals.variables:
                globals.variables[name] = {'type': 'float', 'size': 4}

            # Add the initialized data definition directly.
            woz_bytes = python_float_to_woz_bytes(val)
            byte_str = ", ".join([f"${b:02X}" for b in woz_bytes])
            # Check for duplicates before adding
            if not any(line.strip().startswith(name) for line in globals.data_definitions):
                globals.data_definitions.append(f"{name} {globals.assembly_data_types['byte']} {byte_str}")

        # Variables for error handling and string printing
        if any(routine in expanded_used_routines for routine in ['error_handler', 'print_error_message']):
             handle_variable('error_code', size=1, is_8bit_semantic=True)

        # temp_0 è usato da print_string e da varie routine di messaggi di errore
        if 'print_string' in expanded_used_routines:
            handle_variable('temp_0', size=2) # It's a pointer

        # screen_pointer non è più allocato qui perché print_char non lo usa più.
        # if 'print_string' in expanded_used_routines:
        #     handle_variable('screen_pointer') # Rimosso

        # Variables for mathematical routines
        if 'multiply' in expanded_used_routines:
            handle_variable('multiply_value1', size=1, is_8bit_semantic=True)
            handle_variable('multiply_value2', size=1, is_8bit_semantic=True)
            handle_variable('multiply_result', size=1, is_8bit_semantic=True)
        if 'divide' in expanded_used_routines:
            handle_variable('divide_dividend', size=1, is_8bit_semantic=True)
            handle_variable('divide_divisor',  size=1, is_8bit_semantic=True)
            handle_variable('divide_result',   size=1, is_8bit_semantic=True)

        # Variables for string comparison
        if 'compare_string_const' in expanded_used_routines:
            # compare_string_low_addr and compare_string_high_addr are no longer used as allocatable variables
            handle_variable('result_compare', size=1, is_8bit_semantic=True)

        # Variables for input
        if 'read_string' in expanded_used_routines:
            handle_variable('max_len_input', size=1, is_8bit_semantic=True)
            handle_variable('input_pointer', size=2)

        # Variables for try/except exception handling
        # These should be allocated if the 'try' syntax is used or if routines can raise them.
        handle_variable('exception_handler_active_flag', size=2) # Word for consistency, though only 1 byte used
        handle_variable('current_exception_target_label_ptr', size=2)
        handle_variable('last_exception_type_code', size=1, is_8bit_semantic=True)

        # Ensure the main code terminates correctly
        if globals.generated_code: # Solo se c'è codice generato
            # Check if the last instruction is already a JMP end_program to avoid duplicates
            if not globals.generated_code[-1].strip().upper().startswith("JMP END_PROGRAM"):
                globals.generated_code.append("    JMP end_program")
            globals.used_routines.add('end_program') # Assicura che la routine end_program sia inclusa


        # --- Apply Peephole Optimizations ---
        globals.generated_code = _apply_peephole_optimizations(globals.generated_code)

    except Exception as e:
        # Questo blocco ora catturerà tutte le eccezioni durante la fase di conversione,
        # incluse quelle precedentemente elencate separatamente (TypeError, ValueError, etc.).
        # La logica di gestione differenziata è già incapsulata in _handle_conversion_error
        # e generate_error_handling_assembly.
        return _handle_conversion_error(e, output_file, globals.used_routines)

    # Add fixed error message strings if their routines are used
    if 'generic_error_msg' in expanded_used_routines:
        globals.data_definitions.append(f"error_msg {globals.assembly_data_types['asciiz']} \"Generic error!\"")
    # overflow_error_msg and others now define their strings if used (e.g., in routines.py)
    if 'overflow_error_msg' in expanded_used_routines: # o check_overflow
         globals.data_definitions.append(f"overflow_msg {globals.assembly_data_types['asciiz']} \"Error: Arithmetic overflow!\"")
    if 'division_by_zero_msg' in expanded_used_routines:
         globals.data_definitions.append(f"division_by_zero_msg_string {globals.assembly_data_types['asciiz']} \"Error: Division by zero!\"")
    if 'key_error_msg' in expanded_used_routines:
         globals.data_definitions.append(f"key_error_msg_string {globals.assembly_data_types['asciiz']} \"Error: Key not found!\"")
    if 'value_error_msg' in expanded_used_routines: # Added for ValueError
         globals.data_definitions.append(f"value_error_msg_string {globals.assembly_data_types['asciiz']} \"Error: Invalid value!\"")
    if 'attribute_error_msg' in expanded_used_routines:
        globals.data_definitions.append(f"attribute_error_msg_string {globals.assembly_data_types['asciiz']} \"Error: Attribute not found!\"")
    if 'not_implemented_error_msg' in expanded_used_routines:
        globals.data_definitions.append(f"not_implemented_error_msg_string {globals.assembly_data_types['asciiz']} \"Error: Not implemented!\"")

    # Add chrout definition if print_char (and thus print_string) is used
    if 'print_char' in expanded_used_routines:
        globals.data_definitions.append(f"chrout = {globals.CHROUT_ADDRESS}")

    # Ensure data_section and end_program are always included in the final output

    # Construction of the final output
    # 1. Comment with original Python code
    python_code_comment = [";--------- Start python code ---------"] + \
                          [f"; {line}" for line in python_code.splitlines()] + \
                          [""] # Empty line for separation

    # 2. Entry point e Sezione Dati
    # L'indirizzo di partenza per i dati è INITIAL_MEMORY_POINTER.
    # Le definizioni sono raccolte in globals.data_definitions.
    # Inseriamo un JMP all'inizio del blocco $C100 per saltare al codice principale.
    actual_code_start_label = "main_program_entry_point" # Etichetta per l'inizio del codice

    entry_point_and_data_section = [
        f"    * = ${globals.INITIAL_MEMORY_POINTER:04X}", # ORG per l'entry point
        f"    JMP {actual_code_start_label}",
        "; --- Data Section ---"
    ] + \
        globals.data_definitions + \
        [""] # Empty line for separation

    # 3. Sezione Codice Principale
    # Il codice principale generato è in globals.generated_code.
    # Si assume che questo codice segua la sezione dati.
    main_code_section_output = [f"{actual_code_start_label}:", # Add colon for label definition
                                "; --- Code Section ---"] + \
                               globals.generated_code + \
                               [""] # Riga vuota per separazione

    final_routines_code = finalize_assembly(globals.used_routines) # Passa il set globale

    # 4. Sezione Routine
    # Le routine iniziano a ROUTINES_START.
    routines_section_output = ["; --- Routines Section ---"]
    if final_routines_code: # Aggiungi ORG solo se ci sono routine
        routines_section_output.append(f"    * = ${globals.ROUTINES_START:04X}")
    routines_section_output.extend(final_routines_code)


    # Combina tutte le parti nell'ordine corretto:
    # 1. Commento codice Python
    # 2. Entry point (JMP) e Sezione Dati (iniziano a INITIAL_MEMORY_POINTER)
    # 3. Sezione Codice Principale (segue i dati, inizia con actual_code_start_label)
    # 4. Sezione Routine (inizia a ROUTINES_START)
    full_assembly_output_list = (
        python_code_comment +
        entry_point_and_data_section +
        main_code_section_output +
        routines_section_output
    )

    assembly_string = "\n".join(full_assembly_output_list)
    if not assembly_string.endswith("\n"): # Ensure newline at the end
        assembly_string += "\n"

    write_assembly_to_file(output_file, assembly_string) # Writes the complete string to the temporary file
    return assembly_string # Returns the complete string
