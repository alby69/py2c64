# lib/output.py
"""Manages assembly code output."""

from typing import List

class AssemblyOutput:
    """Gestisce l'output assembly con sezioni organizzate"""
    
    def __init__(self):
        self.data_section: List[str] = []
        self.code_section: List[str] = []
        self.routines_section: List[str] = []
        self.current_section: List[str] = self.code_section
    
    def add_line(self, line: str):
        """Aggiunge una riga alla sezione corrente"""
        self.current_section.append(line)
    
    def add_lines(self, lines: List[str]):
        """Aggiunge multiple righe alla sezione corrente"""
        self.current_section.extend(lines)
    
    def add_label(self, label: str):
        """Aggiunge una label"""
        self.add_line(f"{label}:")
    
    def add_instruction(self, opcode: str, operand: str = ""):
        """Aggiunge un'istruzione assembly"""
        if operand:
            self.add_line(f"    {opcode} {operand}")
        else:
            self.add_line(f"    {opcode}")
    
    def switch_to_data_section(self):
        """Cambia alla sezione dati"""
        self.current_section = self.data_section
    
    def switch_to_code_section(self):
        """Cambia alla sezione codice"""
        self.current_section = self.code_section
    
    def switch_to_routines_section(self):
        """Cambia alla sezione routine"""
        self.current_section = self.routines_section
    
    def generate(self) -> str:
        """Genera l'output assembly completo"""
        result = []
        
        if self.data_section:
            result.append("; === DATA SECTION ===")
            result.extend(self.data_section)
            result.append("")
        
        if self.code_section:
            result.append("; === CODE SECTION ===")
            result.extend(self.code_section)
            result.append("")
        
        if self.routines_section:
            result.append("; === ROUTINES SECTION ===")
            result.extend(self.routines_section)
            result.append("")

        return "\n".join(result)