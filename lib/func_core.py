# func_core.py
# Core utility functions for variable management, label creation, and code generation.

import ast
from .. import globals as py2asm_globals # Import the globals module with an alias

def _get_mangled_local_var_name(func_name, var_name):
    """Mangles a local variable name with its function scope."""
    return f"__{func_name}_{var_name}"

def resolve_variable_name(var_name, current_func_name=None):
    """
    Resolves a variable name to its mangled form if it's a local or parameter,
    otherwise returns the original name for global variables.
    """
    if current_func_name:
        # It's important to check if the mangled name actually exists in the variables table.
        # A variable with the same name could be global.
        mangled_name = _get_mangled_local_var_name(current_func_name, var_name)
        if mangled_name in py2asm_globals.variables:
            return mangled_name
    # If not in a function context, or if the mangled name wasn't found,
    # assume it's a global variable and return the original name.
    return var_name

def get_current_func_name(current_func_info):
    """
    Safely gets the current function name from the info dictionary.
    """
    return current_func_info.get('name') if current_func_info else None


def _generate_copy_2_bytes(source, dest):
    """Generates assembly to copy 2 bytes (a word) from source to dest.
    Source and dest can be variable names (str) or direct ZP addresses (int).
    """
    source_l = f"{source}" if isinstance(source, str) else f"${source:02X}"
    source_h = f"{source}+1" if isinstance(source, str) else f"${source+1:02X}"
    dest_l = f"{dest}" if isinstance(dest, str) else f"${dest:02X}"
    dest_h = f"{dest}+1" if isinstance(dest, str) else f"${dest+1:02X}"

    return [
        f"    LDA {source_l}",
        f"    STA {dest_l}",
        f"    LDA {source_h}",
        f"    STA {dest_h}",
    ]


def _generate_copy_4_bytes(source_var_name, dest_var_name):
    """Generates assembly to copy 4 bytes from one variable to another."""
    return [
        f"    LDA {source_var_name}+0", f"    STA {dest_var_name}+0",
        f"    LDA {source_var_name}+1", f"    STA {dest_var_name}+1",
        f"    LDA {source_var_name}+2", f"    STA {dest_var_name}+2",
        f"    LDA {source_var_name}+3", f"    STA {dest_var_name}+3",
    ]

def handle_variable(var_name, size=None, is_8bit_semantic=None, var_type=None):
    """
    Allocates memory for a variable if it's not already allocated.
    This function is now generic and relies on passed parameters or pre-set
    information in globals.variables, rather than name-based patterns.
    """ # Removed 'global memory_pointer' as it's from another module
    if var_name in py2asm_globals.variables and 'address' in py2asm_globals.variables[var_name]: # Access py2asm_globals.variables
        # Already allocated.
        return py2asm_globals.variables[var_name]['address']

    # If not in py2asm_globals.variables at all, create an entry.
    if var_name not in py2asm_globals.variables:
        py2asm_globals.variables[var_name] = {} # Access py2asm_globals.variables

    # --- Determine allocation size ---
    # Priority: 1. Explicit `size` parameter, 2. Existing `size` in globals, 3. Default.
    alloc_size = size # Can be specified as argument to handle_variable
    if alloc_size is None:
        alloc_size = py2asm_globals.variables[var_name].get('size') # Access py2asm_globals.variables
    if alloc_size is None:
        # Default size for a variable if not specified (e.g., a standard integer).
        alloc_size = 2
        if 'type' not in py2asm_globals.variables[var_name]:
            py2asm_globals.variables[var_name]['type'] = 'int' # Access py2asm_globals.variables

    # --- Update metadata in globals.variables ---
    py2asm_globals.variables[var_name]['size'] = alloc_size # Access py2asm_globals.variables
    if is_8bit_semantic is not None:
        py2asm_globals.variables[var_name]['is_8bit_semantic'] = is_8bit_semantic
    if var_type is not None:
        py2asm_globals.variables[var_name]['type'] = var_type

    # --- Allocate memory and create data definition ---
    address = py2asm_globals.memory_pointer # Access py2asm_globals.memory_pointer
    # Check for memory overflow
    if py2asm_globals.memory_pointer + alloc_size > py2asm_globals.MAX_MEMORY: # Access py2asm_globals.MAX_MEMORY
        py2asm_globals.report_compiler_error(f"Out of memory allocating variable '{var_name}' (size {alloc_size}).", level="ERROR") # Access py2asm_globals.report_compiler_error
        # This is a fatal error. In a real compiler, this would stop compilation.
        return None

    py2asm_globals.memory_pointer += alloc_size # Access py2asm_globals.memory_pointer
    py2asm_globals.variables[var_name]['address'] = address

    res_directive = py2asm_globals.assembly_data_types['res']
    # Handle CBM Prg Studio's special syntax for reserving memory.
    if res_directive.strip() == '*':
        py2asm_globals.data_definitions.append(f"{var_name} {res_directive} = * + {alloc_size}")
    else:
        py2asm_globals.data_definitions.append(f"{var_name} {res_directive} {alloc_size}")

    return address


