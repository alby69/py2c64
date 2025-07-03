# func_dict.py
# Functions for handling dictionaries.

import ast # pyright: ignore[reportMissingModuleSource]
from .. import globals as py2asm_globals # pyright: ignore[reportMissingModuleSource] # Use an alias to avoid conflicts
from .func_core import handle_variable, get_temp_var, release_temp_var, create_label, _generate_copy_2_bytes
from . import routines


def handle_dict_access(node):
    """Handles accessing a dictionary element. Result is placed in temp_2."""
    dict_name = node.value.id  # dict name
    key_node = node.slice  # key node

    if not (isinstance(key_node, ast.Constant) and isinstance(key_node.value, str)):
        # In dictionary access like my_dict['a'], the key 'a' is an ast.Constant.
        # If key_node is ast.Slice, it's not standard dict access.
        py2asm_globals.report_compiler_error(f"Key for dictionary access '{dict_name}' must be a string constant. Got {type(key_node)} with value {getattr(key_node, 'value', 'N/A')}.", node=key_node)
        py2asm_globals.generated_code.append(f"    JSR key_error_msg")
        py2asm_globals.used_routines.add('key_error_msg')
        return None

    searched_key_string = key_node.value

    if f"{dict_name}_keys" not in py2asm_globals.variables: # pragma: no cover
        print(f"ERROR: Dictionary '{dict_name}' not properly initialized or keys list missing.")
        py2asm_globals.generated_code.append(f"    JSR key_error_msg")
        py2asm_globals.used_routines.add('key_error_msg')
        return None

    key_variable_base_names_list = py2asm_globals.variables[f"{dict_name}_keys"] # e.g., ['my_dict_key_0', 'my_dict_key_1']

    dict_access_done_label = f"dict_access_done_{dict_name}_{py2asm_globals.label_counter}"
    py2asm_globals.label_counter +=1

    # Define the searched key string literal once
    key_to_find_label = f"dict_search_key_lit_{py2asm_globals.label_counter}"
    py2asm_globals.label_counter += 1
    escaped_search_key = searched_key_string.replace('"', '""') # Basic escape
    py2asm_globals.data_definitions.append(f"{key_to_find_label} {py2asm_globals.assembly_data_types['asciiz']} \"{escaped_search_key}\"")
    # Assuming .asciiz adds null terminator. If not, add:
    # py2asm_globals.data_definitions.append(f"          {py2asm_globals.assembly_data_types['byte']} 0 ; Null for {key_to_find_label}")

    key_value_offset = 0 # Offset into the dictionary's value storage area

    for key_base_name in key_variable_base_names_list: # e.g., key_base_name = "my_dict_key_0"
        key_string_buffer_label = key_base_name + "_str" # e.g., "my_dict_key_0_str"

        if key_string_buffer_label not in py2asm_globals.variables: # pragma: no cover
            print(f"ERROR: Internal - Key string buffer '{key_string_buffer_label}' not found for dict '{dict_name}'. Skipping this key.")
            key_value_offset += 1
            continue

        # Set up ZP Pointers for compare_string_const
        # PTR1: key_to_find_label (the key we are searching for)
        py2asm_globals.generated_code.append(f"    LDA #<{key_to_find_label}")
        py2asm_globals.generated_code.append(f"    STA ${py2asm_globals.COMPARE_STR_ZP_PTR1:02X}")
        py2asm_globals.generated_code.append(f"    LDA #>{key_to_find_label}")
        py2asm_globals.generated_code.append(f"    STA ${py2asm_globals.COMPARE_STR_ZP_PTR1+1:02X}")

        # PTR2: current key from dictionary (key_string_buffer_label)
        address_key_in_dict = py2asm_globals.variables[key_string_buffer_label]['address']
        py2asm_globals.generated_code.append(f"    LDA #{address_key_in_dict & 0xFF}")
        py2asm_globals.generated_code.append(f"    STA ${py2asm_globals.COMPARE_STR_ZP_PTR2:02X}")
        py2asm_globals.generated_code.append(f"    LDA #{address_key_in_dict >> 8}")
        py2asm_globals.generated_code.append(f"    STA ${py2asm_globals.COMPARE_STR_ZP_PTR2+1:02X}")

        py2asm_globals.generated_code.append(f"    JSR compare_string_const")
        py2asm_globals.used_routines.add('compare_string_const')
        py2asm_globals.generated_code.append(f"    LDA result_compare") # result_compare is 1 if equal, 0 if not
        py2asm_globals.generated_code.append(f"    CMP #1")

        # Use current label_counter for uniqueness in the next_key_check_label
        next_key_check_label = f"dict_next_key_{dict_name}_{key_value_offset}_{py2asm_globals.label_counter-1}" # Use the label_counter value from before this specific literal's increment

        py2asm_globals.generated_code.append(f"    BNE {next_key_check_label} ; If not equal, try next key")

        # Key IS equal. Load the value into temp_2.
        handle_variable('temp_2', size=2)
        dict_values_start_address = py2asm_globals.variables[dict_name]['address']
        # Values are assumed to be 8-bit based on diz_value logic
        py2asm_globals.generated_code.append(f"    LDA ${dict_values_start_address + key_value_offset:04X}")
        py2asm_globals.generated_code.append(f"    STA temp_2")
        # Clear MSB of temp_2 as it's a word but holds an 8-bit value from dict
        py2asm_globals.generated_code.append(f"    LDA #0")
        py2asm_globals.generated_code.append(f"    STA temp_2+1")

        py2asm_globals.generated_code.append(f"    JMP {dict_access_done_label} ; Found key, value loaded, exit")

        py2asm_globals.generated_code.append(f"{next_key_check_label}:")
        key_value_offset += 1

    # If loop finishes, key was not found
    py2asm_globals.generated_code.append(f"    JMP key_error_msg")
    py2asm_globals.used_routines.add('key_error_msg')

    py2asm_globals.generated_code.append(f"{dict_access_done_label}:")
    return None


