# /workspaces/py2c64/main.py

import ast
import argparse
import os
import traceback

# Import project modules
from . import globals
from .lib import ast_processor
from .lib import func_core
from .lib import func_expressions
from .lib import func_operations
from .lib import func_dict
from .lib import func_c64
from .lib import func_structures
from .lib import c64_routine_library

# Aliases
gen_code = globals.generated_code
variables = globals.variables
functions = globals.functions
used_routines = globals.used_routines
report_error = globals.report_compiler_error
create_label = func_core.create_label
resolve_variable_name = func_core.resolve_variable_name
_get_mangled_local_var_name = func_core._get_mangled_local_var_name

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
            if func_name in globals.functions:
                return globals.functions[func_name].get('return_type', 'void')
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
                if current_func_name and var_name in functions.get(current_func_name, {}).get('globals', set()):
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
                        globals.variables[var_name]['type'] = rhs_type

            elif isinstance(target, ast.Subscript):
                # This handles assignments like my_dict['key'] = value
                if isinstance(target.value, ast.Name):
                    dict_name = target.value.id
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
        # Initialize local offset for this function. Use a list for mutable integer.
        local_offset_for_func = [0]
        globals.functions[func_name] = {
            'name': func_name,
            'params': [arg.arg for arg in node.args.args],
            'return_type': 'unknown', # Will be updated by 'return' statements
            'globals': set() # To store variables declared with 'global'
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
                    globals.functions[func_name]['globals'].add(name)
            _collect_variables_recursive(child_node, func_name, local_offset_for_func)

        # After processing the body, determine the function's return type
        for child_node in ast.walk(node):
            if isinstance(child_node, ast.Return):
                return_type = _get_type_of_expression(child_node.value, func_name)
                globals.functions[func_name]['return_type'] = return_type
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


    def generate_error_handling_assembly():
        """
        Generates assembly code for runtime error handling.
        """
        # This is a placeholder for more sophisticated error handling
        if not globals.error_handler_generated:
            gen_code.add_code("value_error_msg:")
            gen_code.add_code('    .byte "ValueError", 0')
            # Add more error types as needed
            globals.error_handler_generated = True


    def finalize_assembly():
        nonlocal output_file
        print("DEBUG: Inside finalize_assembly")
        # Add RTS at the end of the main program logic
        if globals.current_scope == 'global':
            gen_code.add_code("rts") # for the main program

        # Include required C64 routines based on usage
        for routine_name in sorted(list(globals.used_routines)): # Sort for consistent output
            routine_code = c64_routine_library.get_routine_code(routine_name)
            if routine_code:
                gen_code.add_lines(routine_code)
            else:
                # Don't warn for FP routines, they are in an external file
                if not routine_name.startswith("FP_") and not routine_name == "load_one_fp1":
                    print(f"Warning: Routine '{routine_name}' not found in routine library.")

        gen_code.add_code("")
        gen_code.add_code("; *** End of generated code ***")

        # Generate the final assembly code
        output_code = gen_code.get_code()
        with open(output_file, 'w') as f:
            f.write(output_code)
        print(f"Assembly code saved to '{output_file}'.")


    # --- Main execution flow of python_to_assembly ---
    try:
        # 1. Parse the Python code into an AST
        tree = ast.parse(source_code)

        # 2. First Pass: Collect all variables and functions
        _collect_variables_recursive(tree, None, None)

        # 3. Generate initial assembly boilerplate
        gen_code.add_code("; Generated by py2c64 compiler")
        gen_code.add_code("* = $1000") # Start address for code
        gen_code.add_code("jmp main")
        gen_code.add_code("")

        # 4. Generate data segment for global variables
        gen_code.add_code("; --- Global Variables ---")
        for name, details in variables.items():
            if details['scope'] == 'global':
                if details.get('type') == 'str':
                    # For strings, we allocate space for a pointer
                    gen_code.add_code(f"{name}: .word 0 ; string pointer")
                elif details.get('type') == 'dict':
                    # For dicts, also a pointer
                    gen_code.add_code(f"{name}: .word 0 ; dict pointer")
                else:
                    # For numbers, allocate 2 bytes
                    gen_code.add_code(f"{name}: .word 0")
        gen_code.add_code("")


        # 5. Second Pass: Generate code
        gen_code.add_code("; --- Main Program and Functions ---")
        gen_code.add_code("main:")
        current_func_info = None

        for node in tree.body:
            if globals.has_errors: break
            try:
                if isinstance(node, ast.Assign):
                    ast_processor.process_assign_node(node)
                elif isinstance(node, ast.Expr):
                    ast_processor.process_expr_node(node, generate_error_handling_assembly)
                elif isinstance(node, ast.FunctionDef):
                    ast_processor.process_function_def_node(node)
                elif isinstance(node, ast.If):
                    ast_processor.process_if_node(node)
                elif isinstance(node, ast.For):
                    ast_processor.process_for_node(node)
                elif isinstance(node, ast.While):
                    ast_processor.process_while_node(node)
                elif isinstance(node, ast.Try):
                    ast_processor.process_try_node(node, generate_error_handling_assembly)
                elif isinstance(node, (ast.Pass, ast.Global)):
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


    # 6. Finalize the assembly file
    if not globals.has_errors:
        finalize_assembly()
    else:
        print("Assembly generation aborted due to errors.")


def main():
    """
    Command-line interface for the compiler.
    """
    parser = argparse.ArgumentParser(description='Compile Python to 6502 assembly.')
    parser.add_argument('source_file', help='The Python source file to compile.')
    parser.add_argument('-o', '--output', help='The output assembly file name.')
    args = parser.parse_args()

    source_file = args.source_file
    if not os.path.exists(source_file):
        print(f"Error: Source file '{source_file}' not found.")
        return

    output_file = args.output
    if not output_file:
        base_name = os.path.splitext(source_file)[0]
        output_file = base_name + '.asm'

    with open(source_file, 'r') as f:
        source_code = f.read()

    def cli_error_handler(message, lineno):
        print(f"Error on line {lineno}: {message}")

    python_to_assembly(source_code, output_file, cli_error_handler)

if __name__ == '__main__':
    main()
