# lib/graphics/sprites.py
"""Sprite routines for the compiler."""

from typing import Dict, List

def get_sprite_routines() -> Dict[str, List[str]]:
    """Returns a dictionary of all sprite-related assembly routines."""
    return {
        "sprite_enable": ["sprite_enable:", "RTS"],
        "sprite_disable": ["sprite_disable:", "RTS"],
        "sprite_set_pos": ["sprite_set_pos:", "RTS"],
        "sprite_set_color": ["sprite_set_color:", "RTS"],
        "sprite_expand_xy": ["sprite_expand_xy:", "RTS"],
        "sprite_set_multicolor": ["sprite_set_multicolor:", "RTS"],
        "sprite_set_priority": ["sprite_set_priority:", "RTS"],
        "sprite_set_pointer": ["sprite_set_pointer:", "RTS"],
        "sprite_set_x_msb": ["sprite_set_x_msb:", "RTS"],
        "sprite_set_x_msb_clear": ["sprite_set_x_msb_clear:", "RTS"],
        "sprite_set_multicolor_colors": ["sprite_set_multicolor_colors:", "RTS"],
        "sprite_check_collision_sprite": ["sprite_check_collision_sprite:", "RTS"],
        "sprite_check_collision_data": ["sprite_check_collision_data:", "RTS"],
        "sprite_create_from_data": ["sprite_create_from_data:", "RTS"],
    }
