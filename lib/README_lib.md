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

-   **Control and Positioning**:
    -   `sprite_enable(mask)` / `sprite_disable(mask)`: Enables/disables sprites using a bitmask.
    -   `sprite_set_pos(sprite_num, x, y)`: Sets the position (0-255) of a specific sprite.
    -   `sprite_set_x_msb(mask)` / `sprite_set_x_msb_clear(mask)`: Sets or clears the 9th bit (Most Significant Bit) of the X-coordinate for one or more sprites, allowing positions greater than 255.
    -   `sprite_set_pointer(sprite_num, pointer_val)`: Sets the data pointer for a sprite, which determines its graphical data source.
-   **Appearance and Color**:
    -   `sprite_set_color(sprite_num, color)`: Sets the individual color of a sprite.
    -   `sprite_set_multicolor(mask)`: Enables multicolor mode for specific sprites.
    -   `sprite_set_multicolor_colors(mc1, mc2)`: Sets the two global multicolor registers for all multicolor sprites.
    -   `sprite_expand_xy(y_mask, x_mask)`: Expands sprites vertically and/or horizontally.
-   **Interaction and Data**:
    -   `sprite_set_priority(mask)`: Sets the priority of sprites (foreground vs. background).
    -   `sprite_check_collision_sprite()` / `sprite_check_collision_data()`: Reads the sprite-to-sprite and sprite-to-data collision registers.
    -   `sprite_create_from_data(sprite_num, source_addr)`: Copies 63 bytes from a source memory address to a sprite's data area and sets its pointer accordingly.

---

## 2. Compiler Internal Modules

This section describes the role of each Python module within the `lib/` directory, which forms the core of the `py2c64` compiler.

-   `__init__.py`: A standard Python file that marks the `lib` directory as a package, allowing for relative imports between the internal modules.

-   `ast_processor.py`: The central processor for the Abstract Syntax Tree (AST). It traverses the tree generated from the Python source and dispatches each node type (e.g., `ast.Assign`, `ast.FunctionDef`, `ast.For`) to the appropriate handler function to generate assembly code. It orchestrates the entire code generation process.

-   `c64_gfx_routines.py`: A repository of pre-written 6502 assembly routines for C64-specific graphics and sprite operations (e.g., `gfx_turn_on`, `draw_line`, `sprite_set_pos`). These routines are included in the final assembly output only if they are used by the Python code.

-   `func_core.py`: Provides fundamental, low-level functions used throughout the compiler. This includes managing global and local variables, creating unique labels for jumps and loops, managing temporary variables for intermediate calculations, and generating assembly for basic memory operations.

-   `func_dict.py`: Contains the logic for handling Python dictionary operations, specifically creating dictionaries and assigning values to keys (`my_dict[key] = value`).

-   `func_expressions.py`: Responsible for the recursive translation of Python expressions into assembly. It handles constants, variable lookups, function calls, and operations, breaking them down into a sequence of assembly instructions. It works closely with `func_operations.py`.

-   `func_operations.py`: Provides specialized handlers for specific low-level operations. It contains the code generation logic for 16-bit integer arithmetic (add, sub, mul, div), floating-point arithmetic, and comparison operations (`==`, `!=`, `<`, etc.).

-   `func_strings.py`: Manages string-related operations. Its primary role is to handle the `print()` function, generating code to print both string literals and the values of variables to the screen.

-   `func_structures.py`: This module contains handlers for high-level control flow structures, although much of this logic is currently coordinated by `ast_processor.py`.