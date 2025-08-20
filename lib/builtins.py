"""
Defines the built-in functions available in the py2c64 language.
"""

from .symbols import DataType, Variable, Function

BUILTIN_FUNCTIONS = [
    # C64 Hardware Functions
    Function(name="gfx_turn_on", parameters=[], return_type=DataType.VOID),
    Function(name="gfx_turn_off", parameters=[], return_type=DataType.VOID),
    Function(name="gfx_clear_screen", parameters=[], return_type=DataType.VOID),
    Function(name="draw_line", parameters=[
        Variable(name="x1", data_type=DataType.INT16),
        Variable(name="y1", data_type=DataType.INT16),
        Variable(name="x2", data_type=DataType.INT16),
        Variable(name="y2", data_type=DataType.INT16),
    ], return_type=DataType.VOID),
    Function(name="sprite_enable", parameters=[Variable(name="mask", data_type=DataType.INT16)], return_type=DataType.VOID),
    Function(name="sprite_disable", parameters=[Variable(name="mask", data_type=DataType.INT16)], return_type=DataType.VOID),
    Function(name="sprite_set_pos", parameters=[
        Variable(name="sprite_num", data_type=DataType.INT16),
        Variable(name="x", data_type=DataType.INT16),
        Variable(name="y", data_type=DataType.INT16),
    ], return_type=DataType.VOID),
    Function(name="sprite_set_pointer", parameters=[
        Variable(name="sprite_num", data_type=DataType.INT16),
        Variable(name="address", data_type=DataType.INT16),
    ], return_type=DataType.VOID),
    Function(name="sprite_set_priority", parameters=[Variable(name="priority_mask", data_type=DataType.INT16)], return_type=DataType.VOID),
    Function(name="sprite_expand_xy", parameters=[Variable(name="mask", data_type=DataType.INT16)], return_type=DataType.VOID),
    Function(name="sprite_set_multicolor", parameters=[Variable(name="mask", data_type=DataType.INT16)], return_type=DataType.VOID),
    Function(name="sprite_set_multicolor_colors", parameters=[
        Variable(name="mc1", data_type=DataType.INT16),
        Variable(name="mc2", data_type=DataType.INT16),
    ], return_type=DataType.VOID),
    Function(name="sprite_create_from_data", parameters=[
        Variable(name="address", data_type=DataType.INT16),
        Variable(name="data", data_type=DataType.STRING), # This might be tricky
    ], return_type=DataType.VOID),
    Function(name="draw_ellipse", parameters=[
        Variable(name="x", data_type=DataType.INT16),
        Variable(name="y", data_type=DataType.INT16),
        Variable(name="rx", data_type=DataType.INT16),
        Variable(name="ry", data_type=DataType.INT16),
    ], return_type=DataType.VOID),
    Function(name="draw_circle", parameters=[
        Variable(name="x", data_type=DataType.INT16),
        Variable(name="y", data_type=DataType.INT16),
        Variable(name="r", data_type=DataType.INT16),
    ], return_type=DataType.VOID),
    Function(name="draw_rect", parameters=[
        Variable(name="x1", data_type=DataType.INT16),
        Variable(name="y1", data_type=DataType.INT16),
        Variable(name="x2", data_type=DataType.INT16),
        Variable(name="y2", data_type=DataType.INT16),
    ], return_type=DataType.VOID),
    Function(name="sprite_set_color", parameters=[
        Variable(name="sprite_num", data_type=DataType.INT16),
        Variable(name="color", data_type=DataType.INT16),
    ], return_type=DataType.VOID),
    Function(name="sprite_set_x_msb", parameters=[Variable(name="mask", data_type=DataType.INT16)], return_type=DataType.VOID),
    Function(name="sprite_set_x_msb_clear", parameters=[Variable(name="mask", data_type=DataType.INT16)], return_type=DataType.VOID),
    Function(name="sprite_check_collision_data", parameters=[], return_type=DataType.INT16),
    Function(name="sprite_check_collision_sprite", parameters=[], return_type=DataType.INT16),


    # Math Functions
    Function(name="abs", parameters=[Variable(name="n", data_type=DataType.INT16)], return_type=DataType.INT16),
    Function(name="sgn", parameters=[Variable(name="n", data_type=DataType.FLOAT32)], return_type=DataType.INT16),
    Function(name="log", parameters=[Variable(name="n", data_type=DataType.FLOAT32)], return_type=DataType.FLOAT32),
    Function(name="exp", parameters=[Variable(name="n", data_type=DataType.FLOAT32)], return_type=DataType.FLOAT32),

    # I/O Functions
    Function(name="input", parameters=[], return_type=DataType.INT16), # Simplified return type

    # Type Conversion
    Function(name="float", parameters=[Variable(name="n", data_type=DataType.INT16)], return_type=DataType.FLOAT32),
    Function(name="int", parameters=[Variable(name="n", data_type=DataType.FLOAT32)], return_type=DataType.INT16),
]
