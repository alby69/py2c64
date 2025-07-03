# globals.py in py2c64
# Global variables and configuration
import ast
import sys  # For printing to stderr in report_compiler_error

# Directory base per gli output attesi dei test, relativa alla directory test_suite
# Esempio: se test.py è in py2asm/ e expected_outputs è in py2asm/test_suite/expected_outputs/
# Questo percorso è relativo alla directory che contiene test.py e test_suite/
TEST_SUITE_DIR = "test_suite"
EXPECTED_OUTPUTS_SUBDIR = "expected_outputs"


# Changed to: variables = { 'var_name': {'address': int, 'is_8bit_semantic': bool, possibly 'py_type': str} }
# We start with 'address', 'size', and 'is_8bit_semantic'.
# The default for 'is_8bit_semantic' will be False (i.e., 16 bit) unless overridden.
variables = {}
data_definitions = []  # To collect variable and constant definitions
generated_code = []
INITIAL_MEMORY_POINTER = 0xC100
MAX_MEMORY = 0xCFFF # Upper limit for variable allocation before I/O area
CHROUT_ADDRESS = "$FFD2"

# --- Global Constants (renamed slightly for clarity)---
# --- C64 VIC-II Chip Registers ---
VIC_BASE_ADDR = 0xD000


ROUTINES_START = 0x8000

# Zero Page pointers for routines (PRINT_STRING_ZP_BASE_PTR is deprecated by new print_string)
PRINT_STRING_ZP_BASE_PTR = 0xFA # Base address in Zero Page for the print_string pointer ($FA, $FB)
COMPARE_STR_ZP_PTR1 = 0xF8     # ZP pointer for the first string in compare_string_const ($F8, $F9)
COMPARE_STR_ZP_PTR2 = 0xF6     # ZP pointer for the second string in compare_string_const ($F6, $F7)
INPUT_ZP_PTR = 0xF4            # ZP pointer for read_string_loop/end ($F4, $F5)
FOR_LOOP_ZP_PTR = 0xF2  # ZP pointer for for loop iteration ($F2, $F3)
FSTRING_SRC_ZP_PTR = 0xEE  # ZP pointer for the f-string source ($EE, $EF)
FSTRING_DEST_ZP_PTR = 0xF0      # ZP pointer for the f-string destination ($F0, $F1)
memory_pointer = INITIAL_MEMORY_POINTER
TEMP_PTR1 = 0xF2 # A general purpose ZP pointer for routines ($F2, $F3, $F4, $F5)
TEMP_VAR_1 = 0xBA  # temporary variables in zero page (2 bytes each). Used by FP conversion.
TEMP_VAR_2 = 0xBC
TEMP_VAR_3 = 0xBE

# --- Wozniak/Apple II Floating Point Zero Page Addresses ---
WOZ_FP_SIGN = 0xF3
WOZ_FP_X2   = 0xF4 # Exponent FP2 (Floating Point Accumulator 2)
WOZ_FP_M2   = 0xF5 # Mantissa FP2 (3 bytes: $F5, $F6, $F7)
WOZ_FP_X1   = 0xF8 # Exponent FP1 (Floating Point Accumulator 1)
WOZ_FP_M1   = 0xF9 # Mantissa FP1 (3 bytes: $F9, $FA, $FB)
WOZ_FP_E    = 0xFC # Mantissa FP1 extension / scratch (3 bytes: $FC, $FD, $FE)
WOZ_FP_OVLOC = 0x03F5 # Standard Apple II overflow vector

# --- Temporary Variable Management ---
temp_var_counter = 0 # Counter for generating new unique temp var names
temp_var_pool = []   # Pool of released temp var names for reuse

label_counter = 0
current_loop_labels_stack = [] # Stack to manage break/continue labels for nested loops

# --- Function call globals ---
defined_functions = {}  # Stores func_name -> {'label': str, 'params': [str], 'ret_label': str}
MAX_FUNC_ARGS = 3  # Maximum number of arguments a function can take (for predefining __func_arg_N)