def create_label(base_name, unique_id):
    """Creates a unique assembly label."""
    return f"{base_name}_{unique_id}"


def get_temp_var():
    """Gets a temporary variable, allocating it with max size (4 bytes for float).
    Prioritizes reusing released variables from the pool.
    """
    if py2asm_globals.temp_var_pool:
        var_name = py2asm_globals.temp_var_pool.pop() # Reuse from pool
        py2asm_globals.temp_variables[var_name] = True # Mark as in use
        # No need to call handle_variable again, as its memory is already allocated.
        # handle_variable checks if already allocated.
        return var_name
    else:
        # Generate a new unique name using the counter from py2asm_globals
        var_name = f"temp_{py2asm_globals.temp_var_counter}"
        py2asm_globals.temp_var_counter += 1
        py2asm_globals.temp_variables[var_name] = True
        # Temp vars can hold anything, so allocate enough for a float.
        handle_variable(var_name, size=4, var_type='any')
        return var_name

def _generate_load_2_bytes_to_zp(source_var_name, dest_zp_addr):
    """Generates assembly to load 2 bytes (a pointer) from a variable to a zero-page address."""
    return [
        f"    LDA {source_var_name}+0",
        f"    STA ${dest_zp_addr:02X}",
        f"    LDA {source_var_name}+1",
        f"    STA ${dest_zp_addr+1:02X}",
    ]

def load_ax_from_var(var_name):
    """Generates code to load a 16-bit variable into A/X registers."""
    py2asm_globals.generated_code.add_code(f"    ldx {var_name}")       # LSB
    py2asm_globals.generated_code.add_code(f"    lda {var_name}+1")     # MSB

def store_ax_in_var(var_name):
    """Generates code to store A/X registers into a 16-bit variable."""
    py2asm_globals.generated_code.add_code(f"    stx {var_name}")       # LSB
    py2asm_globals.generated_code.add_code(f"    sta {var_name}+1")     # MSB

def load_a_from_var(var_name):
    """Generates code to load an 8-bit variable into A register."""
    py2asm_globals.generated_code.add_code(f"    lda {var_name}")

def store_a_in_var(var_name):
    """Generates code to store A register into an 8-bit variable."""
    py2asm_globals.generated_code.add_code(f"    sta {var_name}")

def load_x_from_var(var_name):
    """Generates code to load an 8-bit variable into X register."""
    py2asm_globals.generated_code.add_code(f"    ldx {var_name}")

def store_x_in_var(var_name):
    """Generates code to store X register into an 8-bit variable."""
    py2asm_globals.generated_code.add_code(f"    stx {var_name}")

def load_y_from_var(var_name):
    """Generates code to load an 8-bit variable into Y register."""
    py2asm_globals.generated_code.add_code(f"    ldy {var_name}")

def store_y_in_var(var_name):
    """Generates code to store Y register into an 8-bit variable."""
    py2asm_globals.generated_code.add_code(f"    sty {var_name}")

