# lib/core.py
"""Core classes for the py2c64 compiler."""

from typing import List, Dict, Any, Optional
from enum import Enum
import ast
from dataclasses import dataclass, field

class DataType(Enum):
    INT16 = "int16"
    FLOAT32 = "float32"
    STRING = "string"
    VOID = "void"

class OperationType(Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"
    EQ = "eq"
    NE = "ne"
    LT = "lt"
    GT = "gt"
    LE = "le"
    GE = "ge"

@dataclass
class Variable:
    name: str
    data_type: DataType
    address: Optional[int] = None
    scope: str = "global"
    is_parameter: bool = False

@dataclass
class Function:
    name: str
    parameters: List[Variable]
    return_type: DataType
    local_vars: Dict[str, Variable] = field(default_factory=dict)
    entry_label: Optional[str] = None

class CodeGenerator(ABC, ast.NodeVisitor):
    """Abstract base class for code generators using the Visitor pattern."""

    def __init__(self, symbol_table: SymbolTable, label_manager: LabelManager, output: AssemblyOutput):
        self.symbol_table = symbol_table
        self.label_manager = label_manager
        self.output = output

    @abstractmethod
    def visit_program(self, node: Program) -> Any:
        pass

    @abstractmethod
    def visit_literal(self, node: Literal) -> Any:
        pass

    @abstractmethod
    def visit_identifier(self, node: Identifier) -> Any:
        pass

    @abstractmethod
    def visit_binary_operation(self, node: BinaryOperation) -> Any:
        pass

    @abstractmethod
    def visit_function_call(self, node: FunctionCall) -> Any:
        pass

    @abstractmethod
    def visit_assignment(self, node: Assignment) -> Any:
        pass

    @abstractmethod
    def visit_if_statement(self, node: IfStatement) -> Any:
        pass

    @abstractmethod
    def visit_while_statement(self, node: WhileStatement) -> Any:
        pass

    @abstractmethod
    def visit_for_statement(self, node: ForStatement) -> Any:
        pass

    @abstractmethod
    def visit_function_definition(self, node: FunctionDefinition) -> Any:
        pass

    @abstractmethod
    def visit_return_statement(self, node: ReturnStatement) -> Any:
        pass

class Py2C64Compiler:
    """Compiler principale che orchestra tutto il processo"""

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.label_manager = LabelManager()
        self.output = AssemblyOutput()
        self.parser = PythonASTParser(self.symbol_table)
        self.code_generator = C64CodeGenerator(self.symbol_table, self.label_manager, self.output)
        self.routine_manager = RoutineManager()
        self.optimizer = PeepholeOptimizer()
    
    def compile_code(self, python_code: str) -> str:
        """Compila codice Python in assembly 6502"""
        try:
            # 1. Parsing
            ast_tree = self.parser.parse(python_code)
            
            # 2. Generazione codice
            self.code_generator.visit_program(ast_tree)
            
            # 3. Aggiunta routine utilizzate
            self._add_required_routines()
            
            # 4. Generazione output
            assembly_code = self.output.generate()
            
            # 5. Ottimizzazione
            lines = assembly_code.split('\n')
            optimized_lines = self.optimizer.optimize(lines)
            
            return '\n'.join(optimized_lines)
            
        except Exception as e:
            raise CompilerError(f"Compilation failed: {str(e)}")
    
    def _add_required_routines(self):
        """Aggiunge le routine necessarie alla sezione routine"""
        # Marca le routine utilizzate nel generatore di codice
        for routine_name in self.code_generator.used_routines:
            self.routine_manager.mark_routine_used(routine_name)
        
        # Ottieni il codice delle routine
        routine_code = self.routine_manager.get_used_routines_code()
        
        # Aggiungile alla sezione routine
        self.output.switch_to_routines_section()
        self.output.add_lines(routine_code)

        # Aggiunge anche le variabili necessarie
        self._add_required_variables()
    
    def _add_required_variables(self):
        """Aggiunge le variabili necessarie per le routine"""
        self.output.switch_to_data_section()
        
        # Variabili per operazioni matematiche
        if "multiply16x16" in self.routine_manager.used_routines:
            self.output.add_lines([
                "MULT_ARG1:      .word 0",
                "MULT_ARG2:      .word 0",
                "MULT_RESULT:    .dword 0"
            ])
        
        if "divide16x16" in self.routine_manager.used_routines:
            self.output.add_lines([
                "DIV_DIVIDEND:   .word 0",
                "DIV_DIVISOR:    .word 0",
                "DIV_QUOTIENT:   .word 0",
                "DIV_REMAINDER:  .word 0"
            ])
        
        if "print_int16" in self.routine_manager.used_routines:
            self.output.add_lines([
                "PRINT_VALUE:    .word 0",
                "PRINT_BUFFER:   .res 8"
            ])

        # Variabili generali
        self.output.add_lines([
            "RETURN_VALUE:   .word 0",
            "FRAME_POINTER:  .byte 0"
        ])

        # Variabili temporanee
        for i in range(self.code_generator.temp_var_counter):
            self.output.add_line(f"TEMP_{i}:        .word 0")
        
        # Variabili globali del programma
        for var_name, variable in self.symbol_table.global_vars.items():
            if variable.data_type == DataType.INT16:
                self.output.add_line(f"{var_name}:        .word 0")
            elif variable.data_type == DataType.FLOAT32:
                self.output.add_line(f"{var_name}:        .dword 0")