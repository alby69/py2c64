# func_structures.py
# Functions for handling data structures (lists, tuples, sets).

import ast # pyright: ignore[reportMissingModuleSource]
from .. import globals as py2asm_globals # pyright: ignore[reportMissingModuleSource] # Use an alias to avoid conflicts
from .func_core import handle_variable, _generate_copy_2_bytes
from . import routines


def list_value(var_name, value):
    """Handles list assignment."""
    # var_name is the name of the Python variable that will hold the pointer to the list.
    # Space for the list data is allocated with a derived name, e.g., var_name_list_data.
    # Here, for simplicity, we continue to use 'var_name' as the basis for allocating list data,
    # but it's important to distinguish that 'var_name' in Python code will be a pointer.

    list_data_label = f"{var_name}_data" # Label for the actual list data
    list_data_start_address = handle_variable(list_data_label) # Allocate space for the data
    if list_data_start_address is None: return None

    # The variable 'var_name' (which will be the pointer) must be allocated.
    handle_variable(var_name)
    py2asm_globals.variables[var_name]['is_8bit_semantic'] = False # A list pointer is 16-bit

    # the pointer to the list is the next free position
    # The variables {var_name}_ptr_meta and {var_name}_len_meta are for list metadata
    handle_variable(f"{var_name}_ptr_meta")
    py2asm_globals.variables[f"{var_name}_ptr_meta"]['is_8bit_semantic'] = False # Pointer
    handle_variable(f"{var_name}_len_meta")
    py2asm_globals.variables[f"{var_name}_len_meta"]['is_8bit_semantic'] = True # Length < 256

    # Save each value of the list
    for i, element in enumerate(value.elts):
        if isinstance(element, ast.Constant):
            py2asm_globals.generated_code.append(f"    LDA #{element.value}") # Assuming 8-bit elements
        elif isinstance(element, ast.Name):
            py2asm_globals.generated_code.append(f"    LDA {element.id}") # Assuming 8-bit elements
        else:
            raise TypeError(f"Element type {type(element)} not supported inside a list")
        py2asm_globals.generated_code.append(f"    STA ${list_data_start_address + i:04X}")

    # Set the 'var_name' pointer to the address of the list data
    py2asm_globals.generated_code.extend(_generate_copy_2_bytes(list_data_label, var_name))
    py2asm_globals.generated_code.extend(_generate_copy_2_bytes(var_name, f"{var_name}_ptr_meta"))
    py2asm_globals.generated_code.append(f"    LDA #{len(value.elts)}")
    py2asm_globals.generated_code.append(f"    STA {var_name}_len_meta")
    py2asm_globals.generated_code.append(f"    LDA #0") # MSB of length (assuming length < 256)
    py2asm_globals.generated_code.append(f"    STA {var_name}_len_meta+1")

    return list_data_start_address # Returns the raw list data address


def tuple_value(var_name, value):
    """Handles tuple assignment (similar to lists)."""
    return list_value(var_name, value)


def set_value(var_name, value):
    """Handles set assignment (similar to lists)."""
    return list_value(var_name, value)


def diz_value(var_name, node):
    """Handles dictionary assignment."""
    dict_start_address = handle_variable(var_name)
    py2asm_globals.variables[f"{var_name}_keys"] = []
    current_offset = 0

    # Ensure temp_0 is allocated (used for compare_string_const)
    handle_variable('temp_0')

    for i in range(len(node.keys)):
        # key
        if isinstance(node.keys[i], ast.Constant) and isinstance(node.keys[i].value, str):
            string_label = f"{var_name}_key_{i}_str"
            string_address = handle_variable(string_label)
            # handle_variable(string_label) already correctly registers string_label
            # in py2asm_globals.variables with its address and metadata.
            # The line `variables[string_label] = string_address` was incorrect and overwritten the metadata.
            # The line `variables[f"{var_name}_key_{i}"] = string_address` is also not needed here.
            py2asm_globals.variables[f"{var_name}_keys"].append(f"{var_name}_key_{i}") # Store the base name of the key, e.g., "my_dict_key_0"
            key_offset = 0
            for char in node.keys[i].value:
                py2asm_globals.generated_code.append(f"    LDA #'{char}'")
                py2asm_globals.generated_code.append(f"    STA ${string_address + key_offset:04X}")
                key_offset += 1
            # Add the null terminator at the end of the string
            py2asm_globals.generated_code.append(f"    LDA #0")
            py2asm_globals.generated_code.append(f"    STA ${string_address + key_offset:04X}")
        else:
            # TODO: handle if the key is not a string
            print("Error: Dictionary key is not a string.")
            py2asm_globals.generated_code.extend(routines.generic_error_msg().splitlines())

        # value
        if isinstance(node.values[i], ast.Constant):
            py2asm_globals.generated_code.append(f"    LDA #{node.values[i].value}")
        elif isinstance(node.values[i], ast.Name):
            py2asm_globals.generated_code.append(f"    LDA {node.values[i].id}")
        else:
            raise TypeError("Value type not supported inside a dict")
        py2asm_globals.generated_code.append(f"    STA ${dict_start_address + current_offset:04X}")
        current_offset += 1

    return dict_start_address
