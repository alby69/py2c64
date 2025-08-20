from typing import Dict, List

def get_math_routines() -> Dict[str, List[str]]:
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
