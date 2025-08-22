# lib/graphics/drawing.py
"""Drawing routines for the compiler."""

from typing import Dict, List

def get_drawing_routines() -> Dict[str, List[str]]:
    """Returns a dictionary of all drawing-related assembly routines."""
    return {
        "print_int16": [ # Should be in an IO module, but moving here for now
            "PRINT_INT16:",
            "  LDX #0",
            "  LDA PRINT_VALUE+1", "  BNE print_nonzero",
            "  LDA PRINT_VALUE", "  BNE print_nonzero",
            "  LDA #'0'", "  JSR $FFD2", "  RTS",
            "print_nonzero:",
            "  LDA PRINT_VALUE+1", "  PHA",
            "  LDA PRINT_VALUE", "  PHA",
            "  JSR $BDCD", "  RTS"
        ],
        "gfx_turn_on": ["gfx_turn_on:", "RTS"],
        "gfx_turn_off": ["gfx_turn_off:", "RTS"],
        "gfx_clear_screen": ["gfx_clear_screen:", "RTS"],
        "draw_line": ["draw_line:", "RTS"],
        "draw_circle": ["draw_circle:", "RTS"],
        "draw_ellipse": ["draw_ellipse:", "RTS"],
        "draw_rect": ["draw_rect:", "RTS"],
    }
