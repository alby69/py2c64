# func_strings.py
# Functions for handling strings.

import ast # pyright: ignore[reportMissingModuleSource]
from .. import globals as py2asm_globals # pyright: ignore[reportMissingModuleSource]
from .func_core import handle_variable, _generate_load_2_bytes_to_zp
from . import routines

def str_slice(var_name, node):
    """Handles string slicing.""" # pyright: ignore[reportUnusedFunction]
    if isinstance(node.slice, ast.Slice):
        string_var_name = node.value.id  # name of the string
        lower_bound = node.slice.lower.value if node.slice.lower else 0  # if no lower bound, start from 0
        upper_bound = node.slice.upper.value if node.slice.upper else 255  # if no upper bound, max length (255)

        # Check if upper and lower are valid
        if lower_bound >= upper_bound:
            py2asm_globals.generated_code.append(f"    JSR generic_error_msg")
            return None
        # check if the bounds are correct
        if f"{string_var_name}_str" not in py2asm_globals.variables: # pragma: no cover
            py2asm_globals.generated_code.append(f"    JSR generic_error_msg")
            return None
        # Allocate a variable to store the string length at runtime
        py2asm_globals.handle_variable(f"str_len_{string_var_name}", size=1, is_8bit_semantic=True)
        # Get the original string length (this part seems to calculate it but doesn't use the result effectively for bounds checking)
        py2asm_globals.generated_code.append(f"    LDX #0")
        py2asm_globals.generated_code.append(f"check_str_len_{string_var_name}") # Label definition
        py2asm_globals.generated_code.append(f"    LDA ${py2asm_globals.variables[f'{string_var_name}_str']['address']:04X},X") # Use address
        py2asm_globals.generated_code.append(f"    BEQ end_str_len_{string_var_name}") # go out if == 0
        py2asm_globals.generated_code.append(f"    INX")
        py2asm_globals.generated_code.append(f"    CPX #255") # Check if max length reached (arbitrary limit)
        py2asm_globals.generated_code.append(f"    BEQ generic_error_msg") # if == 255 stop with an error
        py2asm_globals.generated_code.append(f"    JMP check_str_len_{string_var_name}")
        py2asm_globals.generated_code.append(f"end_str_len_{string_var_name}") # Label definition
        py2asm_globals.generated_code.append(f"    STX temp_3") # save in temp_3
        py2asm_globals.generated_code.append(f"    LDA temp_3") # load the correct value
        py2asm_globals.generated_code.append(f"    STA str_len_{string_var_name}") # save in memory the length

        if lower_bound >= original_string_length or upper_bound > original_string_length or lower_bound < 0 or upper_bound < 0:
                py2asm_globals.generated_code.append(f"    JSR generic_error_msg")
                return None

        new_string_label = f"{var_name}_str"
        new_string_address = handle_variable(new_string_label)  # new variable for the substring

        # Ensure temp_0, temp_1, temp_3 are allocated
        # temp_0 and temp_1 are handled by _generate_load_2_bytes_to_zp
        handle_variable('temp_3') # Used for string length
        py2asm_globals.generated_code.extend(_generate_load_2_bytes_to_zp(string_var_name, py2asm_globals.TEMP_PTR1))
        py2asm_globals.generated_code.append(f"    LDY #{lower_bound}")

        # Now copy the correct substring to the new variable
        for j in range(lower_bound, upper_bound):
            py2asm_globals.generated_code.append(f"    LDA (${py2asm_globals.TEMP_PTR1:02X}),Y ;Load the letter of the string")
            py2asm_globals.generated_code.append(f"    STA ${new_string_address + j - lower_bound:04X}")
            # Update Y
            py2asm_globals.generated_code.append(f"    INY")

        # Add 0 at the end
        py2asm_globals.generated_code.append(f"    LDA #0")
        py2asm_globals.generated_code.append(f"    STA ${new_string_address + upper_bound - lower_bound:04X}")

        # Save address in var_name
        py2asm_globals.generated_code.append(f"    LDA #{new_string_address & 0xFF}")  # Low
        py2asm_globals.generated_code.append(f"    STA {var_name}")  # save in the correct place
        py2asm_globals.generated_code.append(f"    LDA #{new_string_address >> 8}") # high byte
        py2asm_globals.generated_code.append(f"    STA {var_name}+1")

        return new_string_label
    else:
        py2asm_globals.generated_code.append(f"    JSR generic_error_msg")
        return None


