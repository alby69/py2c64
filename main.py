# /workspaces/py2c64/main.py

import ast
import traceback

# Import project modules
import globals
from lib import ast_processor
from lib import func_core
from lib import func_structures
from lib import routines as routine_manager # Renamed for clarity

# Note: Other lib modules like func_expressions, func_operations, etc.,
# are used by ast_processor and don't need to be imported directly here.

# Aliases
gen_code = globals.generated_code
variables = globals.variables
defined_functions = globals.defined_functions
used_routines = globals.used_routines
report_error = globals.report_compiler_error
create_label = func_core.create_label
_get_mangled_local_var_name = func_core._get_mangled_local_var_name
resolve_variable_name = func_core.resolve_variable_name

def _get_type_of_expression(expr_node, current_func_name_context=None):
    """
    Recursively determines the type of a variable or expression.
    This is a simplified type inference engine.
    """
    if isinstance(expr_node, ast.Constant):
        if isinstance(expr_node.value, int):
            return 'int'
        elif isinstance(expr_node.value, float):
            return 'float'
        elif isinstance(expr_node.value, str):
            return 'str'
        elif isinstance(expr_node.value, bool):
            return 'bool'
    elif isinstance(expr_node, ast.Name):
        var_id = expr_node.id
        # Use the new resolver from func_core
        resolved_var_id = resolve_variable_name(var_id, current_func_name_context)
        if resolved_var_id in globals.variables:
            return globals.variables[resolved_var_id].get('type', 'unknown')
        return 'unknown'
    elif isinstance(expr_node, ast.BinOp):
        left_type = _get_type_of_expression(expr_node.left, current_func_name_context)
        right_type = _get_type_of_expression(expr_node.right, current_func_name_context)
        if left_type == 'float' or right_type == 'float':
            return 'float'
        return 'int' # Default for other binary operations
    elif isinstance(expr_node, ast.Call):
        if isinstance(expr_node.func, ast.Name):
            func_name = expr_node.func.id
            if func_name in globals.defined_functions: # Se la funzione è definita dall'utente
                return globals.defined_functions[func_name].get('return_type', 'void')
            # Check for built-in functions that return types
            if func_name == 'int': return 'int'
            if func_name == 'float': return 'float'
            if func_name == 'str': return 'str'
            if func_name == 'input': return 'str'
    elif isinstance(expr_node, ast.Subscript):
        # For now, assume slicing a string returns a string
        value_type = _get_type_of_expression(expr_node.value, current_func_name_context)
        if value_type == 'str':
            return 'str'
    elif isinstance(expr_node, ast.JoinedStr):
        return 'str'
    return 'unknown'

