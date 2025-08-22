# lib/symbols.py
"""Manages the symbol table for the compiler."""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from lib.core import DataType, Function, Variable  # Import core types

class SymbolTable:
    """Gestisce simboli, variabili e scope in modo strutturato"""
    
    def __init__(self):
        self.global_vars: Dict[str, Variable] = {}
        self.functions: Dict[str, Function] = {}
        self.current_scope: str = "global"
        self.scope_stack: List[str] = ["global"]
        self.local_vars_stack: List[Dict[str, Variable]] = [{}]
    
    def enter_scope(self, scope_name: str):
        """Entra in un nuovo scope (funzione)"""
        self.scope_stack.append(scope_name)
        self.current_scope = scope_name
        self.local_vars_stack.append({})
    
    def exit_scope(self):
        """Esce dallo scope corrente"""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.local_vars_stack.pop()
            self.current_scope = self.scope_stack[-1]
    
    def declare_variable(self, name: str, data_type: DataType) -> Variable:
        """Dichiara una nuova variabile nello scope corrente"""
        var = Variable(name, data_type, scope=self.current_scope)
        
        if self.current_scope == "global":
            self.global_vars[name] = var
        else:
            self.local_vars_stack[-1][name] = var
        
        return var
    
    def lookup_variable(self, name: str) -> Optional[Variable]:
        """Cerca una variabile negli scope disponibili"""
        # Prima cerca negli scope locali (dal più profondo al più superficiale)
        for local_vars in reversed(self.local_vars_stack[1:]):
            if name in local_vars:
                return local_vars[name]
        
        # Poi cerca nelle variabili globali
        return self.global_vars.get(name)
    
    def declare_function(self, name: str, params: List[Variable], return_type: DataType) -> Function:
        """Dichiara una nuova funzione"""
        func = Function(name, params, return_type)
        self.functions[name] = func
        return func
    
    def lookup_function(self, name: str) -> Optional[Function]:
        """Cerca una funzione"""
        return self.functions.get(name)