def load_fp1_from_var(var_name):
    """
    Generates code to load a 4-byte float from a variable into FP1.
    This is a convenience wrapper around _generate_load_float_to_fp1.
    """
    py2asm_globals.generated_code.add_lines("\n".join(_generate_load_float_to_fp1(var_name)))

def store_fp1_in_var(var_name):
    """
    Generates code to store a 4-byte float from FP1 into a variable.
    This is a convenience wrapper around _generate_store_float_from_fp1.
    """
    py2asm_globals.generated

def _generate_store_2_bytes_from_zp(source_zp_addr, dest_var_name):
    """Generates assembly to store 2 bytes (a pointer) from a zero-page address to a variable."""
    return [
        f"    LDA ${source_zp_addr:02X}",
        f"    STA {dest_var_name}+0",
        f"    LDA ${source_zp_addr+1:02X}",
        f"    STA {dest_var_name}+1",
    ]


def _generate_load_float_to_fp1(source_var_name):
    """Generates assembly to load a 4-byte float from a variable into FP1."""
    return [
        f"    LDA {source_var_name}+3",      # Exponent
        f"    STA ${py2asm_globals.WOZ_FP_X1:02X}",
        f"    LDA {source_var_name}+0",      # Mantissa LSB
        f"    STA ${py2asm_globals.WOZ_FP_M1:02X}",
        f"    LDA {source_var_name}+1",
        f"    STA ${py2asm_globals.WOZ_FP_M1+1:02X}",
        f"    LDA {source_var_name}+2",      # Mantissa MSB
        f"    STA ${py2asm_globals.WOZ_FP_M1+2:02X}",
    ]


def _generate_load_float_to_fp2(source_var_name):
    """Generates assembly to load a 4-byte float from a variable into FP2."""
    return [
        f"    LDA {source_var_name}+3",      # Exponent
        f"    STA ${py2asm_globals.WOZ_FP_X2:02X}",
        f"    LDA {source_var_name}+0",      # Mantissa LSB
        f"    STA ${py2asm_globals.WOZ_FP_M2:02X}",
        f"    LDA {source_var_name}+1",
        f"    STA ${py2asm_globals.WOZ_FP_M2+1:02X}",
        f"    LDA {source_var_name}+2",      # Mantissa MSB
        f"    STA ${py2asm_globals.WOZ_FP_M2+2:02X}",
    ]


def release_temp_var(var_name):
    """Releases a temporary variable for reuse.""" # Access py2asm_globals.temp_variables
    if var_name in py2asm_globals.temp_variables:
        del py2asm_globals.temp_variables[var_name]
        py2asm_globals.temp_var_pool.append(var_name) # Add to pool for reuse
    else:
        py2asm_globals.report_compiler_error(f"Attempted to release non-active temporary variable '{var_name}'.", level="WARNING")


