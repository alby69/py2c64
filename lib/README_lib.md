# py2c64 Library Reference

This document provides a reference for the built-in libraries available in `py2c64` for interacting with the Commodore 64 hardware.

## 1. User-Facing Libraries

### Commodore 64 Graphics Library
An integrated library for controlling the C64's high-resolution (320x200) bitmap mode. The necessary routines are automatically linked if used in the Python source.

-   `gfx_turn_on()`: Initializes bitmap graphics mode.
-   `gfx_turn_off()`: Restores the standard text mode.
-   `gfx_clear_screen()`: Clears the entire 8KB graphics screen.
-   `draw_line(x1, y1, x2, y2)`: Draws a line between two points using an efficient implementation of Bresenham's algorithm.
-   `draw_ellipse(xm, ym, xr, yr)`: Draws an ellipse (or a circle if `xr`==`yr`) centered at (xm, ym) with the given X and Y radii.
-   `draw_circle(x, y, r)`: Draws a circle centered at (x, y) with the given radius.
-   `draw_rect(x1, y1, x2, y2)`: Draws a rectangle defined by two opposite corners.

### Commodore 64 Sprite Library
An integrated library for controlling the C64's hardware sprites.

-   `sprite_enable(mask)`: Enables sprites using a bitmask (e.g., `0b00000001` for sprite 0).
-   `sprite_disable(mask)`: Disables sprites using a bitmask.
-   `sprite_set_pos(sprite_num, x, y)`: Sets the position (X: 0-255, Y: 0-255) of a specific sprite.
-   `sprite_set_x_msb(mask)`: Sets the 9th bit of the X-coordinate for sprites in the mask, allowing X positions > 255.
-   `sprite_set_x_msb_clear(mask)`: Clears the 9th bit of the X-coordinate.
-   `sprite_set_color(sprite_num, color)`: Sets the individual color (0-15) of a sprite.
-   `sprite_set_multicolor(mask)`: Enables multicolor mode for specified sprites.
-   `sprite_set_multicolor_colors(mc1, mc2)`: Sets the two global multicolor registers ($D025, $D026).
-   `sprite_expand_xy(y_mask, x_mask)`: Expands sprites vertically and/or horizontally.
-   `sprite_set_priority(mask)`: Sets sprite priority (1=behind background, 0=in front).
-   `sprite_set_pointer(sprite_num, pointer_val)`: Sets the data pointer for a sprite. The address is `pointer_val * 64`.
-   `sprite_create_from_data(sprite_num, source_addr)`: Copies 63 bytes from a source memory address to a dedicated sprite data area and sets the sprite's pointer to it.
-   `sprite_check_collision_sprite()`: Returns the sprite-to-sprite collision register.
-   `sprite_check_collision_data()`: Returns the sprite-to-data collision register.

---

## 2. Compiler Internal Modules

This section describes the role of each Python module within the `lib/` directory, which forms the core of the `py2c64` compiler.

-   `__init__.py`: A standard Python file that marks the `lib` directory as a package, allowing for relative imports between the internal modules.

-   `ast_processor.py`: The central processor for the Abstract Syntax Tree (AST). It traverses the tree and orchestrates the code generation process by delegating tasks to specialized modules like `func_expressions` for expressions, `func_structures` for control flow, and `func_c64` for hardware calls.

-   `c64_routine_library.py`: A library of generator functions that produce 6502 assembly for C64-specific graphics and sprite operations (e.g., `gfx_turn_on`, `draw_line`, `sprite_set_pos`).

-   `func_core.py`: Provides fundamental, low-level functions used throughout the compiler. This includes managing global and local variables, creating unique labels for jumps and loops, managing temporary variables for intermediate calculations, and generating assembly for basic memory operations.

-   `func_dict.py`: Contains experimental and incomplete logic for handling Python dictionary operations. Currently, most dictionary features are not supported.

-   `func_expressions.py`: Responsible for the recursive translation of Python expressions into assembly. It handles constants, variable lookups, function calls, and operations, breaking them down into a sequence of assembly instructions. It works closely with `func_operations.py`.

-   `func_operations.py`: Provides specialized handlers for specific low-level operations. It contains the code generation logic for 16-bit integer arithmetic (add, sub, mul, div), floating-point arithmetic, and comparison operations (`==`, `!=`, `<`, etc.).

-   `func_strings.py`: Manages string-related operations. Its primary role is to handle the `print()` function and f-string concatenation.

-   `func_structures.py`: Contains handlers for high-level control flow structures like `if`, `for`, and `while`, separating this logic from the main AST processor.

-   `routines.py`: This module consolidates all assembly routines, both generic (like `multiply16x16`) and C64-specific. It manages a dependency graph to ensure that when a routine is used, any other routines it depends on are also included in the final assembly output.