def handle_dict_assignment(node):
    """Handles assigning a value to a dictionary element."""
    dict_name = node.targets[0].value.id
    key_node = node.targets[0].slice
    # Save the value
    if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
        # check if the key exist
        key_found = False
        key_index = 0
        for _current_key_idx in range(len(py2asm_globals.variables)): # Iterate up to a reasonable max number of keys
            key_name = f"{dict_name}_key_{key_index}"
            # This logic to find a free slot or an existing key is problematic.
            # For now, assume we are adding a new key and find the first free slot.
            # A real dictionary implementation would require collision/hash management.
            if f"{dict_name}_key_{key_index}_str" not in py2asm_globals.variables: # Cerca uno slot non usato per la stringa della chiave
                key_found = False # Trovato uno slot libero
                break # Esci per usare key_index
            key_index += 1

        # Se key_found è ancora False, significa che abbiamo trovato uno slot libero (key_index)
        # Se key_found fosse True (da una logica di ricerca precedente, non implementata qui), aggiorneremmo il valore.
        if not key_found: # Aggiungi una nuova chiave/valore
            # key
            string_label = f"{dict_name}_key_{key_index}_str"
            key_string_size = len(key_node.value) + 1 # +1 for null terminator
            string_address = handle_variable(string_label, size=key_string_size, var_type='str_buffer')

            # variables[f"{dict_name}_key_{key_index}"] will store the pointer to this string_label
            # This variable holds the pointer to the key string.
            key_pointer_var_name = f"{dict_name}_key_{key_index}"
            handle_variable(key_pointer_var_name, size=2, var_type='pointer')

            # Store the address of string_label into the key pointer variable
            py2asm_globals.generated_code.append(f"    LDA #<{string_label}")
            py2asm_globals.generated_code.append(f"    STA {key_pointer_var_name}")
            py2asm_globals.generated_code.append(f"    LDA #>{string_label}")
            py2asm_globals.generated_code.append(f"    STA {key_pointer_var_name}+1")

            key_offset = 0
            for char in key_node.value:
                py2asm_globals.generated_code.append(f"    LDA #'{char}'")
                py2asm_globals.generated_code.append(f"    STA ${string_address + key_offset:04X}")
                key_offset += 1
            # Add the null terminator at the end of the string
            py2asm_globals.generated_code.append(f"    LDA #0")
            py2asm_globals.generated_code.append(f"    STA ${string_address + key_offset:04X}")
        # value
        if isinstance(node.value, ast.Constant):
            py2asm_globals.generated_code.append(f"    LDA #{node.value.value}")
        elif isinstance(node.value, ast.Name):
            py2asm_globals.generated_code.append(f"    LDA {node.value.id}")
        else:
            raise TypeError("Value type not supported inside a dict")
        py2asm_globals.generated_code.append(f"    STA ${py2asm_globals.variables[dict_name]['address'] + key_index:04X}") # Usa ['address']

    else:
        raise TypeError("Key type not supported")


