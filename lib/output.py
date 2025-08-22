# lib/output.py
"""Manages the assembly output for the compiler."""

from typing import List

class AssemblyOutput:
    """Manages the different sections of the assembly output."""
    def __init__(self):
        self.code_section: List[str] = []
        self.data_section: List[str] = []
        self.routines_section: List[str] = []
        self.current_section = self.code_section

    def add_line(self, line: str):
        """Adds a line to the current section."""
        self.current_section.append(line)

    def add_lines(self, lines: List[str]):
        """Adds multiple lines to the current section."""
        self.current_section.extend(lines)

    def add_instruction(self, instruction: str, operand: str = ""):
        """Adds a formatted instruction to the current section."""
        if operand:
            self.add_line(f"  {instruction} {operand}")
        else:
            self.add_line(f"  {instruction}")

    def add_label(self, label: str):
        """Adds a label to the current section."""
        self.add_line(f"{label}:")

    def switch_to_code_section(self):
        """Switches the current section to the code section."""
        self.current_section = self.code_section

    def switch_to_data_section(self):
        """Switches the current section to the data section."""
        self.current_section = self.data_section

    def switch_to_routines_section(self):
        """Switches the current section to the routines section."""
        self.current_section = self.routines_section

    def generate(self) -> str:
        """Generates the final assembly code as a single string."""
        # Basic structure of the assembly file
        header = [
            "*=$0801",
            "    !byte $0c, $08, $0a, $00, $9e, $20, $28, $32, $30, $36, $31, $29, $00, $00, $00",
            "PROGRAM_START:",
        ]
        
        sections = [
            ("CODE", self.code_section),
            ("ROUTINES", self.routines_section),
            ("DATA", self.data_section),
        ]
        
        full_code = header
        for name, section in sections:
            if section:
                full_code.append(f"\n; --- {name} SECTION ---")
                full_code.extend(section)
        
        return "\n".join(full_code)
