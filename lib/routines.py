from typing import Dict, List, Set

from .graphics.drawing import get_drawing_routines, get_drawing_package_data
from .graphics.scrolling import get_scrolling_routines
from .graphics.sprites import get_sprite_routines
from .graphics.text import get_text_routines
from .math.arithmetic import get_math_routines

class RoutineManager:
    """Manages library routines and their dependencies."""

    def __init__(self):
        self.available_routines: Dict[str, List[str]] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self.used_routines: Set[str] = set()

        # Load routines from their new locations
        self.available_routines.update(get_drawing_routines())
        self.available_routines.update(get_drawing_package_data())
        self.available_routines.update(get_scrolling_routines())
        self.available_routines.update(get_sprite_routines())
        self.available_routines.update(get_math_routines())
        self.available_routines.update(self._get_list_routines())
        self.available_routines.update(get_text_routines())

        # Define dependencies
        self.dependencies = {
            "SLINE": ["C824", "C841", "C912", "C931", "C92A", "C858", "C855", "C86B", "C868", "C879", "C894", "C8E2", "C9BB", "C9A6", "C979"],
            "CLLINE": ["C824", "C841", "C912", "C931", "C92A", "C858", "C855", "C86B", "C868", "C879", "C894", "C8E2", "C9BB", "C9A6", "C979"],
            "PLOT": ["C858", "C879", "C894", "C8E2"],
            "UNPLOT": ["C855", "C879", "C894", "C8E2"],
            "GCLEAR": ["C912", "C937"],
            "SCOLOR": ["C931"],
            "PCOLOR": ["C92A"],
            "GON": ["C824"],
            "GOFF": ["C841"],
            "SCROLL": ["CCOO", "CCBB", "CCE5", "CC86", "CCAB", "CC8D"],
            "print_int16": ["divide16x16"]
        }

    def mark_routine_used(self, routine_name: str):
        """Marks a routine as used and recursively adds its dependencies."""
        if routine_name in self.available_routines and routine_name not in self.used_routines:
            self.used_routines.add(routine_name)

            # Recursively add dependencies
            if routine_name in self.dependencies:
                for dep in self.dependencies[routine_name]:
                    self.mark_routine_used(dep)

    def _get_list_routines(self) -> Dict[str, List[str]]:
        """Returns the routines for list manipulation."""
        # ZP_PTR1 = $FB/$FC
        # ZP_PTR2 = $FD/$FE
        return {
            "get_list_element": [
                "; Routine to get an element from a list",
                "; Input:",
                ";   LIST_ROUTINE_ARG1: 16-bit pointer to the list",
                ";   LIST_ROUTINE_ARG2: 16-bit index",
                "; Output:",
                ";   LIST_ROUTINE_RET1: 16-bit value of the element",
                "GET_LIST_ELEMENT:",
                "; 1. Calculate offset = index * 2",
                "    LDA LIST_ROUTINE_ARG2",
                "    ASL A",
                "    STA $FB",
                "    LDA LIST_ROUTINE_ARG2+1",
                "    ROL A",
                "    STA $FC",
                "; 2. Add 1 to offset to get past the length byte",
                "    CLC",
                "    LDA $FB",
                "    ADC #1",
                "    STA $FB",
                "    BCC GET_ELEM_NO_CARRY",
                "    INC $FC",
                "GET_ELEM_NO_CARRY:",
                "; 3. Calculate final address = base_ptr + offset",
                "    CLC",
                "    LDA LIST_ROUTINE_ARG1",
                "    ADC $FB",
                "    STA $FD",
                "    LDA LIST_ROUTINE_ARG1+1",
                "    ADC $FC",
                "    STA $FE",
                "; 4. Dereference pointer to get the value",
                "    LDY #0",
                "    LDA ($FD),Y",
                "    STA LIST_ROUTINE_RET1",
                "    INY",
                "    LDA ($FD),Y",
                "    STA LIST_ROUTINE_RET1+1",
                "    RTS",
            ]
        }

    def get_used_routines_code(self) -> List[str]:
        """Returns the assembly code for all used routines."""
        code = []
        for routine_name in self.used_routines:
            if routine_name in self.available_routines:
                code.extend(self.available_routines[routine_name])
                code.append("")  # Blank line between routines

        return code