def handle_dict_deletion(node):
    """Handles deleting a key from a dictionary."""
    dict_name = node.targets[0].value.id
    key_node = node.targets[0].slice
    if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
        # get the key position
        key_found = False
        key_index = 0
        # current_key = 0 # This variable is not used effectively
        for current_key_idx in range(len(py2asm_globals.variables)): # Iterate up to a reasonable max number of keys
            # This iteration is to find the key to delete.
            key_name = f"{dict_name}_key_{key_index}" # Use key_index which is incremented
            if f"{dict_name}_key_{key_index}_str" in py2asm_globals.variables: # Controlla se esiste il buffer per questa chiave (using key_index)
                key_found = True
                # Key to search for (from key_node.value, which is a string constant)
                # This is a placeholder - proper handling of key_node string constant needed here.
                key_to_find_label = f"dict_delete_key_{py2asm_globals.label_counter}" # Needs a unique label
                py2asm_globals.data_definitions.append(f"{key_to_find_label} {py2asm_globals.assembly_data_types['asciiz']} \"{key_node.value}\"")
                py2asm_globals.label_counter +=1

                py2asm_globals.generated_code.append(f"    LDA #<{key_to_find_label}")
                py2asm_globals.generated_code.append(f"    STA ${py2asm_globals.COMPARE_STR_ZP_PTR1:02X}")
                py2asm_globals.generated_code.append(f"    LDA #>{key_to_find_label}")
                py2asm_globals.generated_code.append(f"    STA ${py2asm_globals.COMPARE_STR_ZP_PTR1+1:02X}")

                # Key in dictionary (variables[f"{dict_name}_key_{current_key}_str"] is its address)
                address_key_in_dict = py2asm_globals.variables[f"{dict_name}_key_{key_index}_str"]['address'] # Use key_index
                py2asm_globals.generated_code.append(f"    LDA #{address_key_in_dict & 0xFF}")
                py2asm_globals.generated_code.append(f"    STA ${py2asm_globals.COMPARE_STR_ZP_PTR2:02X}")
                py2asm_globals.generated_code.append(f"    LDA #{address_key_in_dict >> 8}")
                py2asm_globals.generated_code.append(f"    STA ${py2asm_globals.COMPARE_STR_ZP_PTR2+1:02X}")

                py2asm_globals.generated_code.append(f"    JSR compare_string_const")  # compare
                py2asm_globals.generated_code.append(f"    LDA result_compare")  # check result
                not_found_label = create_label("dict_key_not_found", f"{dict_name}_{py2asm_globals.label_counter}")
                # label_counter is already incremented in process_if_node or here if needed for unique labels
                py2asm_globals.generated_code.append(f"    BNE {not_found_label} ;skip if found") # modify the label
                py2asm_globals.generated_code.append(f"    LDA #0")
                py2asm_globals.generated_code.append(f"    STA ${py2asm_globals.variables[dict_name]['address'] + key_index:04X}") # Use ['address'] and correct key_index
                # delete the key
                # "Deleting" a key by zeroing its pointer and string buffer is a simplification.
                # A real dict would need to handle collisions or re-packing.
                py2asm_globals.generated_code.append(f"    LDA #0")
                # To "delete" the key, we should ideally remove entries from 'globals.variables'
                # or mark them as unused. Zeroing the pointer is a start.
                py2asm_globals.generated_code.append(f"    STA {key_name}")
                py2asm_globals.generated_code.append(f"    STA {key_name}+1")
                # Also consider zeroing the first byte of f"{dict_name}_key_{key_index}_str"
                key_found = True
                break
            key_index += 1

        if not key_found:
            py2asm_globals.generated_code.append(f"    JMP key_error_msg")
        # Add the label after the loop for the BNE target
        # If not_found_label was not defined before (because the loop never entered or the key was found immediately)
        py2asm_globals.generated_code.append(f"{not_found_label}:")
    else:
        raise TypeError("Key type not supported")
