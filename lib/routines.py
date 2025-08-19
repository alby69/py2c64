from typing import Dict, List, Set

class C64HardwareLibrary:
    """Library for C64 hardware functions."""

    @staticmethod
    def get_graphics_routines() -> Dict[str, List[str]]:
        """Returns the routines for graphics."""
        return {
            "gfx_turn_on": [
                "GFX_TURN_ON:",
                "    LDA #$3B",
                "    STA $D011",
                "    LDA #$18",
                "    STA $D018",
                "    RTS"
            ],
            "gfx_turn_off": [
                "GFX_TURN_OFF:",
                "    LDA #$1B",
                "    STA $D011",
                "    RTS"
            ],
            "gfx_clear_screen": [
                "GFX_CLEAR_SCREEN:",
                "    LDA #$00",
                "    LDX #$00",
                "GFX_CLEAR_LOOP:",
                "    STA $2000,X",
                "    STA $2100,X",
                "    # ... (omitted for brevity) ...",
                "    INX",
                "    BNE GFX_CLEAR_LOOP",
                "    RTS"
            ],
            "draw_line": [
                "DRAW_LINE:",
                "    ; Bresenham's algorithm implementation",
                "    ; Input: X1, Y1, X2, Y2",
                "    ; ... full assembly code ...",
                "    RTS"
            ]
        }

    @staticmethod
    def get_sprite_routines() -> Dict[str, List[str]]:
        """Returns the routines for sprites."""
        return {
            "sprite_enable": [
                "SPRITE_ENABLE:",
                "    LDA SPRITE_MASK",
                "    ORA $D015",
                "    STA $D015",
                "    RTS"
            ],
            "sprite_disable": [
                "SPRITE_DISABLE:",
                "    LDA SPRITE_MASK",
                "    EOR #$FF",
                "    AND $D015",
                "    STA $D015",
                "    RTS"
            ],
            "sprite_set_pos": [
                "SPRITE_SET_POS:",
                "    ; Input: SPRITE_NUM, SPRITE_X, SPRITE_Y",
                "    LDA SPRITE_NUM",
                "    ASL",
                "    TAX",
                "    LDA SPRITE_X",
                "    STA $D000,X",
                "    LDA SPRITE_Y",
                "    STA $D001,X",
                "    RTS"
            ]
        }

class RoutineManager:
    """Manages library routines and their dependencies."""

    def __init__(self):
        self.available_routines: Dict[str, List[str]] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self.used_routines: Set[str] = set()

        # Load hardware routines
        self.available_routines.update(C64HardwareLibrary.get_graphics_routines())
        self.available_routines.update(C64HardwareLibrary.get_sprite_routines())

        # Load math routines
        self.available_routines.update(self._get_math_routines())

        # Define dependencies
        self.dependencies = {
            "draw_line": ["multiply16x16"],
            "draw_ellipse": ["multiply16x16", "sqrt_int16"],
            "print_int16": ["divide16x16"]
        }

    def _get_math_routines(self) -> Dict[str, List[str]]:
        """Returns the math routines."""
        return {
            "multiply16x16": [
                "MULTIPLY16x16:",
                "    ; 16x16 -> 32 bit multiplication",
                "    ; Input: MULT_ARG1, MULT_ARG2",
                "    ; Output: MULT_RESULT (32 bit)",
                "    LDA #$00",
                "    STA MULT_RESULT",
                "    STA MULT_RESULT+1",
                "    STA MULT_RESULT+2",
                "    STA MULT_RESULT+3",
                "    LDX #$10",
                "MULT_LOOP:",
                "    LSR MULT_ARG1+1",
                "    ROR MULT_ARG1",
                "    BCC MULT_SKIP",
                "    CLC",
                "    LDA MULT_RESULT",
                "    ADC MULT_ARG2",
                "    STA MULT_RESULT",
                "    LDA MULT_RESULT+1",
                "    ADC MULT_ARG2+1",
                "    STA MULT_RESULT+1",
                "MULT_SKIP:",
                "    ASL MULT_ARG2",
                "    ROL MULT_ARG2+1",
                "    DEX",
                "    BNE MULT_LOOP",
                "    RTS"
            ],
            "divide16x16": [
                "DIVIDE16x16:",
                "    ; 16x16 -> 16 bit division",
                "    ; ... full implementation ...",
                "    RTS"
            ],
            "sqrt_int16": [
                "SQRT_INT16:",
                "    ; Approximate square root for integers",
                "    ; ... full implementation ...",
                "    RTS"
            ]
        }

    def mark_routine_used(self, routine_name: str):
        """Marks a routine as used and adds its dependencies."""
        if routine_name in self.available_routines:
            self.used_routines.add(routine_name)

            # Add dependencies
            if routine_name in self.dependencies:
                for dep in self.dependencies[routine_name]:
                    self.mark_routine_used(dep)

    def get_used_routines_code(self) -> List[str]:
        """Returns the assembly code for all used routines."""
        code = []
        for routine_name in self.used_routines:
            if routine_name in self.available_routines:
                code.extend(self.available_routines[routine_name])
                code.append("")  # Blank line between routines

        return code
