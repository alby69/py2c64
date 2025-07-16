# py2c64/lib/func_strings.py
# Functions for handling strings.

import ast # pyright: ignore[reportMissingModuleSource]
import V1.globals as globals
from lib.func_core import handle_variable, _generate_load_2_bytes_to_zp
import lib.routines

def str_slice(var_name, node):
    """Handles string slicing.""" # pyright: ignore[reportUnusedFunction]
    if isinstance(node.slice, ast.Slice):
        string_var_name = node.value.id  # name of the string
        lower_bound = node.slice.lower.value if node.slice.lower else 0  # if no lower bound, start from 0
        upper_bound = node.slice.upper.value if node.slice.upper else 255  # if no upper bound, max length (255)

        # Check if upper and lower are valid
        if lower_bound >= upper_bound:
            globals.generated_code.append(f"    JSR generic_error_msg")
            return None
        # check if the bounds are correct
        if f"{string_var_name}_str" not in globals.variables: # pragma: no cover
            globals.generated_code.append(f"    JSR generic_error_msg")
            return None
        # Allocate a variable to store the string length at runtime
        globals.handle_variable(f"str_len_{string_var_name}", size=1, is_8bit_semantic=True)
        # Get the original string length (this part seems to calculate it but doesn't use the result effectively for bounds checking)
        globals.generated_code.append(f"    LDX #0")
        globals.generated_code.append(f"check_str_len_{string_var_name}") # Label definition
        globals.generated_code.append(f"    LDA ${globals.variables[f'{string_var_name}_str']['address']:04X},X") # Use address
        globals.generated_code.append(f"    BEQ end_str_len_{string_var_name}") # go out if == 0
        globals.generated_code.append(f"    INX")
        globals.generated_code.append(f"    CPX #255") # Check if max length reached (arbitrary limit)
        globals.generated_code.append(f"    BEQ generic_error_msg") # if == 255 stop with an error
        globals.generated_code.append(f"    JMP check_str_len_{string_var_name}")
        globals.generated_code.append(f"end_str_len_{string_var_name}") # Label definition
        globals.generated_code.append(f"    STX temp_3") # save in temp_3
        globals.generated_code.append(f"    LDA temp_3") # load the correct value
        globals.generated_code.append(f"    STA str_len_{string_var_name}") # save in memory the length

        if lower_bound >= original_string_length or upper_bound > original_string_length or lower_bound < 0 or upper_bound < 0:
                globals.generated_code.append(f"    JSR generic_error_msg")
                return None

        new_string_label = f"{var_name}_str"
        new_string_address = handle_variable(new_string_label)  # new variable for the substring

        # Ensure temp_0, temp_1, temp_3 are allocated
        # temp_0 and temp_1 are handled by _generate_load_2_bytes_to_zp
        handle_variable('temp_3') # Used for string length
        globals.generated_code.extend(_generate_load_2_bytes_to_zp(string_var_name, globals.TEMP_PTR1))
        globals.generated_code.append(f"    LDY #{lower_bound}")

        # Now copy the correct substring to the new variable
        for j in range(lower_bound, upper_bound):
            globals.generated_code.append(f"    LDA (${globals.TEMP_PTR1:02X}),Y ;Load the letter of the string")
            globals.generated_code.append(f"    STA ${new_string_address + j - lower_bound:04X}")
            # Update Y
            globals.generated_code.append(f"    INY")

        # Add 0 at the end
        globals.generated_code.append(f"    LDA #0")
        globals.generated_code.append(f"    STA ${new_string_address + upper_bound - lower_bound:04X}")

        # Save address in var_name
        globals.generated_code.append(f"    LDA #{new_string_address & 0xFF}")  # Low
        globals.generated_code.append(f"    STA {var_name}")  # save in the correct place
        globals.generated_code.append(f"    LDA #{new_string_address >> 8}") # high byte
        globals.generated_code.append(f"    STA {var_name}+1")

        return new_string_label
    else:
        globals.generated_code.append(f"    JSR generic_error_msg")
        return None


def join_str_value(var_name, node):
    """Handles f-strings."""
    # Allocate space for the new f-string result
    string_label = f"{var_name}_str"
    string_address = handle_variable(string_label)

    # 1. Initialize the destination ZP pointer (FSTRING_DEST_ZP_PTR) to string_address (start of var_name_str)
    globals.generated_code.append(f"    LDA #<{string_label} ; LSB of f-string buffer '{string_label}'")
    globals.generated_code.append(f"    STA ${globals.FSTRING_DEST_ZP_PTR:02X}")
    globals.generated_code.append(f"    LDA #>{string_label} ; MSB of f-string buffer '{string_label}'")
    globals.generated_code.append(f"    STA ${globals.FSTRING_DEST_ZP_PTR+1:02X}")

    for part_index, part in enumerate(node.values):
        if isinstance(part, ast.Constant) and isinstance(part.value, str):
            # Constant part of the f-string
            literal_part_label = f"fstr_const_{globals.label_counter}"
            globals.label_counter += 1
            escaped_value = part.value.replace('"', '""')
            globals.data_definitions.append(f"{literal_part_label} {globals.assembly_data_types['asciiz']} \"{escaped_value}\"")
            globals.data_definitions.append(f"          {globals.assembly_data_types['byte']} 0 ; Null terminator for {literal_part_label}")

            globals.generated_code.extend(_generate_load_2_bytes_to_zp(literal_part_label, globals.FSTRING_SRC_ZP_PTR))

        elif isinstance(part, ast.Name) or \
             (isinstance(part, ast.FormattedValue) and isinstance(part.value, ast.Name)):
            # Variable part of the f-string
            var_node = part if isinstance(part, ast.Name) else part.value
            var_id = var_node.id

            if not (var_id in globals.variables):
                globals.report_compiler_error(f"String variable '{var_id}' (which should hold a pointer) not found for f-string.", node=var_node)
                globals.generated_code.append(f"    JSR generic_error_msg")
                globals.used_routines.add('generic_error_msg')
                continue # Skip this part if the variable is invalid

            globals.generated_code.extend(_generate_load_2_bytes_to_zp(var_id, globals.FSTRING_SRC_ZP_PTR))
        else:
            globals.report_compiler_error(f"Unsupported part type {type(part)} in f-string.", node=part)
            globals.generated_code.append(f"    JSR generic_error_msg")
            globals.used_routines.add('generic_error_msg')
            continue

        # Loop di copia per questa parte (costante o variabile)
        globals.used_routines.add('fstr_cat_str')
        globals.generated_code.append("    JSR fstr_cat_str")

    # Add the null terminator at the end of the string
    globals.generated_code.append(f"    LDA #0 ; Null terminator")
    globals.generated_code.append(f"    LDY #0 ; Index for ZP indirect")
    globals.generated_code.append(f"    STA (${globals.FSTRING_DEST_ZP_PTR:02X}),Y ; Write terminator using ZP destination pointer")

    # Save the address of the f-string buffer (string_address) into the Python variable (var_name)
    # Use the label directly for clarity and robustness
    globals.generated_code.append(f"    LDA #<{string_label}")  # Low byte of the buffer address
    globals.generated_code.append(f"    STA {var_name}")
    globals.generated_code.append(f"    LDA #>{string_label}")  # High byte of the buffer address
    globals.generated_code.append(f"    STA {var_name}+1")

    return string_label