def type_value(var_name, node):
    """Generates code to assign a constant value to a variable and allocates it."""
    if not isinstance(node, ast.Constant):
        py2asm_globals.report_compiler_error(f"Internal Error: type_value expects ast.Constant node, got {type(node).__name__}.", level="ERROR")
        return # Do not proceed with invalid node type

    # Ensure the variable is allocated with a default size/type if not already.
    # This is important for constants that might be assigned to variables without prior declaration.
    handle_variable(var_name)

    value = node.value
    if isinstance(value, (int, bool)): # Access py2asm_globals.generated_code
        # Allocate variable and generate code for integer assignment
        py2asm_globals.variables[var_name]['size'] = 2
        py2asm_globals.variables[var_name]['type'] = 'int'
        py2asm_globals.variables[var_name]['is_8bit_semantic'] = True
        py2asm_globals.generated_code.extend([
            f"    LDA #{value & 0xFF}",
            f"    STA {var_name}",
            f"    LDA #{(value >> 8) & 0xFF}",
            f"    STA {var_name}+1"
        ])
    elif isinstance(value, float):
        py2asm_globals.variables[var_name]['size'] = 4
        py2asm_globals.variables[var_name]['type'] = 'float'
        py2asm_globals.variables[var_name]['is_8bit_semantic'] = False # Floats are not 8-bit semantic
        # Convert Python float to Wozniak FP bytes and store directly
        woz_bytes = python_float_to_woz_bytes(value)
        for i, byte_val in enumerate(woz_bytes):
            py2asm_globals.generated_code.append(f"    LDA #${byte_val:02X}")
            py2asm_globals.generated_code.append(f"    STA {var_name}+{i}")
    elif isinstance(value, str):
        # Create a string literal in data_definitions and store its address (pointer) in var_name.
        string_literal_label = f"str_lit_{py2asm_globals.label_counter}"
        py2asm_globals.label_counter += 1
        escaped_value = value.replace('"', '""') # Basic escape for assembly string
        py2asm_globals.data_definitions.append(f"{string_literal_label} {py2asm_globals.assembly_data_types['asciiz']} \"{escaped_value}\"")

        py2asm_globals.variables[var_name]['size'] = 2 # Pointers are 2 bytes
        py2asm_globals.variables[var_name]['type'] = 'pointer'
        py2asm_globals.variables[var_name]['is_8bit_semantic'] = False # Pointers are 16-bit semantic

        # Store the address of the string literal into 'var_name'
        py2asm_globals.generated_code.append(f"    LDA #<{string_literal_label}")
        py2asm_globals.generated_code.append(f"    STA {var_name}")
        py2asm_globals.generated_code.append(f"    LDA #>{string_literal_label}")
        py2asm_globals.generated_code.append(f"    STA {var_name}+1")
    else:
        py2asm_globals.report_compiler_error(f"Unsupported constant type '{type(value).__name__}' for assignment to '{var_name}'.", level="ERROR")


def python_float_to_woz_bytes(py_float):
    """
    Converts a Python float to a 4-byte Wozniak floating-point representation.
    This is a simplified conversion and might not be perfectly accurate for all values.
    A proper Wozniak FP conversion is complex and involves specific normalization rules.
    For now, this provides a basic approximation for common values.
    """
    # Wozniak FP: Byte 0: Exponent (biased by 128, MSB is sign of mantissa)
    # Byte 1-3: Mantissa (24-bit, implicit leading 1, normalized to 0.5 to <1.0)
    # Example: 1.0 is $81 $40 $00 $00
    # 0.5 is $80 $40 $00 $00
    # 2.0 is $82 $40 $00 $00
    # -1.0 is $81 $C0 $00 $00

    # This is a placeholder. For accurate conversion, a dedicated library or
    # a more complex algorithm is needed.
    # For now, we use a very basic direct mapping for common floats.
    # Memory layout is [LSB_MANT, MID_MANT, MSB_MANT, EXP].
    if py_float == 0.0: return [0x00, 0x00, 0x00, 0x00]
    if py_float == 1.0: return [0x00, 0x00, 0x40, 0x81]
    if py_float == -1.0: return [0x00, 0x00, 0xC0, 0x81]
    if py_float == 2.0: return [0x00, 0x00, 0x40, 0x82]
    if py_float == 0.5: return [0x00, 0x00, 0x40, 0x80]
    if py_float == 3.14: return [0x5C, 0x8F, 0x64, 0x82] # Approximation
    if py_float == 1.5: return [0x00, 0x00, 0x60, 0x81]
    if py_float == -0.25: return [0x00, 0x00, 0xC0, 0x7E]
    if py_float == 2.718: return [0x00, 0x00, 0x56, 0x82] # Approximation
    if py_float == 3.5: return [0x00, 0x00, 0x70, 0x82]
    # Constants for LOG and EXP routines
    if py_float == 3.0: return [0x00, 0x00, 0x60, 0x82]
    if py_float == 5.0: return [0x00, 0x00, 0x50, 0x83]
    if py_float == 7.0: return [0x00, 0x00, 0x70, 0x83]
    if py_float == 9.0: return [0x00, 0x00, 0x48, 0x84]
    if py_float == 11.0: return [0x00, 0x00, 0x58, 0x84]
    if py_float == 0.693147: return [0x9E, 0xE0, 0x58, 0x80] # ln(2)
    if py_float == 1.442695: return [0x1F, 0x85, 0x5B, 0x81] # 1/ln(2)
    py2asm_globals.report_compiler_error(f"Float literal {py_float} conversion to Wozniak FP is not precisely implemented. Using 0.0.", level="WARNING")
    return [0x00, 0x00, 0x00, 0x00]

