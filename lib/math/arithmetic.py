# lib/math/arithmetic.py
"""Arithmetic routines for the compiler."""

from typing import Dict, List

def get_arithmetic_routines() -> Dict[str, List[str]]:
    """Returns a dictionary of all arithmetic assembly routines."""
    return {
        "multiply16x16": [
            "multiply16x16:",
            "  LDA #0", "  STA MULT_RESULT", "  STA MULT_RESULT+1", "  STA MULT_RESULT+2", "  STA MULT_RESULT+3",
            "  LDX #16",
            "multiply_loop:",
            "  LSR MULT_ARG2+1", "  ROR MULT_ARG2",
            "  BCC no_add",
            "  CLC",
            "  LDA MULT_RESULT+2", "  ADC MULT_ARG1", "  STA MULT_RESULT+2",
            "  LDA MULT_RESULT+3", "  ADC MULT_ARG1+1", "  STA MULT_RESULT+3",
            "no_add:",
            "  ROR MULT_RESULT+3", "  ROR MULT_RESULT+2", "  ROR MULT_RESULT+1", "  ROR MULT_RESULT",
            "  DEX", "  BNE multiply_loop",
            "  RTS"
        ],
    }
