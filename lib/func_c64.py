# lib/func_c64.py
"""
Handles the processing of C64-specific hardware function calls.
This module uses a data-driven approach to generate assembly code for
graphics, sprites, and other hardware interactions, replacing the large
if/elif block that was previously in ast_processor.py.
"""
import ast
from .. import globals
from . import func_core
from . import func_expressions

# Aliases
gen_code = globals.generated_code
used_routines = globals.used_routines
report_error = globals.report_compiler_error

# --- C64 Function Definitions ---
# This dictionary defines how to handle each C64-specific function call.
# 'routine': The assembly subroutine to call.
# 'args': A list of dictionaries, one for each argument, specifying how to pass it.
#         'reg': 'a' or 'x' - pass the argument via the A or X register.
#         'zp': address - store the argument in a Zero-Page location.
#         'size': 8 or 16 - the size of the argument in bits.
# 'special': A function to handle non-standard argument processing.

C64_FUNCTIONS = {
    # --- Graphics Routines ---
    'gfx_turn_on': {'routine': 'gfx_turn_on', 'args': []},
    'gfx_turn_off': {'routine': 'gfx_turn_off', 'args': []},
    'gfx_clear_screen': {'routine': 'gfx_clear_screen', 'args': []},
    'draw_line': {
        'routine': 'gfx_draw_line',
        'args': [
            {'zp': 0xB0, 'size': 16},  # x1
            {'zp': 0xB2, 'size': 8},   # y1
            {'zp': 0xB6, 'size': 16},  # x2
            {'zp': 0xB8, 'size': 8},   # y2
        ]
    },
    'draw_rect': {
        'routine': 'gfx_draw_rect',
        'args': [
            {'zp': 0xB0, 'size': 16},  # x1
            {'zp': 0xB2, 'size': 8},   # y1
            {'zp': 0xB6, 'size': 16},  # x2
            {'zp': 0xB8, 'size': 8},   # y2
        ]
    },
    'draw_ellipse': {
        'routine': 'gfx_draw_ellipse',
        'args': [
            {'zp': 0xB0, 'size': 16},  # xm
            {'zp': 0xB2, 'size': 8},   # ym
            {'zp': 0xB6, 'size': 16},  # xr
            {'zp': 0xB8, 'size': 8},   # yr
        ]
    },
    'draw_circle': {
        'routine': 'gfx_draw_ellipse', # Uses the ellipse routine
        'special': '_handle_draw_circle'
    },

    # --- Sprite Routines ---
    'sprite_enable': {'routine': 'sprite_enable', 'args': [{'reg': 'a'}]},
    'sprite_disable': {'routine': 'sprite_disable', 'args': [{'reg': 'a'}]},
    'sprite_set_x_msb': {'routine': 'sprite_set_x_msb', 'args': [{'reg': 'a'}]},
    'sprite_set_x_msb_clear': {'routine': 'sprite_set_x_msb_clear', 'args': [{'reg': 'a'}]},
    'sprite_set_priority': {'routine': 'sprite_set_priority', 'args': [{'reg': 'a'}]},
    'sprite_set_multicolor': {'routine': 'sprite_set_multicolor', 'args': [{'reg': 'a'}]},
    'sprite_set_color': {
        'routine': 'sprite_set_color',
        'args': [
            {'reg': 'x'},  # sprite_num
            {'reg': 'a'},  # color
        ]
    },
    'sprite_expand_xy': {
        'routine': 'sprite_expand_xy',
        'args': [
            {'reg': 'a'},  # y_mask
            {'reg': 'x'},  # x_mask
        ]
    },
    'sprite_set_multicolor_colors': {
        'routine': 'sprite_set_multicolor_colors',
        'args': [
            {'reg': 'a'},  # mc1
            {'reg': 'x'},  # mc2
        ]
    },
    'sprite_set_pointer': {
        'routine': 'sprite_set_pointer',
        'args': [
            {'reg': 'x'},  # sprite_num
            {'reg': 'a'},  # pointer_val
        ]
    },
    'sprite_set_pos': {
        'routine': 'sprite_set_pos',
        'args': [
            {'reg': 'x'},             # sprite_num
            {'zp': 0xB0, 'size': 8},  # x_pos (LSB only for this routine)
            {'reg': 'a'},             # y_pos
        ]
    },
    'sprite_create_from_data': {
        'routine': 'sprite_create_from_data',
        'args': [
            {'reg': 'x'},             # sprite_num
            {'zp': 0xF0, 'size': 16}, # source_addr
        ]
    },
}