def _generate_store_float_from_fp1(dest_var_name):
    """Generates assembly to store a 4-byte float from FP1 into a variable."""
    return [
        f"    LDA ${py2asm_globals.WOZ_FP_X1:02X}",
        f"    STA {dest_var_name}+3",        # Exponent
        f"    LDA ${py2asm_globals.WOZ_FP_M1:02X}",
        f"    STA {dest_var_name}+0",        # Mantissa LSB
        f"    LDA ${py2asm_globals.WOZ_FP_M1+1:02X}",
        f"    STA {dest_var_name}+1",
        f"    LDA ${py2asm_globals.WOZ_FP_M1+2:02X}",
        f"    STA {dest_var_name}+2",        # Mantissa MSB
    ]

def handle_input(var_name):
    """Placeholder for input() handling."""
    pass
def _generate_int_to_float_conversion(source, dest):
    """Generates assembly to convert a 16-bit integer (source) to a 4-byte float (dest)."""
    py2asm_globals.generated_code.append(f"    LDA {source}")
    py2asm_globals.generated_code.append(f"    STA ${py2asm_globals.WOZ_FP_M1+2:02X}") # LSB of int to LSB of FP mantissa
    py2asm_globals.generated_code.append(f"    LDA {source}+1")
    py2asm_globals.generated_code.append(f"    STA ${py2asm_globals.WOZ_FP_M1+1:02X}") # MSB of int to MID of FP mantissa
    py2asm_globals.generated_code.append(f"    LDA #0") # Clear MSB of mantissa (for positive int)
    py2asm_globals.generated_code.append(f"    STA ${py2asm_globals.WOZ_FP_M1:02X}")
    py2asm_globals.generated_code.append(f"    JSR FP_FLOAT") # Convert to float
    py2asm_globals.used_routines.add('FP_FLOAT')
    # Result is in X1/M1, copy to dest
    for i in range(4):
        py2asm_globals.generated_code.append(f"    LDA ${py2asm_globals.WOZ_FP_X1+i:02X}")
        py2asm_globals.generated_code.append(f"    STA {dest}+{i}")

def _generate_float_to_int_conversion(source, dest):
    """Generates assembly to convert a 4-byte float (source) to a 16-bit integer (dest)."""
    # Load float from source into X1/M1 # Access py2asm_globals.generated_code, py2asm_globals.WOZ_FP_X1
    for i in range(4):
        py2asm_globals.generated_code.append(f"    LDA {source}+{i}")
        py2asm_globals.generated_code.append(f"    STA ${py2asm_globals.WOZ_FP_X1+i:02X}")
    py2asm_globals.generated_code.append(f"    JSR FP_FIX") # Convert to integer
    py2asm_globals.used_routines.add('FP_FIX')
    # Result is in M1, M1+1. Copy to dest.
    py2asm_globals.generated_code.append(f"    LDA ${py2asm_globals.WOZ_FP_M1+1:02X}") # MSB of integer
    py2asm_globals.generated_code.append(f"    STA {dest}+1")
    py2asm_globals.generated_code.append(f"    LDA ${py2asm_globals.WOZ_FP_M1+2:02X}") # LSB of integer
    py2asm_globals.generated_code.append(f"    STA {dest}")