def _collect_variables_recursive(node, current_func_name, local_offset_ptr):
    """
    Recursively traverses the AST to identify all variables and their scopes.
    It assigns memory locations (labels for globals, stack offsets for locals).
    """
    if isinstance(node, ast.Assign):
        # Determine the type of the right-hand side
        rhs_type = _get_type_of_expression(node.value, current_func_name)

        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                is_global = False
                # Check for 'global' keyword declaration within the function scope
                if current_func_name and var_name in defined_functions.get(current_func_name, {}).get('globals', set()):
                    is_global = True

                if current_func_name and not is_global:
                    # It's a local variable or a parameter being reassigned
                    mangled_name = _get_mangled_local_var_name(current_func_name, var_name)
                    if mangled_name not in globals.variables:
                        # This is a new local variable. Assign it a negative offset from FP.
                        local_offset_ptr[0] -= 2 # Assuming 2 bytes for now
                        globals.variables[mangled_name] = {
                            'scope': 'local',
                            'offset': local_offset_ptr[0],
                            'type': rhs_type,
                            'size': 2 # Default size
                        }
                    else:
                        # It's a known local or parameter, just update its type
                        globals.variables[mangled_name]['type'] = rhs_type
                else:
                    # It's a global variable
                    if var_name not in globals.variables:
                        globals.variables[var_name] = {
                            'scope': 'global',
                            'type': rhs_type,
                            'size': 2 # Default size
                        }
                    else:
                        # It's a known global, just update its type
                        # Also ensure scope is set, as it might have been added without one
                        if 'scope' not in globals.variables[var_name]:
                            globals.variables[var_name]['scope'] = 'global'
                        globals.variables[var_name]['type'] = rhs_type

            elif isinstance(target, ast.Subscript):
                # This handles assignments like my_dict['key'] = value
                if isinstance(target.value, ast.Name):
                    dict_name = target.value.id # pyright: ignore[reportAttributeAccessIssue]
                    # Use the new resolver from func_core
                    resolved_var_id = resolve_variable_name(dict_name, current_func_name)
                    if resolved_var_id in globals.variables:
                        # Check if type is changing from its previous state
                        if globals.variables[resolved_var_id].get('type') != rhs_type:
                            globals.variables[resolved_var_id]['type'] = 'dict'
                            # Potentially re-evaluate other properties if needed
                    else:
                        # This case should ideally be handled by a prior declaration
                        # For now, we'll assume it's a global dictionary
                        globals.variables[dict_name] = {'scope': 'global', 'type': 'dict', 'keys': {}}

                    if isinstance(target.slice, ast.Constant) and isinstance(target.slice.value, str):
                        key = target.slice.value
                        if 'keys' not in globals.variables[resolved_var_id]:
                            globals.variables[resolved_var_id]['keys'] = {}
                        # Store info about the key and its type
                        globals.variables[resolved_var_id]['keys'][key] = {'type': rhs_type}

    elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
        var_name = node.id
        if current_func_name:
            mangled_name = _get_mangled_local_var_name(current_func_name, var_name)
            # Check if it's a new local variable. Parameters are handled in FunctionDef.
            if mangled_name not in globals.variables:
                # This is a new local variable. Assign it a negative offset from FP.
                local_offset_ptr[0] -= 2 # Assuming 2 bytes for now
                globals.variables[mangled_name] = {
                    'scope': 'local',
                    'offset': local_offset_ptr[0],
                    'type': 'unknown', # Type will be determined on assignment
                    'size': 2
                }

    elif isinstance(node, ast.FunctionDef):
        func_name = node.name
        # Create labels for the function
        func_label = create_label(f"func_{func_name}", str(globals.label_counter))
        ret_label = create_label(f"func_{func_name}_ret", str(globals.label_counter))
        globals.label_counter += 1

        # Initialize local offset for this function. Use a list for mutable integer.
        local_offset_for_func = [0]
        globals.defined_functions[func_name] = {
            'name': func_name,
            'params': [arg.arg for arg in node.args.args],
            'return_type': 'unknown', # Will be updated by 'return' statements
            'globals': set(), # To store variables declared with 'global'
            'label': func_label,
            'ret_label': ret_label
        }

        # --- Assign offsets for parameters ---
        param_offset_counter = 4
        for arg in node.args.args:
            mangled_param_name = _get_mangled_local_var_name(func_name, arg.arg)
            param_size = 2 # Assume all params are 2 bytes for now
            globals.variables[mangled_param_name] = {
                'scope': 'param', 'offset': param_offset_counter, 'type': 'unknown', 'size': param_size
            }
            param_offset_counter += param_size

        # --- Recursively collect variables inside the function ---
        for child_node in node.body:
            # First, find global declarations
            if isinstance(child_node, ast.Global):
                for name in child_node.names:
                    globals.defined_functions[func_name]['globals'].add(name)
            _collect_variables_recursive(child_node, func_name, local_offset_for_func)

        # After processing the body, determine the function's return type
        for child_node in ast.walk(node):
            if isinstance(child_node, ast.Return):
                return_type = _get_type_of_expression(child_node.value, func_name)
                globals.defined_functions[func_name]['return_type'] = return_type
                break # Assume first return statement dictates the type

    # --- Generic traversal for other node types ---
    else:
        for child_node in ast.iter_child_nodes(node):
            # Pass the current function context down
            _collect_variables_recursive(child_node, current_func_name, local_offset_ptr)


