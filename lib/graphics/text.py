"""
This file contains the assembly language routines for text and
cursor manipulation on the C64 screen.
"""
from typing import Dict, List

def get_text_routines() -> Dict[str, List[str]]:
    """Returns a dictionary of all text-related assembly routines."""
    return {
        "set_cursor": [
            "set_cursor:",
            "    ; Input: X = row, Y = col",
            "    JSR $FFF0 ; KERNAL PLOT routine",
            "    RTS"
        ],
        "print_char": [
            "print_char:",
            "    ; Input: A = character code",
            "    JSR $FFD2 ; KERNAL CHROUT routine",
            "    RTS"
        ],
        "set_char_color": [
            "set_char_color:",
            "    ; Input: A = color code",
            "    ; This routine sets the color of the character at the current cursor position.",
            "    LDX $D3     ; Get cursor column from memory",
            "    LDY $D6     ; Get cursor row from memory",
            "    ; Calculate offset in color RAM: offset = row * 40 + col",
            "    ; We need a multiplication routine for this, or a loop.",
            "    ; For simplicity, we will use a loop here.",
            "    LDA #0",
            "    STA $FB       ; Temp storage for high byte of offset",
            "    STA $FC       ; Temp storage for low byte of offset",
            "CALC_LOOP:",
            "    CPY #0",
            "    BEQ CALC_DONE",
            "    CLC",
            "    LDA $FC",
            "    ADC #40",
            "    STA $FC",
            "    BCC NO_CARRY",
            "    INC $FB",
            "NO_CARRY:",
            "    DEY",
            "    JMP CALC_LOOP",
            "CALC_DONE:",
            "    CLC",
            "    TXA",
            "    ADC $FC",
            "    STA $FC",
            "    BCC NO_CARRY2",
            "    INC $FB",
            "NO_CARRY2:",
            "    ; Now $FB/$FC holds the offset. Add base address of color RAM.",
            "    CLC",
            "    LDA #<$D800",
            "    ADC $FC",
            "    STA $FD",
            "    LDA #>$D800",
            "    ADC $FB",
            "    STA $FE",
            "    ; Finally, store the color (passed in A) at the calculated address",
            "    PHA         ; Save color from A register",
            "    LDY #0",
            "    PLA         ; Restore color to A register",
            "    STA ($FD),Y",
            "    RTS"
        ]
    }
