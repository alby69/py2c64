# lib/routines.py
"""Manages and provides assembly routines for the compiler."""

from typing import Dict, List, Set
from .graphics.drawing import get_drawing_routines
from .graphics.sprites import get_sprite_routines
from .math.arithmetic import get_arithmetic_routines

def get_all_routines() -> Dict[str, List[str]]:
    """Returns a dictionary of all assembly routines."""
    routines = {}
    routines.update(get_drawing_routines())
    routines.update(get_sprite_routines())
    routines.update(get_arithmetic_routines())
    return routines

class RoutineManager:
    """Manages the inclusion of assembly routines."""
    def __init__(self):
        self.all_routines = get_all_routines()
        self.used_routines: Set[str] = set()

    def mark_routine_used(self, name: str):
        """Marks a routine as used."""
        if name in self.all_routines and name not in self.used_routines:
            self.used_routines.add(name)

    def get_used_routines_code(self) -> List[str]:
        """Returns the assembly code for all used routines."""
        code = []
        for name in sorted(list(self.used_routines)):
            if name in self.all_routines:
                code.extend(self.all_routines[name])
        return code