# --- Stack Pointer and Frame Pointer ---
STACK_POINTER_ZP = 0x00E0  # Zero Page address for the software stack pointer (2 bytes)
FRAME_POINTER_ZP = 0x00E2  # Zero Page address for the software frame pointer (2 bytes)

STACK_BASE_ADDRESS = 0x0200 # Start of the software stack memory area
STACK_TOP_ADDRESS = 0x02FF  # End of the software stack memory area (grows downwards)

temp_variables = {}

used_routines = set()  # Tracks routines used by the generated code

str_pointer = 0
list_pointer = 0
max_len_input = 0
input_pointer = 0
result_compare = 0

# --- Configurazione Sintassi Assembler ---

# Defines sets of directives for supported assemblers.
# The user can extend this dictionary with other assemblers and their specific directives.
SUPPORTED_ASSEMBLERS_DIRECTIVES = {
    "CBM_PRG_STUDIO": {
        'byte': 'byte',     # Directive to define a single byte
            'word': 'word',     # Directive to define a word (2 bytes)
            'res':  '* = * +',   # Directive to reserve a block of bytes.
                                 # Used as: {label} {res_directive} {size}
                                 # For CBM Prg Studio, this translates to: label * = * + size
            'asciiz': 'text'    # Directive for null-terminated strings
        },
        "GENERIC_DEFAULT": { # Original values or a common alternative
            'byte': 'byte',
        'word': 'word',
        'res':  '.res',      # Many assemblers use .res or .block, ds.b, etc.
        'asciiz': 'text'     # '.asciiz' is common, 'text' is used here as a generic placeholder
    }
    # Add other assembler profiles here, e.g., "ACME", "CA65"
    # "ACME": {
    #     'byte': '!byte',
    #     'word': '!word',
    #     'res':  '!fill',  # Note: ACME's !fill is !fill size, value.
    #                       # The code generating it might need adaptation.
    #                       # Or use '!zone zone_name' for uninitialized data blocks.
    #     'asciiz': '!text' # o '!asciiz'
    # }
}

# Sets the current assembler syntax.
# This could be set via a command-line argument
# or a configuration file in a real application.
# For this request, we set CBM Prg Studio as the default.
CURRENT_ASSEMBLER_SYNTAX = "CBM_PRG_STUDIO"

# Dictionary for assembly data types, populated dynamically.
assembly_data_types = {}

def _initialize_assembly_data_types():
    """Initializes assembly_data_types based on CURRENT_ASSEMBLER_SYNTAX."""
    global assembly_data_types # Needed for modification
    # print(f"DEBUG: _initialize_assembly_data_types() called. CURRENT_ASSEMBLER_SYNTAX = {CURRENT_ASSEMBLER_SYNTAX}") # Debug
    if CURRENT_ASSEMBLER_SYNTAX in SUPPORTED_ASSEMBLERS_DIRECTIVES:
        assembly_data_types.clear() # Clear before repopulating
        assembly_data_types.update(SUPPORTED_ASSEMBLERS_DIRECTIVES[CURRENT_ASSEMBLER_SYNTAX])
        # print(f"DEBUG: assembly_data_types set to: {assembly_data_types}") # Debug
    else:
        # Fallback al default generico se la sintassi specificata non è trovata
        report_compiler_error(f"Assembler syntax '{CURRENT_ASSEMBLER_SYNTAX}' not recognized. Using GENERIC_DEFAULT.", level="WARNING")
        assembly_data_types.clear() # Svuota prima di ripopolare
        assembly_data_types.update(SUPPORTED_ASSEMBLERS_DIRECTIVES["GENERIC_DEFAULT"]) # Updates with a default syntax
# Chiama la funzione di inizializzazione all'importazione del modulo
_initialize_assembly_data_types()

# --- Fine Configurazione Sintassi Assembler ---

# --- Compiler Error Reporting ---
_compiler_error_count = 0
_compiler_warning_count = 0

