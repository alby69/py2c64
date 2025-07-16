# /workspaces/py2c64/lib/builtin_function_specs.py

# This file contains the specifications for Python's built-in functions.
# It is used by func_builtins.py to generate the correct assembly code.

# 'params': A list of dictionaries, one for each parameter.
#     'name': The name of the parameter (for documentation).
#     'type': Expected Python type ('int', 'float', 'str', 'any').
# 'routine': The name of the assembly language routine to call.
# 'return': (Optional) A dictionary describing the return value.
#     'type': The Python type of the return value.
# 'special_handling': (Optional) A flag for functions that need custom logic
#                     in the handler beyond simple argument passing.

BUILTIN_FUNCTION_SPECS = {
    'print': {
        'special_handling': 'print', # Custom logic for variable args and types
        'params': [], # Handled specially by the handler
        'return': None
    },
    'int': {
        'routine': 'convert_to_int', # Routine to convert float/str in AX to int in AX
        'params': [
            {'name': 'value', 'type': 'any'}
        ],
        'return': {'type': 'int'}
    },
    'float': {
        'routine': 'convert_to_float', # Routine to convert int/str in AX to float in FP1
        'params': [
            {'name': 'value', 'type': 'any'}
        ],
        'return': {'type': 'float'}
    },
    'abs': {
        'special_handling': 'abs', # Needs to check type of argument at compile time
        'params': [
            {'name': 'value', 'type': 'any'}
        ],
        'return': {'type': 'any'} # Return type depends on argument type
    },
    'len': {
        'special_handling': 'len', # Needs to check type (str, list) and get length
        'params': [
            {'name': 'obj', 'type': 'any'}
        ],
        'return': {'type': 'int'}
    },
    'input': {
        'special_handling': 'input', # Needs to handle optional prompt and read from keyboard
        'params': [], # Handled specially by the handler
        'return': {'type': 'str'}
    },
}