def _handle_draw_circle(call_node, func_info, current_func_info):
    """Special handler for draw_circle, which maps its arguments to the draw_ellipse routine."""
    if len(call_node.args) != 3:
        report_error(f"Function 'draw_circle' expects 3 arguments (x, y, radius), got {len(call_node.args)}.", node=call_node)
        return

    # Arguments: x (16bit), y (8bit), r (used for xr and yr)
    # ZP locations for draw_ellipse: xm(0xB0, 16b), ym(0xB2, 8b), xr(0xB6, 16b), yr(0xB8, 8b)
    zp_map = {
        0: {'zp_base': 0xB0, 'size': 16},  # x -> xm
        1: {'zp_base': 0xB2, 'size': 8},   # y -> ym
        2: {'zp_base': 0xB6, 'size': 16},  # r -> xr
    }

    gen_code.append(f"    ; --- Preparing call to draw_circle (via draw_ellipse) ---")

    # Evaluate the 3 arguments (x, y, r) and place them in ZP for xm, ym, xr
    temp_vars = []
    for i, arg_node in enumerate(call_node.args):
        temp_arg_var = func_core.get_temp_var()
        temp_vars.append(temp_arg_var)
        func_expressions.translate_expression_recursive(temp_arg_var, arg_node, current_func_info.get('name') if current_func_info else None)

        zp_addr = zp_map[i]['zp_base']
        if zp_map[i]['size'] == 16:
            gen_code.append(f"    LDA {temp_arg_var}      ; LSB")
            gen_code.append(f"    STA ${zp_addr:02X}")
            gen_code.append(f"    LDA {temp_arg_var}+1    ; MSB")
            gen_code.append(f"    STA ${zp_addr+1:02X}")
        else:
            gen_code.append(f"    LDA {temp_arg_var}      ; LSB is sufficient")
            gen_code.append(f"    STA ${zp_addr:02X}")

        # If processing the radius (argument 2), also copy its LSB to yr (0xB8)
        if i == 2:
            gen_code.append(f"    ; Copy radius (LSB) to ZP for yr")
            gen_code.append(f"    LDA {temp_arg_var}      ; LSB of radius")
            gen_code.append(f"    STA ${0xB8:02X}")

    # Release temp vars
    for temp_var in temp_vars:
        func_core.release_temp_var(temp_var)

    # Call the routine
    gen_code.append(f"    JSR {func_info['routine']}")
    used_routines.add(func_info['routine'])
    gen_code.append(f"    ; --- End call to draw_circle ---")

def process_c64_call(call_node, current_func_info=None):
    """
    Processes a call to a C64-specific function.
    Returns True if the function was handled, False otherwise.
    """
    if not isinstance(call_node.func, ast.Name):
        return False

    func_name = call_node.func.id
    if func_name not in C64_FUNCTIONS:
        return False

    func_info = C64_FUNCTIONS[func_name]
    gen_code.append(f"    ; --- Preparing call to {func_name} ---")

    # Handle special cases
    if 'special' in func_info:
        handler_func = globals()[func_info['special']]
        handler_func(call_node, func_info, current_func_info)
        return True

    # --- Standard Argument Handling ---
    expected_arg_count = len(func_info['args'])
    if len(call_node.args) != expected_arg_count:
        report_error(f"Function '{func_name}' expects {expected_arg_count} arguments, got {len(call_node.args)}.", node=call_node)
        return True # Handled (with an error)

    temp_vars = []
    for arg_node in call_node.args:
        temp_arg_var = func_core.get_temp_var()
        temp_vars.append(temp_arg_var)
        func_expressions.translate_expression_recursive(temp_arg_var, arg_node, current_func_info.get('name') if current_func_info else None)

    # Load evaluated arguments into registers or ZP locations in reverse order
    for i in range(len(func_info['args']) - 1, -1, -1):
        arg_spec = func_info['args'][i]
        temp_var = temp_vars[i]

        if 'reg' in arg_spec:
            reg = arg_spec['reg'].upper()
            gen_code.append(f"    LD{reg} {temp_var}      ; Load arg {i+1} into {reg}")
        elif 'zp' in arg_spec:
            zp_addr = arg_spec['zp']
            if arg_spec.get('size', 8) == 16:
                gen_code.append(f"    LDA {temp_var}      ; LSB of arg {i+1}")
                gen_code.append(f"    STA ${zp_addr:02X}")
                gen_code.append(f"    LDA {temp_var}+1    ; MSB of arg {i+1}")
                gen_code.append(f"    STA ${zp_addr+1:02X}")
            else:
                gen_code.append(f"    LDA {temp_var}      ; LSB of arg {i+1}")
                gen_code.append(f"    STA ${zp_addr:02X}")

    gen_code.append(f"    JSR {func_info['routine']}")
    used_routines.add(func_info['routine'])

    for temp_var in temp_vars:
        func_core.release_temp_var(temp_var)

    gen_code.append(f"    ; --- End call to {func_name} ---")
    return True