def python_to_assembly(source_code, output_file, error_handler_func):
    """
    Main function to convert a Python script into 6502 assembly.
    """
    # Reset globals for a fresh compilation
    globals.reset_globals()

    def _handle_conversion_error(e, node):
        """
        Centralized error handling during AST processing.
        """
        lineno = getattr(node, 'lineno', 'unknown')
        print(f"DEBUG: _handle_conversion_error received exception: {e}")
        print("--- Traceback of the caught error (inside _handle_conversion_error): ---")
        traceback.print_exc()
        print("----------------------------------------------------------------------")
        error_handler_func(f"Error processing node on line {lineno}: {e}", lineno)
        globals.has_errors = True


    # --- Main execution flow of python_to_assembly ---
    try: # Gestione globale degli errori
        # 1. Analizza il codice Python in un AST
        tree = ast.parse(source_code)

        # 2. Prima Passata: Raccogli tutte le variabili e le funzioni
        _collect_variables_recursive(tree, None, None)

        # 3. Genera il boilerplate iniziale dell'assembly
        gen_code.append(f"; Generated by py2c64 compiler")
        gen_code.append("; --- Python Source Code ---")
        for line in source_code.strip().split('\n'):
            gen_code.append(f"; {line}")
        gen_code.append("; --------------------------")

        gen_code.append("* = $1000") # Start address for code

        # 5. Second Pass: Generate code
        gen_code.append("; --- Main Program and Functions ---")
        gen_code.append("main:")
        current_func_info = None

        for node in tree.body:
            if globals.has_errors: break
            try:
                if isinstance(node, ast.Assign):
                    ast_processor.process_assign_node(node)
                elif isinstance(node, ast.Expr): # Standalone expression (e.g. function call)
                    ast_processor.process_expr_node(node, error_handler_func)
                elif isinstance(node, ast.FunctionDef):
                    ast_processor.process_function_def_node(node, error_handler_func) # This is correct
                elif isinstance(node, ast.If):
                    func_structures.process_if_node(node, error_handler_func)
                elif isinstance(node, ast.For):
                    func_structures.process_for_node(node, error_handler_func)
                elif isinstance(node, ast.While):
                    func_structures.process_while_node(node, error_handler_func)
                elif isinstance(node, ast.Try):
                    ast_processor.process_try_node(node, error_handler_func)
                elif isinstance(node, (ast.Pass, ast.Global, ast.Import, ast.ImportFrom)):
                    pass # Already handled or no code needed
                else:
                    report_error(f"Unsupported top-level statement: {type(node).__name__}", node.lineno)

            except Exception as e:
                _handle_conversion_error(e, node)

    except SyntaxError as e:
        error_handler_func(f"Syntax Error: {e}", e.lineno)
        globals.has_errors = True
    except Exception as e:
        # Catch-all for other unexpected errors during setup
        print("--- Traceback of the caught error (in main try-except): ---")
        traceback.print_exc()
        print("-----------------------------------------------------------")
        error_handler_func(f"An unexpected error occurred: {e}", 0)
        globals.has_errors = True

    # 6. Finalize the assembly output
    if not globals.has_errors:
        # Add RTS at the end of the main program logic
        gen_code.append("rts ; End of main program")

        # --- Assemble the final output string ---
        program_code = gen_code.get_code()

        # --- Data Segment ---
        data_segment_lines = ["\n; --- Data Segment (Variables and Constants) ---"]
        # Global variables (allocated with .res)
        for name, details in sorted(variables.items()):
            if details['scope'] == 'global':
                size = details.get('size', 2)
                data_segment_lines.append(f"{name} .res {size}")
        # String literals and other data definitions
        data_segment_lines.extend(sorted(globals.data_definitions))
        data_segment = "\n".join(data_segment_lines)

        # --- Routines Segment ---
        routines_segment_lines = ["\n; --- Subroutines ---"]
        # Get all required routines, including dependencies
        all_routines_to_include = routine_manager.get_all_required_routines(used_routines)
        for routine_name in sorted(list(all_routines_to_include)):
            routine_code = routine_manager.get_routine_by_name(routine_name)
            if routine_code:
                routines_segment_lines.append(f"\n; Routine: {routine_name}")
                routines_segment_lines.append(routine_code)
            else:
                # This warning should now be rare due to the improved routine loading
                print(f"Warning: Code for routine '{routine_name}' could not be generated.")
        routines_segment = "\n".join(routines_segment_lines)

        # Combine all parts
        final_assembly = f"{program_code}\n{data_segment}\n{routines_segment}\n"

        # Write to file (optional, but useful for debugging)
        with open(output_file, 'w') as f:
            f.write(final_assembly)

        # Return the final string for the test runner
        return final_assembly
    else:
        print("Assembly generation aborted due to errors.")
        return None # Indicate failure

# The command-line interface has been removed as test.py is the primary entry point.