def join_str_value(var_name, node):
    """Handles f-strings."""
    # Allocate space for the new f-string result
    string_label = f"{var_name}_str"
    string_address = handle_variable(string_label)

    # 1. Initialize the destination ZP pointer (FSTRING_DEST_ZP_PTR) to string_address (start of var_name_str)
    py2asm_globals.generated_code.append(f"    LDA #<{string_label} ; LSB of f-string buffer '{string_label}'")
    py2asm_globals.generated_code.append(f"    STA ${py2asm_globals.FSTRING_DEST_ZP_PTR:02X}")
    py2asm_globals.generated_code.append(f"    LDA #>{string_label} ; MSB of f-string buffer '{string_label}'")
    py2asm_globals.generated_code.append(f"    STA ${py2asm_globals.FSTRING_DEST_ZP_PTR+1:02X}")

    for part_index, part in enumerate(node.values):
        if isinstance(part, ast.Constant) and isinstance(part.value, str):
            # Constant part of the f-string
            literal_part_label = f"fstr_const_{py2asm_globals.label_counter}"
            py2asm_globals.label_counter += 1
            escaped_value = part.value.replace('"', '""')
            py2asm_globals.data_definitions.append(f"{literal_part_label} {py2asm_globals.assembly_data_types['asciiz']} \"{escaped_value}\"")
            py2asm_globals.data_definitions.append(f"          {py2asm_globals.assembly_data_types['byte']} 0 ; Null terminator for {literal_part_label}")

            py2asm_globals.generated_code.extend(_generate_load_2_bytes_to_zp(literal_part_label, py2asm_globals.FSTRING_SRC_ZP_PTR))

        elif isinstance(part, ast.Name) or \
             (isinstance(part, ast.FormattedValue) and isinstance(part.value, ast.Name)):
            # Variable part of the f-string
            var_node = part if isinstance(part, ast.Name) else part.value
            var_id = var_node.id

            if not (var_id in py2asm_globals.variables):
                py2asm_globals.report_compiler_error(f"String variable '{var_id}' (which should hold a pointer) not found for f-string.", node=var_node)
                py2asm_globals.generated_code.append(f"    JSR generic_error_msg")
                py2asm_globals.used_routines.add('generic_error_msg')
                continue # Skip this part if the variable is invalid

            py2asm_globals.generated_code.extend(_generate_load_2_bytes_to_zp(var_id, py2asm_globals.FSTRING_SRC_ZP_PTR))
        else:
            py2asm_globals.report_compiler_error(f"Unsupported part type {type(part)} in f-string.", node=part)
            py2asm_globals.generated_code.append(f"    JSR generic_error_msg")
            py2asm_globals.used_routines.add('generic_error_msg')
            continue

        # Loop di copia per questa parte (costante o variabile)
        py2asm_globals.used_routines.add('fstr_cat_str')
        py2asm_globals.generated_code.append("    JSR fstr_cat_str")

    # Add the null terminator at the end of the string
    py2asm_globals.generated_code.append(f"    LDA #0 ; Null terminator")
    py2asm_globals.generated_code.append(f"    LDY #0 ; Index for ZP indirect")
    py2asm_globals.generated_code.append(f"    STA (${py2asm_globals.FSTRING_DEST_ZP_PTR:02X}),Y ; Write terminator using ZP destination pointer")

    # Save the address of the f-string buffer (string_address) into the Python variable (var_name)
    # Use the label directly for clarity and robustness
    py2asm_globals.generated_code.append(f"    LDA #<{string_label}")  # Low byte of the buffer address
    py2asm_globals.generated_code.append(f"    STA {var_name}")
    py2asm_globals.generated_code.append(f"    LDA #>{string_label}")  # High byte of the buffer address
    py2asm_globals.generated_code.append(f"    STA {var_name}+1")

    return string_label
