# lib/builtins.py
"""
Defines the built-in functions and their properties for the compiler.
"""

from .symbols import Function, DataType, Variable

# This is a simplified list. I will add more as needed.
BUILTIN_FUNCTIONS = {
    "print": Function(name="print", parameters=[Variable(name="val", data_type=DataType.INT16)], return_type=DataType.VOID),
    "len": Function(name="len", parameters=[Variable(name="obj", data_type=DataType.VOID)], return_type=DataType.INT16),
    "abs": Function(name="abs", parameters=[Variable(name="val", data_type=DataType.INT16)], return_type=DataType.INT16, entry_label="abs"),
    "exp": Function(name="exp", parameters=[Variable(name="val", data_type=DataType.INT16)], return_type=DataType.INT16, entry_label="exp"),
    "log": Function(name="log", parameters=[Variable(name="val", data_type=DataType.INT16)], return_type=DataType.INT16, entry_label="log"),
    "input": Function(name="input", parameters=[], return_type=DataType.STRING, entry_label="input"),
    "float": Function(name="float", parameters=[Variable(name="val", data_type=DataType.INT16)], return_type=DataType.FLOAT32, entry_label="float"),

    # Graphics
    "gfx_turn_on": Function(name="gfx_turn_on", parameters=[], return_type=DataType.VOID, entry_label="gfx_turn_on"),
    "gfx_turn_off": Function(name="gfx_turn_off", parameters=[], return_type=DataType.VOID, entry_label="gfx_turn_off"),
    "gfx_clear_screen": Function(name="gfx_clear_screen", parameters=[], return_type=DataType.VOID, entry_label="gfx_clear_screen"),
    "draw_line": Function(name="draw_line", parameters=[], return_type=DataType.VOID, entry_label="draw_line"),
    "draw_circle": Function(name="draw_circle", parameters=[], return_type=DataType.VOID, entry_label="draw_circle"),
    "draw_ellipse": Function(name="draw_ellipse", parameters=[], return_type=DataType.VOID, entry_label="draw_ellipse"),
    "draw_rect": Function(name="draw_rect", parameters=[], return_type=DataType.VOID, entry_label="draw_rect"),

    # Sprites
    "sprite_enable": Function(name="sprite_enable", parameters=[], return_type=DataType.VOID, entry_label="sprite_enable"),
    "sprite_disable": Function(name="sprite_disable", parameters=[], return_type=DataType.VOID, entry_label="sprite_disable"),
    "sprite_set_pos": Function(name="sprite_set_pos", parameters=[], return_type=DataType.VOID, entry_label="sprite_set_pos"),
    "sprite_set_color": Function(name="sprite_set_color", parameters=[], return_type=DataType.VOID, entry_label="sprite_set_color"),
    "sprite_expand_xy": Function(name="sprite_expand_xy", parameters=[], return_type=DataType.VOID, entry_label="sprite_expand_xy"),
    "sprite_set_multicolor": Function(name="sprite_set_multicolor", parameters=[], return_type=DataType.VOID, entry_label="sprite_set_multicolor"),
    "sprite_set_priority": Function(name="sprite_set_priority", parameters=[], return_type=DataType.VOID, entry_label="sprite_set_priority"),
    "sprite_set_pointer": Function(name="sprite_set_pointer", parameters=[], return_type=DataType.VOID, entry_label="sprite_set_pointer"),
    "sprite_set_x_msb": Function(name="sprite_set_x_msb", parameters=[], return_type=DataType.VOID, entry_label="sprite_set_x_msb"),
    "sprite_set_x_msb_clear": Function(name="sprite_set_x_msb_clear", parameters=[], return_type=DataType.VOID, entry_label="sprite_set_x_msb_clear"),
    "sprite_set_multicolor_colors": Function(name="sprite_set_multicolor_colors", parameters=[], return_type=DataType.VOID, entry_label="sprite_set_multicolor_colors"),
    "sprite_check_collision_sprite": Function(name="sprite_check_collision_sprite", parameters=[], return_type=DataType.INT16, entry_label="sprite_check_collision_sprite"),
    "sprite_check_collision_data": Function(name="sprite_check_collision_data", parameters=[], return_type=DataType.INT16, entry_label="sprite_check_collision_data"),
    "sprite_create_from_data": Function(name="sprite_create_from_data", parameters=[], return_type=DataType.VOID, entry_label="sprite_create_from_data"),
}
