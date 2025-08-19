# lib/core.py
"""The main compiler orchestrator."""

from .symbols import SymbolTable, DataType
from .labels import LabelManager
from .output import AssemblyOutput
from .parser import PythonASTParser
from .c64 import C64CodeGenerator
from .routines import RoutineManager
from .optimizer import PeepholeOptimizer
from .errors import CompilerError

class Py2C64Compiler:
    """The main compiler class that orchestrates the compilation process."""

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.label_manager = LabelManager()
        self.output = AssemblyOutput()
        self.parser = PythonASTParser(self.symbol_table)
        self.code_generator = C64CodeGenerator(self.symbol_table, self.label_manager, self.output)
        self.routine_manager = RoutineManager()
        self.optimizer = PeepholeOptimizer()
    
    def compile_code(self, python_code: str) -> str:
        """Compiles Python code to 6502 assembly."""
        try:
            # 1. Parsing
            ast_tree = self.parser.parse(python_code)
            
            # 2. Code Generation
            self.code_generator.visit_program(ast_tree)
            
            # 3. Add required routines
            self._add_required_routines()
            
            # 4. Add required variables
            self._add_required_variables()

            # 5. Generate final output
            assembly_code = self.output.generate()
            
            # 6. Optimization
            lines = assembly_code.split('\n')
            optimized_lines = self.optimizer.optimize(lines)
            
            return '\n'.join(optimized_lines)
            
        except Exception as e:
            # Re-raise as a CompilerError for consistent error handling
            raise CompilerError(f"Compilation failed: {str(e)}")
    
    def _add_required_routines(self):
        """Adds the necessary routines to the output."""
        for routine_name in self.code_generator.used_routines:
            self.routine_manager.mark_routine_used(routine_name)
        
        routine_code = self.routine_manager.get_used_routines_code()
        
        self.output.switch_to_routines_section()
        self.output.add_lines(routine_code)
    
    def _add_required_variables(self):
        """Adds the necessary variables for routines and global scope."""
        self.output.switch_to_data_section()
        
        used_routines = self.routine_manager.used_routines

        if "multiply16x16" in used_routines:
            self.output.add_lines(["MULT_ARG1:      .word 0", "MULT_ARG2:      .word 0", "MULT_RESULT:    .dword 0"])
        if "divide16x16" in used_routines:
            self.output.add_lines(["DIV_DIVIDEND:   .word 0", "DIV_DIVISOR:    .word 0", "DIV_QUOTIENT:   .word 0", "DIV_REMAINDER:  .word 0"])
        if "print_int16" in used_routines:
            self.output.add_lines(["PRINT_VALUE:    .word 0", "PRINT_BUFFER:   .res 8"])
        
        if "get_list_element" in used_routines:
            self.output.add_lines([
                "LIST_ROUTINE_ARG1: .word 0",
                "LIST_ROUTINE_ARG2: .word 0",
                "LIST_ROUTINE_RET1: .word 0"
            ])

        # General variables
        self.output.add_lines(["RETURN_VALUE:   .word 0", "FRAME_POINTER:  .byte 0"])
        
        # Add heap pointer if list support is used
        if self.code_generator.list_support_initialized:
            self.output.add_lines([
                "HEAP_POINTER:   .word $C000 ; Start of heap memory for dynamic allocation"
            ])

        # Temporary variables
        for i in range(self.code_generator.temp_var_counter):
            self.output.add_line(f"TEMP_{i}:        .word 0")
        
        # Global variables from the program
        for var_name, variable in self.symbol_table.global_vars.items():
            if variable.data_type == DataType.INT16:
                self.output.add_line(f"{var_name}:        .word 0")
            elif variable.data_type == DataType.FLOAT32:
                self.output.add_line(f"{var_name}:        .dword 0")