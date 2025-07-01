# py2c64: A Python to 6502 Assembly Compiler for the Commodore 64

`py2c64` is an experimental compiler that translates a subset of the Python language into 6502 assembly code, specifically targeting the Commodore 64. The project aims to make retro-programming more accessible by combining Python's clean, modern syntax with the challenge and charm of low-level 8-bit development.

## Core Concept

This project explores the challenges of compiling a high-level, dynamic language for a resource-constrained 8-bit architecture, blending the simplicity of Python with the satisfaction of direct hardware control.

The compiler is continuously evolving. Currently, it supports the following Python features:

### Core Language
-   **Data Types**:
    -   16-bit signed integers (`int`).
    -   32-bit floating-point numbers (`float`), with arithmetic routines based on Steve Wozniak's work for the Apple II.
-   **Arithmetic Operations**:
    -   **Integer**: `+`, `-`, `*`, `//` (integer division), `^` (XOR).
    -   **Floating-Point**: `+`, `-`, `*`, `/`.
-   **Control Flow**:
    -   `if/else` conditional statements.
-   **Functions**:
    -   Function definitions (`def`) and calls.
    -   Stack-based parameter passing and local variable management using a frame pointer.
    -   `return` statements for both values and void returns.
-   **Built-in Functions**:
    -   `print()`: For printing string literals and numeric values to the screen.
    -   Type casting: `int()`, `float()`.
    -   Math: `abs()`, `log()`, `exp()`.

### Commodore 64 Graphics Library
An integrated library for controlling the C64's high-resolution (320x200) bitmap mode. The necessary routines are automatically linked if used in the Python source.

-   `gfx_turn_on()`: Initializes bitmap graphics mode.
-   `gfx_turn_off()`: Restores the standard text mode.
-   `gfx_clear_screen()`: Clears the entire 8KB graphics screen.
-   `draw_line(x1, y1, x2, y2)`: Draws a line between two points using an efficient implementation of Bresenham's algorithm.
-   `draw_ellipse(xm, ym, xr, yr)`: Draws an ellipse (or a circle if `xr`==`yr`) centered at (xm, ym) with the given X and Y radii.
-   `draw_circle(x, y, r)`: Draws a circle centered at (x, y) with the given radius.

### Commodore 64 Sprite Library
An integrated library for controlling the C64's hardware sprites.

-   `sprite_set_pos(sprite_num, x, y)`: Sets the screen position of a sprite. `sprite_num` is 0-7, `x` is 0-319 (16-bit), `y` is 0-255 (8-bit). Note: The MSB for X coordinates > 255 is handled by a
## How to Use

The project is driven by the `test.py` script, which acts as both a test runner and a compiler frontend.

1.  **Write Python Code**: Create a new Python file inside the `py2c64/test_suite/` directory (e.g., `test_my_program.py`).
2.  **Define a Test Case**: Inside your new file, create a list named `test_cases`. Each item in the list is a dictionary that defines a single compilation unit:
    -   `name`: A descriptive name for your program.
    -   `code`: A multi-line string containing the Python code to be compiled.
    -   `expected`: The name of the output assembly file (e.g., `my_program.asm`) that will be saved in `py2c64/test_suite/expected_outputs/`.
3.  **Compile the Code**: Run the `test.py` script from the root of the project.

    ```bash
    # Compile and verify all test cases in the test_suite/ directory
    python py2c64/test.py

    # Compile and verify only a specific file
    python py2c64/test.py test_my_program.py
    ```

4.  **Regenerate Expected Output**: If you modify the compiler and need to update the reference assembly files, use the `--regenerate` flag. This will overwrite the existing files in `expected_outputs/` with the new output.

    ```bash
    # Regenerate all expected files
    python py2c64/test.py --regenerate

    # Regenerate a single expected file
    python py2c64/test.py --regenerate test_my_program.py
    ```

## Project Structure

-   `py2c64/main.py`: The main entry point for the compiler.
-   `py2c64/lib/`: Contains the core compiler logic, including AST processing, routine definitions, and code generation for various language features.
-   `py2c64/test.py`: The test runner.
-   `py2c64/test_suite/`: Contains the Python test cases.
-   `py2c64/test_suite/expected_outputs/`: Contains the expected assembly output for regression testing.

## Roadmap for Future Development

The project is a work in progress. Future enhancements are planned in two main areas:

### Expanding Language Support

-   [ ] **Loops**: Implement `for` and `while` loops.
-   [ ] **Comparisons & Logic**: Full support for comparison (`==`, `!=`, `<`, `>`, `<=`, `>=`) and boolean (`and`, `or`, `not`) operators.
-   [ ] **Data Structures**: Introduce support for basic arrays or lists with static allocation.
-   [ ] **Global Variables**: Proper handling of the `global` keyword within functions.

### Improving Tooling and C64 Integration

-   [ ] **Code Optimization**: Add a peephole optimizer pass to make the generated assembly smaller and faster.
-   [ ] **Enhanced C64 Libraries**: Add support for more C64 features, such as sprites, character graphics, and the SID sound chip.
-   [ ] **Error Reporting**: Improve error messages to include line and column numbers from the source Python file.
-   [ ] **Emulator Integration**: Create a "compile and run" workflow that automatically launches the compiled program in an emulator like VICE.