def report_compiler_error(message: str, node: ast.AST = None, level: str = "ERROR"):
    """
    Reports a compiler error or warning.
    Args:
        message (str): The error message.
        node (ast.AST, optional): The AST node related to the error, for line/col info.
        level (str, optional): "ERROR" or "WARNING".
    """
    global _compiler_error_count, _compiler_warning_count

    location = ""
    if node and hasattr(node, 'lineno'):
        location = f" (line {node.lineno}"
        if hasattr(node, 'col_offset'): # col_offset is 0-indexed
            location += f", column {node.col_offset + 1}"
        location += ")"

    full_message = f"{level.upper()}: {message}{location}"
    print(full_message, file=sys.stderr)

    if level.upper() == "ERROR":
        _compiler_error_count += 1
    elif level.upper() == "WARNING":
        _compiler_warning_count += 1

def get_compiler_error_count():
    return _compiler_error_count


class ErrorCodes:
    OVERFLOW = 1
    DIVISION_BY_ZERO = 2
    # GENERIC_ERROR removed as a specific code, used as a fallback
    KEY_NOT_FOUND = 4 # Added based on routines.py usage
    VALUE_ERROR = 5
    TYPE_ERROR = 6
    INDEX_ERROR = 7
    NAME_ERROR = 8 # For undefined variables (not actively used yet)
    ASSERTION_ERROR = 9
    ATTRIBUTE_ERROR = 10      # New for Point 2
    NOT_IMPLEMENTED_ERROR = 11 # New for Point 2
    # Add others if necessary
    # GENERIC_RUNTIME_ERROR_CODE is a special code for the global error handler
    # when no specific try/except catches the error.
    # It should not be used directly by 'raise SpecificError'.
    GENERIC_RUNTIME_ERROR_CODE = 255 # A high code to distinguish it


# Mapping from Python exception name (as a string) to ErrorCodes
exception_name_to_code = {
    "OverflowError": ErrorCodes.OVERFLOW,
    "ZeroDivisionError": ErrorCodes.DIVISION_BY_ZERO,
    "KeyError": ErrorCodes.KEY_NOT_FOUND,
    "ValueError": ErrorCodes.VALUE_ERROR,                   # Invalid argument or data value
    "TypeError": ErrorCodes.TYPE_ERROR,                     # Operation or function applied to incorrect type
    "IndexError": ErrorCodes.INDEX_ERROR,                   # Sequence index out of range
    "NameError": ErrorCodes.NAME_ERROR,                     # Variable or name not found (e.g., undefined variable)
    "AssertionError": ErrorCodes.ASSERTION_ERROR,           # Assert statement failed
    "AttributeError": ErrorCodes.ATTRIBUTE_ERROR,           # Attribute reference or assignment failed
    "FloatingPointError": ErrorCodes.OVERFLOW,  # Map generic FP error to overflow for now
    "NotImplementedError": ErrorCodes.NOT_IMPLEMENTED_ERROR, # New for Point 2
}


def clear_variables():
    """Resets global variables to their initial state."""
    global variables, memory_pointer, label_counter, temp_variables, current_loop_labels_stack, temp_var_counter, temp_var_pool
    global str_pointer, list_pointer, max_len_input, input_pointer, result_compare, used_routines, data_definitions
    global generated_code, _compiler_error_count, _compiler_warning_count
    variables.clear()
    # memory_pointer is reset by the caller of python_to_assembly
    # or at the beginning of python_to_assembly.
    # Reset data structures.
    temp_var_counter = 0    # Reset temp var counter
    temp_var_pool.clear()   # Clear temp var pool
    label_counter = 0
    temp_variables.clear()  # Dictionary to track temporary variables in use
    str_pointer = 0
    list_pointer = 0
    max_len_input = 0
    input_pointer = 0
    result_compare = 0
    generated_code.clear()
    data_definitions.clear()
    used_routines.clear()
    current_loop_labels_stack.clear()
    _compiler_error_count = 0 # Reset error count
    _compiler_warning_count = 0 # Reset warning count
    # Re-initialize assembly data types if CURRENT_ASSEMBLER_SYNTAX
    # could change between executions (e.g., in tests).
    # This is for greater robustness, ensuring that assembly_data_types
    # is correct at the start of each test.
    _initialize_assembly_data_types()
