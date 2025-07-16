# lib/errors.py
"""Defines custom compiler errors."""

from typing import Optional
import sys
class CompilerError(Exception):
    """Eccezione personalizzata per errori di compilazione"""
    
    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Formatta il messaggio di errore con informazioni di posizione"""
        if self.line is not None and self.column is not None:
            return f"Error at line {self.line}, column {self.column}: {self.message}"
        return f"Compilation error: {self.message}"