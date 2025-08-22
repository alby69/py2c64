# lib/symbols.py
"""Manages the symbol table for the compiler."""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

class DataType(Enum):
    INT16 = "int16"
    FLOAT32 = "float32"
    STRING = "string"
    VOID = "void"
    LIST = "list"

class OperationType(Enum):
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"
    XOR = "^"
    EQ = "=="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="

class UnaryOperationType(Enum):
    NEG = "-"
    NOT = "not"

class BoolOpType(Enum):
    AND = "and"
    OR = "or"

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
    is_interrupt_handler: bool = False

class SymbolTable:
    """Manages symbols, variables, and scopes."""
    
    def __init__(self):
        self.global_vars: Dict[str, Variable] = {}
        self.functions: Dict[str, Function] = {}
        self.current_scope: Optional[Function] = None

    def enter_scope(self, func_name: str):
        self.current_scope = self.functions.get(func_name)

    def exit_scope(self):
        self.current_scope = None

    def declare_variable(self, name: str, data_type: DataType, is_parameter: bool = False) -> Variable:
        var = Variable(name=name, data_type=data_type, is_parameter=is_parameter)
        if self.current_scope:
            self.current_scope.local_vars[name] = var
        else:
            self.global_vars[name] = var
        return var

    def lookup_variable(self, name: str) -> Optional[Variable]:
        if self.current_scope:
            if name in self.current_scope.local_vars:
                return self.current_scope.local_vars[name]
        return self.global_vars.get(name)

    def declare_function(self, name: str, params: List, return_type: DataType, is_interrupt: bool = False) -> Function:
        parameters = [Variable(p.arg, DataType.INT16, is_parameter=True) for p in params] # Simplified
        func = Function(name, parameters, return_type, is_interrupt_handler=is_interrupt)
        self.functions[name] = func
        return func

    def lookup_function(self, name: str) -> Optional[Function]:
        return self.functions.get(name)

    def register_builtins(self, builtins: Dict[str, Any]):
        for name, func_data in builtins.items():
            self.functions[name] = func_data