def _copy_variable_content(source_var_name, dest_var_name, current_func_name=None):
    """
    Generates assembly code to copy the content of source_var_name to dest_var_name.
    Assumes both variables are already allocated and their types/sizes are in globals.variables.
    Handles type coercion if necessary (e.g., int to float, float to int).
    """
    source_info = py2asm_globals.variables.get(source_var_name)
    dest_info = py2asm_globals.variables.get(dest_var_name)

    if not source_info or not dest_info:
        py2asm_globals.report_compiler_error(f"Internal Error: Cannot copy. Source '{source_var_name}' or destination '{dest_var_name}' variable info missing.", level="ERROR")
        return

    source_type = source_info.get('type', 'unknown')
    dest_type = dest_info.get('type', 'unknown')
    source_size = source_info.get('size', 2) # Default to 2 bytes
    dest_size = dest_info.get('size', 2) # Default to 2 bytes

    # Handle type coercion (int <-> float)
    if source_type == 'int' and dest_type == 'float': # Access py2asm_globals.generated_code
        _generate_int_to_float_conversion(source_var_name, dest_var_name)
        return
    elif source_type == 'float' and dest_type == 'int': # Access py2asm_globals.generated_code
        _generate_float_to_int_conversion(source_var_name, dest_var_name)
        return

    # Use helper functions for direct byte copying
    if source_size == 2 and dest_size == 2:
        py2asm_globals.generated_code.extend(_generate_copy_2_bytes(source_var_name, dest_var_name))
    elif source_size == 4 and dest_size == 4:
        py2asm_globals.generated_code.extend(_generate_copy_4_bytes(source_var_name, dest_var_name))
    else:
        # Fallback for mixed sizes or unknown types, copy minimum bytes
        bytes_to_copy = min(source_size, dest_size)
        for i in range(bytes_to_copy):
            py2asm_globals.generated_code.append(f"    LDA {source_var_name}+{i}")
            py2asm_globals.generated_code.append(f"    STA {dest_var_name}+{i}")

def process_print_call(call_node, error_handler_func, current_func_info, func_expressions_module):
    """
    Processes a print() function call.
    Assumes print takes one argument for now.
    """
    if not call_node.args:
        # print() with no arguments, print a newline
        py2asm_globals.generated_code.append(f"    LDA #$0D ; ASCII for Carriage Return")
        py2asm_globals.generated_code.append(f"    JSR print_char")
        py2asm_globals.used_routines.add('print_char')
        return

    # For simplicity, handle only the first argument
    arg_node = call_node.args[0]

    if isinstance(arg_node, ast.Constant) and isinstance(arg_node.value, str):
        # Handle string literal: create a label for the string and print it
        string_literal_label = f"print_str_lit_{py2asm_globals.label_counter}"
        py2asm_globals.label_counter += 1
        escaped_value = arg_node.value.replace('"', '""')
        py2asm_globals.data_definitions.append(f"{string_literal_label} {py2asm_globals.assembly_data_types['asciiz']} \"{escaped_value}\"")

        py2asm_globals.generated_code.append(f"    LDA #<{string_literal_label}")
        py2asm_globals.generated_code.append(f"    STA temp_0")
        py2asm_globals.generated_code.append(f"    LDA #>{string_literal_label}")
        py2asm_globals.generated_code.append(f"    STA temp_0+1")
        py2asm_globals.generated_code.append(f"    JSR print_string")
        py2asm_globals.used_routines.add('print_string')
    else:
        # Handle variable or expression: evaluate it into a temp var, then print it
        temp_var_for_print = get_temp_var()
        func_expressions_module.translate_expression_recursive(temp_var_for_print, arg_node, current_func_info.get('name') if current_func_info else None)
        # Assuming temp_var_for_print holds a pointer to a string for print.
        # This needs more robust type checking. For now, assume it's a string pointer.
        py2asm_globals.generated_code.append(f"    LDA {temp_var_for_print}")
        py2asm_globals.generated_code.append(f"    STA temp_0")
        py2asm_globals.generated_code.append(f"    LDA {temp_var_for_print}+1")
        py2asm_globals.generated_code.append(f"    STA temp_0+1")
        py2asm_globals.generated_code.append(f"    JSR print_string")
        py2asm_globals.used_routines.add('print_string')
        release_temp_var(temp_var_for_print)
