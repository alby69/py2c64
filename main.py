# main.py
"""
Command-line interface for the py2c64 compiler.
"""

import argparse
from lib.core import Py2C64Compiler
from lib.errors import CompilerError

def main():
    """
    Parses command-line arguments and runs the compiler.
    """
    parser = argparse.ArgumentParser(
        description="Compile Python code to 6502 assembly for the Commodore 64."
    )
    parser.add_argument(
        "input_file",
        help="The Python source file to compile (.py)."
    )
    parser.add_argument(
        "-o", "--output",
        help="The output assembly file name (.asm). Defaults to the input file name with .asm extension."
    )
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            python_code = f.read()

        # Instantiate the compiler and compile the code
        compiler = Py2C64Compiler()
        assembly_code = compiler.compile_code(python_code)

        # Determine the output file name
        output_file = args.output
        if not output_file:
            if args.input_file.lower().endswith('.py'):
                output_file = args.input_file[:-3] + ".asm"
            else:
                output_file = args.input_file + ".asm"

        # Write the assembly code to the output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(assembly_code)

        print(f"Compilation successful. Assembly code written to {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file not found: '{args.input_file}'")
    except CompilerError as e:
        print(f"Compilation failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
