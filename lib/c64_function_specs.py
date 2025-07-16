# py2c64/lib/c64_function_specs.py

# This file contains the specifications for C64-specific hardware functions.
# It is used by func_c64.py to generate the correct assembly code.

# 'params': A list of dictionaries, one for each parameter.
#     'name': The name of the parameter (for documentation).
#     'store': Where to store the argument: 'a', 'x', 'y', 'ax', or 'zp'.
#     'size': 8 or 16 bits.
#     'address': The Zero-Page address (if store is 'zp').
# 'routine': The name of the assembly language routine to call.
# 'return': (Optional) A dictionary describing the return value.
#     'reg': The register holding the return value ('a' or 'ax').
#     'size': 8 or 16 bits.

C64_HARDWARE_ALIASES = {
    'draw_line': 'gfx_draw_line',
    'draw_circle': 'gfx_draw_circle',
    'draw_ellipse': 'gfx_draw_ellipse',
    'draw_rect': 'gfx_draw_rect',
}

C64_FUNCTION_SPECS = {
    # --- Graphics Functions ---
    'gfx_turn_on': {
        'routine': 'gfx_turn_on',
        'params': []
    },
    'gfx_turn_off': {
        'routine': 'gfx_turn_off',
        'params': []
    },
    'gfx_clear_screen': {
        'routine': 'gfx_clear_screen',
        'params': []
    },
    'gfx_draw_line': {
        'routine': 'gfx_draw_line',
        'params': [
            {'name': 'x1', 'store': 'zp', 'address': 0xfb, 'size': 16},
            {'name': 'y1', 'store': 'zp', 'address': 0xfd, 'size': 8},
            {'name': 'x2', 'store': 'ax', 'size': 16},
            {'name': 'y2', 'store': 'y', 'size': 8},
        ]
    },
    'gfx_draw_ellipse': {
        'routine': 'gfx_draw_ellipse',
        'params': [
            {'name': 'cx', 'store': 'zp', 'address': 0xfb, 'size': 16},
            {'name': 'cy', 'store': 'zp', 'address': 0xfd, 'size': 8},
            {'name': 'rx', 'store': 'ax', 'size': 16},
            {'name': 'ry', 'store': 'y', 'size': 8},
        ]
    },
    'gfx_draw_circle': {
        'routine': 'gfx_draw_circle',
        'params': [
            {'name': 'cx', 'store': 'zp', 'address': 0xfb, 'size': 16},
            {'name': 'cy', 'store': 'zp', 'address': 0xfd, 'size': 8},
            {'name': 'r', 'store': 'a', 'size': 8},
        ]
    },
    'gfx_draw_rect': {
        'routine': 'gfx_draw_rect',
        'params': [
            {'name': 'x1', 'store': 'zp', 'address': 0xfb, 'size': 16},
            {'name': 'y1', 'store': 'zp', 'address': 0xfd, 'size': 8},
            {'name': 'x2', 'store': 'ax', 'size': 16},
            {'name': 'y2', 'store': 'y', 'size': 8},
        ]
    },

    # --- Sprite Functions ---
    'sprite_set_pos': {
        'routine': 'sprite_set_pos',
        'params': [
            {'name': 'sprite_num', 'store': 'y', 'size': 8},
            {'name': 'x', 'store': 'a', 'size': 8},
            {'name': 'y', 'store': 'x', 'size': 8},
        ]
    },
    'sprite_enable': {
        'routine': 'sprite_enable',
        'params': [
            {'name': 'mask', 'store': 'a', 'size': 8},
        ]
    },
    'sprite_disable': {
        'routine': 'sprite_disable',
        'params': [
            {'name': 'mask', 'store': 'a', 'size': 8},
        ]
    },
    'sprite_set_color': {
        'routine': 'sprite_set_color',
        'params': [
            {'name': 'sprite_num', 'store': 'y', 'size': 8},
            {'name': 'color', 'store': 'a', 'size': 8},
        ]
    },
    'sprite_set_x_msb': {
        'routine': 'sprite_set_x_msb',
        'params': [
            {'name': 'mask', 'store': 'a', 'size': 8},
        ]
    },
    'sprite_set_x_msb_clear': {
        'routine': 'sprite_set_x_msb_clear',
        'params': [
            {'name': 'mask', 'store': 'a', 'size': 8},
        ]
    },
    'sprite_expand_xy': {
        'routine': 'sprite_expand_xy',
        'params': [
            {'name': 'y_mask', 'store': 'a', 'size': 8},
            {'name': 'x_mask', 'store': 'x', 'size': 8},
        ]
    },
    'sprite_set_pointer': {
        'routine': 'sprite_set_pointer',
        'params': [
            {'name': 'sprite_num', 'store': 'y', 'size': 8},
            {'name': 'pointer_val', 'store': 'a', 'size': 8},
        ]
    },
    'sprite_set_priority': {
        'routine': 'sprite_set_priority',
        'params': [
            {'name': 'mask', 'store': 'a', 'size': 8},
        ]
    },
    'sprite_set_multicolor': {
        'routine': 'sprite_set_multicolor',
        'params': [
            {'name': 'mask', 'store': 'a', 'size': 8},
        ]
    },
    'sprite_set_multicolor_colors': {
        'routine': 'sprite_set_multicolor_colors',
        'params': [
            {'name': 'mc1', 'store': 'a', 'size': 8},
            {'name': 'mc2', 'store': 'x', 'size': 8},
        ]
    },
    'sprite_check_collision_sprite': {
        'routine': 'sprite_check_collision_sprite',
        'params': [],
        'return': {'reg': 'a', 'size': 8}
    },
    'sprite_check_collision_data': {
        'routine': 'sprite_check_collision_data',
        'params': [],
        'return': {'reg': 'a', 'size': 8}
    },
    'sprite_create_from_data': {
        'routine': 'sprite_create_from_data',
        'params': [
            {'name': 'sprite_num', 'store': 'y', 'size': 8},
            {'name': 'data_address', 'store': 'ax', 'size': 16},
        ]
    },
}