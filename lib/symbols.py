# lib/symbols.py
"""Manages the symbol table for the compiler."""

from typing import List, Dict, Optional
from enum import Enum
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

class SymbolTable:
    """Manages symbols, variables, and scopes in a structured way."""
    
    def __init__(self):
        self.global_vars: Dict[str, Variable] = {}
        self.functions: Dict[str, Function] = {}
        self.current_scope: str = "global"
        self.scope_stack: List[str] = ["global"]
        self.local_vars_stack: List[Dict[str, Variable]] = [{}]
    
    def enter_scope(self, scope_name: str):
        """Enters a new scope (function)."""
        self.scope_stack.append(scope_name)
        self.current_scope = scope_name
        self.local_vars_stack.append({})
    
    def exit_scope(self):
        """Exits the current scope."""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.local_vars_stack.pop()
            self.current_scope = self.scope_stack[-1]
    
    def declare_variable(self, name: str, data_type: DataType) -> Variable:
        """Declares a new variable in the current scope."""
        var = Variable(name, data_type, scope=self.current_scope)
        
        if self.current_scope == "global":
            self.global_vars[name] = var
        else:
            self.local_vars_stack[-1][name] = var
        
        return var
    
    def lookup_variable(self, name: str) -> Optional[Variable]:
        """Looks for a variable in the available scopes."""
        # First, search in local scopes (from deepest to shallowest)
        for local_vars in reversed(self.local_vars_stack[1:]):
            if name in local_vars:
                return local_vars[name]
        
        # Then, search in global variables
        return self.global_vars.get(name)
    
    def declare_function(self, name: str, params: List[Variable], return_type: DataType) -> Function:
        """Declares a new function."""
        func = Function(name, params, return_type)
        self.functions[name] = func
        return func
    
    def lookup_function(self, name: str) -> Optional[Function]:
        """Looks for a function."""
        return self.functions.get(name)