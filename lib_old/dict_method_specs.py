# /workspaces/py2c64/lib/dict_method_specs.py

# This file contains the specifications for Python's dictionary methods.
# It is used by func_dict.py to generate the correct assembly code for method calls.

# 'params': A list of dictionaries, one for each parameter.
#     'name': The name of the parameter (for documentation).
#     'type': Expected Python type ('int', 'float', 'str', 'dict', 'any').
#     'required': Boolean, True if the parameter is mandatory.
# 'routine': The name of the assembly language routine to call.
#     The routine is expected to receive the dictionary's address and arguments
#     in predefined zero-page locations or registers.
# 'return': (Optional) A dictionary describing the return value.
#     'type': The Python type of the return value ('list', 'any', etc.).
#     A type of 'pointer' indicates a pointer to a complex data structure.

DICT_METHOD_SPECS = {
    'get': {
        'routine': 'dict_get_value',
        'params': [
            {'name': 'key', 'type': 'any', 'required': True},
            {'name': 'default', 'type': 'any', 'required': False, 'default_value': None}
        ],
        'return': {'type': 'any'}  # Type depends on the value found or the default
    },
    'keys': {
        'routine': 'dict_get_keys',
        'params': [],
        'return': {'type': 'pointer'}  # Returns a pointer to a new list object
    },
    'values': {
        'routine': 'dict_get_values',
        'params': [],
        'return': {'type': 'pointer'}  # Returns a pointer to a new list object
    },
    'items': {
        'routine': 'dict_get_items',
        'params': [],
        'return': {'type': 'pointer'}  # Returns a pointer to a new list of tuples
    },
    'clear': {
        'routine': 'dict_clear',
        'params': [],
        'return': None
    },
    # pop, popitem, update, etc. can be added later following this pattern.
}