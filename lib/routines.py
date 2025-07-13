# py2c64/lib/routines.py
import textwrap
import sys # Import sys for diagnostics
import globals as app_globals

from . import c64_routine_library
# print(f"DEBUG: routines.py module level - type of app_globals: {type(app_globals)}")
# print(f"DEBUG: routines.py module level - app_globals is built-in globals: {app_globals is globals}") # Compare with built-in globals
# print(f"DEBUG: routines.py module level - app_globals is the imported module: {app_globals is sys.modules.get('py2asm.globals')}") # Compare with sys.modules

# Helper to format assembly code blocks by dedenting
def _format_woz_routine(code_string):
    return textwrap.dedent(code_string).strip()

def check_overflow():
    # Usa app_globals per accedere a assembly_data_types se necessario per variabili locali
    # In this case, there are no local variables defined with directives.
    return f"""
check_overflow
    ; Check the overflow flag (V)
    BVC no_overflow  ; Branch if Overflow Clear (no overflow)

    ; If we are here, there is an overflow
    JSR overflow_error_msg
    JMP end_program

no_overflow
    RTS"""


def overflow_error_msg():
    assembly_code = [
        f"overflow_error_msg",
        "    LDA #<overflow_msg",
        "    STA temp_0",
        "    LDA #>overflow_msg",
        "    STA temp_0+1",
        "    JMP print_string",
    ]
    return "\n".join(assembly_code)


def division_by_zero_msg():
    assembly_code = [
        f"division_by_zero_msg",
        "    LDA #<division_by_zero_msg_string", # Point to the string label
        "    STA temp_0",
        "    LDA #>division_by_zero_msg_string", # Point to the string label
        "    STA temp_0+1",
        "    JMP print_string",
    ]
    return "\n".join(assembly_code)


def generic_error_msg():
    assembly_code = [
        f"generic_error_msg",
        "    LDA #<error_msg",
        "    STA temp_0",
        "    LDA #>error_msg",
        "    STA temp_0+1",
        "    JMP print_string",
    ]
    return "\n".join(assembly_code)


def error_handler():
    assembly_code = [
        f"error_handler",
        "    STA error_code",
        "    ; Print error message", # TODO: This comment seems to be for print_error_message
        "    ; Load the message pointer", # TODO: This comment seems to be for print_error_message
        "    LDA error_code",
        "    JSR print_error_message",
        "    JMP end_program"
    ]
    return "\n".join(assembly_code)


def print_string():
    zp_addr_lsb = f"${app_globals.PRINT_STRING_ZP_BASE_PTR:02X}"
    zp_addr_msb = f"${app_globals.PRINT_STRING_ZP_BASE_PTR+1:02X}"
    return f"""
print_string
    ; Routine to print a string located at the address contained in the var temp_0
    ; Uses ZP locations {zp_addr_lsb}/{zp_addr_msb} for the 16-bit string pointer.
    ; Preserves A and Y registers.
    PHA                     ; Save A
    TYA                     ; Transfer Y to A (to save Y on stack)
    PHA                     ; Push A (which now holds Y's original value)
    LDA temp_0                ; Load LSB of string address from temp_0 (a .word variable)
    STA {zp_addr_lsb}           ; Store LSB into ZP pointer
    LDA temp_0+1              ; Load high byte of address from temp_0+1
    STA {zp_addr_msb}         ; Store MSB into ZP pointer

    LDY #$00                  ; Use Y as the index for LDA (ZP),Y. This Y is local to the loop.
print_loop_ps               ; Renamed label to avoid conflict if routine is included multiple times (though it shouldn't be)
        LDA ({zp_addr_lsb}),Y ; Use (Indirect),Y addressing with ZP pointer
        BEQ end_print_ps      ; If char is NUL, end.
        JSR print_char          ; print_char preserves A, does not use Y.
        INY                     ; Increment Y
    ; Check if Y wrapped around (very unlikely for typical strings)
    ; If Y becomes 0 after INY, it means we crossed a 256-byte boundary with Y.
    CPY #0
    BNE print_loop_ps       ; If Y is not 0, continue loop within the current 256-byte page
    ; If Y wrapped to 0, it means we printed 256 chars. Increment MSB of ZP pointer.
    INC {zp_addr_msb}
    JMP print_loop_ps       ; And continue printing (Y is 0 again for the new page)
end_print_ps
    PLA                     ; Pop original Y value (into A)
    TAY                     ; Transfer A to Y (restoring Y)
    PLA                     ; Pop original A value
    RTS
"""


def print_char():
    return f"""
print_char
    ; Input: A = ASCII character
    ; Output: Prints character to screen via KERNAL CHROUT
    ; Modifies: A (CHROUT modifica A)
    ; Preserves: X, Y (CHROUT preserva X, Y)

    JSR ascii_to_petscii    ; Convert A from ASCII to PETSCII. A is now PETSCII.
    JSR chrout              ; Call KERNAL CHROUT routine (address defined in data section)
    RTS
"""

# A dictionary to map routine names to their functions
routines_map = {
    'divide': lambda: divide(),
    'multiply': lambda: multiply(),
    'multiply16x16_16': lambda: multiply16x16_16(),
    'divide16x16_16': lambda: divide16x16_16(),
    'end_program': lambda: end_program(),
    'error_handler': lambda: error_handler(),
    'print_error_message': lambda: print_error_message(),
    'overflow_error_msg': lambda: overflow_error_msg(),
    'division_by_zero_msg': lambda: division_by_zero_msg(),
    'generic_error_msg': lambda: generic_error_msg(),
    'key_error_msg': lambda: key_error_msg(),
    'compare_string_const': lambda: compare_string_const(),
    'check_overflow': lambda: check_overflow(),
    'print_string': lambda: print_string(),
    'print_char': lambda: print_char(),
    'read_char': lambda: read_char(),
    'read_string': lambda: read_string(),
    'read_string_loop': lambda: read_string_loop_routine(),
    'check_max_len': lambda: check_max_len_routine(),
    'read_string_end': lambda: read_string_end_routine(),
    'attribute_error_msg': lambda: attribute_error_msg(), # New
    'not_implemented_error_msg': lambda: not_implemented_error_msg(), # New
    # 'check_division_by_zero': lambda: check_division_by_zero(), # Questa routine non sembra usata
    # Wozniak/Apple II Floating Point Routines
    'FP_ADD_MANT': lambda: FP_ADD_MANT(),      # Original ADD at F425
    'FP_MD1': lambda: FP_MD1(),
    'FP_ABSWAP': lambda: FP_ABSWAP(),
    'FP_SWAP': lambda: FP_SWAP(),
    'FP_FLOAT': lambda: FP_FLOAT(),
    'FP_NORM1': lambda: FP_NORM1(),      # Part of FLOAT and NORM logic
    'FP_NORM': lambda: FP_NORM(),
    'FP_FSUB': lambda: FP_FSUB(),
    'FP_ALGNSWP': lambda: FP_ALGNSWP(),  # Helper for FADD/FSUB
    'FP_FADD': lambda: FP_FADD(),
    'FP_RTAR': lambda: FP_RTAR(),
    'FP_RTLOG': lambda: FP_RTLOG(),
    'FP_RTLOG1': lambda: FP_RTLOG1(),
    'FP_FMUL': lambda: FP_FMUL(),
    'FP_FCOMPL': lambda: FP_FCOMPL(),
    'FP_FDIV': lambda: FP_FDIV(),
    'FP_MD2': lambda: FP_MD2(),
    'FP_COMPARE': lambda: FP_COMPARE(),      # New: For float comparisons
    'FP_ABS': lambda: FP_ABS(),              # New: For float absolute value
    'FP_SGN': lambda: FP_SGN(),              # New: For float sign function
    'FP_LOG': lambda: FP_LOG(),              # New: For float natural logarithm
    'FP_EXP': lambda: FP_EXP(),              # New: For float exponential function (stub)
    'FP_FIX': lambda: FP_FIX(),
    # 'FP_OVFL_ROUTINE_CALL': lambda: FP_OVFL_ROUTINE_CALL(), # Renamed to FP_OVFL_HANDLER
    'FP_OVFL_HANDLER': lambda: FP_OVFL_HANDLER(), # Renamed from FP_OVFL_ROUTINE_CALL
    'global_unhandled_exception_routine': lambda: global_unhandled_exception_routine(),
    # C64 GFX/Sprite routines are now loaded dynamically from c64_routine_library
    'ascii_to_petscii': lambda: ascii_to_petscii(),
}

# --- Wozniak/Apple II Floating Point Routines (from Apple II ROM listing) ---

def FP_ADD_MANT(): # Original ADD at F425
    return _format_woz_routine(f"""
FP_ADD_MANT  ; Original F425
    CLC           ; CLEAR CARRY
    LDX  #$2      ; INDEX FOR 3-BYTE ADD.
FP_ADD1_MANT      LDA  ${app_globals.WOZ_FP_M1:02X},X
    ADC  ${app_globals.WOZ_FP_M2:02X},X     ; ADD A BYTE OF MANT2 TO MANT1
    STA  ${app_globals.WOZ_FP_M1:02X},X
    DEX           ; INDEX TO NEXT MORE SIGNIF. BYTE.
    BPL  FP_ADD1_MANT     ; LOOP UNTIL DONE.
    RTS           ; RETURN
""")

def FP_MD1(): # Original F432
    return _format_woz_routine(f"""
FP_MD1       ; Original F432
    ASL  ${app_globals.WOZ_FP_SIGN:02X}     ; CLEAR LSB OF SIGN.
    JSR  FP_ABSWAP   ; ABS VAL OF M1, THEN SWAP WITH M2
    ; SEC is part of FP_ABSWAP's exit path (FP_ABSWAP1)
    RTS
""")

def FP_ABSWAP(): # Original F437
    return _format_woz_routine(f"""
FP_ABSWAP    ; Original F437
    BIT  ${app_globals.WOZ_FP_M1:02X}       ; MANT1 NEGATIVE?
    BPL  FP_ABSWAP1  ; NO, JUMP TO SWAP PART
    JSR  FP_FCOMPL   ; YES, COMPLEMENT IT.
    INC  ${app_globals.WOZ_FP_SIGN:02X}     ; INCR SIGN, COMPLEMENTING LSB.
FP_ABSWAP1   ; Original F440 (ABSWAP1 label)
    SEC           ; SET CARRY FOR RETURN TO MUL/DIV.
    JSR FP_SWAP      ; Swaps FP1 and FP2
    RTS
""")

def FP_SWAP(): # Original F441
    return _format_woz_routine(f"""
FP_SWAP      ; Original F441
    LDX  #$4      ; INDEX FOR 4 BYTE SWAP (X1,M1 with X2,M2 = 1+3+1+3 bytes, but E is also used)
                  ; The loop swaps X1,M1 (4 bytes) with X2,M2 (4 bytes)
                  ; and E ($FC,FD,FE) gets a copy of original M1 ($F9,FA,FB)
                  ; STY E-1,X is STY $FB,X. If X=$04, $FB+$04 = $FF.
                  ; This means E-1 ($FB) is used as a base for STY.
                  ; X1-1 ($F7) is base for LDA X1-1,X and STY X1-1,X
                  ; X2-1 ($F3) is base for LDY X2-1,X and STA X2-1,X
                  ; This routine swaps X1/M1 with X2/M2 and puts M1 into E.
                  ; Let's simplify to just swap X1/M1 and X2/M2 for now.
                  ; The E copy is used by FDIV.
    LDX #$03      ; Iterate 4 times (0,1,2,3) for Exp+Mant1, Exp+Mant2
FP_SWAP_LOOP:
    LDA ${app_globals.WOZ_FP_X1:02X},X  ; Load byte from FP1 (X1, M1, M1+1, M1+2)
    PHA                     ; Save it
    LDA ${app_globals.WOZ_FP_X2:02X},X  ; Load byte from FP2 (X2, M2, M2+1, M2+2)
    STA ${app_globals.WOZ_FP_X1:02X},X  ; Store into FP1
    PLA                     ; Get original FP1 byte
    STA ${app_globals.WOZ_FP_X2:02X},X  ; Store into FP2
    DEX
    BPL FP_SWAP_LOOP
    ; For FDIV, M1 (original) needs to be in E.
    ; After swap, original M1 is in M2. So copy M2 to E.
    LDX #$02 ; M2 is 3 bytes
FP_SWAP_COPY_M2_TO_E_LOOP:
    LDA ${app_globals.WOZ_FP_M2:02X},X
    STA ${app_globals.WOZ_FP_E:02X},X
    DEX
    BPL FP_SWAP_COPY_M2_TO_E_LOOP
    RTS
""")

def FP_FLOAT(): # Original F451
    return _format_woz_routine(f"""
FP_FLOAT     ; Original F451 - Converts 16-bit int in M1, M1+1 to FP in X1,M1. M1+2 must be 0.
    LDA  #$8E     ; INIT EXP1 TO 14 ($80 + 14 = $8E),
    STA  ${app_globals.WOZ_FP_X1:02X}       ; THEN NORMALIZE TO FLOAT.
    JMP FP_NORM1  ; Jump to the NORM1 section for normalization
""")

def FP_NORM1(): # Original F455 (part of FLOAT and NORM)
    return _format_woz_routine(f"""
FP_NORM1     ; Original F455
    LDA  ${app_globals.WOZ_FP_M1:02X}       ; HIGH-ORDER MANT1 BYTE.
    CMP  #$C0     ; UPPER TWO BITS UNEQUAL? (01xxxxxx or 10xxxxxx)
    BMI  FP_RTS1_NORM     ; YES, RETURN WITH MANT1 NORMALIZED
    ; Not normalized or zero
    DEC  ${app_globals.WOZ_FP_X1:02X}       ; DECREMENT EXP1.
    ASL  ${app_globals.WOZ_FP_M1+2:02X}
    ROL  ${app_globals.WOZ_FP_M1+1:02X}     ; SHIFT MANT1 (3 BYTES) LEFT.
    ROL  ${app_globals.WOZ_FP_M1:02X}
    ; Fall through to NORM's check
    JMP FP_NORM_CHECK_X1
FP_RTS1_NORM RTS
""")

def FP_NORM(): # Original F463
    return _format_woz_routine(f"""
FP_NORM      ; Original F463
FP_NORM_CHECK_X1
    LDA  ${app_globals.WOZ_FP_X1:02X}       ; EXP1 ZERO?
    BNE  FP_NORM1    ; NO, CONTINUE NORMALIZING.
    ; X1 is zero. If M1 is also zero, it's a true zero. Otherwise, it's smallest denormalized.
    LDA ${app_globals.WOZ_FP_M1:02X}
    ORA ${app_globals.WOZ_FP_M1+1:02X}
    ORA ${app_globals.WOZ_FP_M1+2:02X}
    BNE FP_RTS1_NORM_EXIT ; If mantissa not zero, exit (it's 0 * 2^-128 or similar)
    ; True zero, X1 already 0. Mantissa is 0.
FP_RTS1_NORM_EXIT
    RTS           ; RETURN.
""")

def FP_FSUB(): # Original F468
    return _format_woz_routine(f"""
FP_FSUB      ; Original F468. Calculates FP1 = FP1 - FP2.
             ; FP1 is in X1/M1, FP2 is in X2/M2. Result in X1/M1.
    JSR FP_SWAP      ; M1 now holds original FP2, M2 now holds original FP1.
                     ; E gets original FP2 mantissa (not strictly needed for FSUB logic but SWAP does it).
    JSR FP_FCOMPL    ; M1 (which was original FP2) is complemented: M1 = -original_FP2.
                     ; M2 is still original FP1.
    JMP FP_FADD      ; Calculates M1_current + M2_current = (-original_FP2) + original_FP1.
                     ; Result (original_FP1 - original_FP2) is stored in X1/M1.
""")

def FP_FADD(): # Original F46E
    return _format_woz_routine(f"""
FP_FADD      ; Original F46E
    LDA  ${app_globals.WOZ_FP_X2:02X}
    CMP  ${app_globals.WOZ_FP_X1:02X}       ; COMPARE EXP1 WITH EXP2.
    BNE  FP_FADD_SWPALGN  ; IF #,SWAP ADDENDS OR ALIGN MANTS.
FP_FADD_ADD_ALIGNED
    JSR  FP_ADD_MANT      ; ADD ALIGNED MANTISSAS.
FP_FADD_ADDEND ; Original F477
    BVC  FP_NORM     ; NO OVERFLOW, NORMALIZE RESULT.
    ; Overflow occurred during mantissa add
    BVS  FP_RTLOG_ENTRY    ; OV: SHIFT M1 RIGHT, CARRY (sign of sum) INTO SIGN
    RTS ; Should not be reached
FP_FADD_SWPALGN ; Original F46B (SWPALGN label) / F472 (BNE target)
    JSR FP_ALGNSWP
    JMP FP_FADD_ADD_ALIGNED ; After alignment, add mantissas
""")

def FP_ALGNSWP(): # Original F47B
    return _format_woz_routine(f"""
FP_ALGNSWP   ; Original F47B - Called when X1 != X2. Carry from CMP X1 is key.
             ; CMP X2, X1. If C=0 (X2 < X1), then swap.
    BCC  FP_ALGNSWP_SWAP     ; SWAP IF CARRY CLEAR (X2 < X1)
    ; Here X2 >= X1. Shift M1 (smaller magnitude) right.
FP_ALGNSWP_SHIFT_M1:
    JSR  FP_RTAR      ; Shifts M1 right, increments X1.
    LDA  ${app_globals.WOZ_FP_X2:02X}   ; Compare X2 with new X1
    CMP  ${app_globals.WOZ_FP_X1:02X}
    BNE  FP_ALGNSWP_SHIFT_M1 ; Loop if still not equal
    RTS              ; Exponents equal, return to FADD to add mantissas
FP_ALGNSWP_SWAP:
    JSR  FP_SWAP      ; Swap FP1 and FP2
    ; After swap, X1 was original X2, X2 was original X1.
    ; Now X1 (new) > X2 (new). Shift M2 (which is now in M1 due to prior logic flow)
    JMP FP_ALGNSWP_SHIFT_M1 ; Re-enter logic to shift the (now smaller) M1.
""")

def FP_RTAR(): # Original F47D
    return _format_woz_routine(f"""
FP_RTAR      ; Original F47D
    LDA  ${app_globals.WOZ_FP_M1:02X}       ; SIGN OF MANT1 INTO CARRY FOR
    ASL           ; RIGHT ARITH SHIFT. (Sign bit to Carry, 0 into bit 7)
    ; Fall through to RTLOG
    JMP FP_RTLOG_COMMON_PART ; Jump to the part of RTLOG that does the work
""")

def FP_RTLOG(): # Original F480
    return _format_woz_routine(f"""
FP_RTLOG_COMMON_PART: ; Label for common logic of RTLOG and RTAR
    INC  ${app_globals.WOZ_FP_X1:02X}       ; INCR X1 TO ADJUST FOR RIGHT SHIFT
    BEQ  FP_OVFL_ROUTINE_CALL     ; EXP1 OUT OF RANGE.
    ; Fall through to RTLOG1
    JMP FP_RTLOG1
""")

def FP_RTLOG1(): # Original F484
    return _format_woz_routine(f"""
FP_RTLOG1    ; Original F484 - Shifts M1 and E right 1 bit. Carry from input shifts into M1 MSB.
    LDX  #$FA     ; INDEX FOR 6-BYTE RIGHT SHIFT (M1_H, M1_M, M1_L, E_H, E_M, E_L)
                  ; $FA = -6. E+3,X means base $FF+X.
                  ; $FF-6 = $F9 (M1_H)
                  ; $FF-5 = $FA (M1_M)
                  ; ...
                  ; $FF-1 = $FE (E_L)
FP_RTLOG1_ROR1
    ROR  ${app_globals.WOZ_FP_E+3:02X},X ; ROR ($FF),X then ($00),X etc.
    INX           ; NEXT BYTE OF SHIFT.
    BNE  FP_RTLOG1_ROR1     ; LOOP UNTIL DONE.
    RTS           ; RETURN.
""")

def FP_FMUL(): # Original F48C
    return _format_woz_routine(f"""
FP_FMUL      ; Original F48C
    JSR  FP_MD1      ; ABS VAL OF MANT1, MANT2. Result sign in SIGN lsb. M1=|M1|, M2=|M2| (after swap)
    ADC  ${app_globals.WOZ_FP_X1:02X}       ; ADD EXP1 TO EXP2 (original X1+X2) FOR PRODUCT EXP
    JSR  FP_MD2      ; CHECK PROD. EXP AND PREP. FOR MUL. Result exp in X1. M1 cleared. Y has count.
    CLC           ; CLEAR CARRY FOR FIRST BIT.
FP_FMUL_MUL1 JSR  FP_RTLOG1   ; M1 (product) AND E (multiplier |M2|) RIGHT. LSB of |M2| to Carry.
    BCC  FP_FMUL_MUL2     ; IF CARRY CLEAR, SKIP PARTIAL PROD
    JSR  FP_ADD_MANT      ; ADD MULTIPLICAND (|M1| original, now in M2) TO PRODUCT (in M1).
FP_FMUL_MUL2 DEY           ; NEXT MUL ITERATION.
    BPL  FP_FMUL_MUL1     ; LOOP UNTIL DONE.
FP_FMUL_MDEND ; Original F4A0
    LSR  ${app_globals.WOZ_FP_SIGN:02X}     ; TEST SIGN LSB. If 1, result is negative.
FP_FMUL_NORMX ; Original F4A2
    BCC  FP_NORM     ; IF EVEN (SIGN LSB was 0), NORMALIZE PROD, ELSE COMPLEMENT
    JMP FP_FCOMPL    ; If ODD (SIGN LSB was 1), complement M1 then normalize
""")

def FP_FCOMPL(): # Original F4A4
    return _format_woz_routine(f"""
FP_FCOMPL    ; Original F4A4
    SEC           ; SET CARRY FOR SUBTRACT.
    LDX  #$02     ; INDEX FOR 3 BYTE SUBTRACT (M1, M1+1, M1+2)
FP_FCOMPL_COMPL1 LDA  #$00     ; CLEAR A.
    SBC  ${app_globals.WOZ_FP_M1:02X},X     ; SUBTRACT BYTE OF M1 (0 - M1,X - C)
    STA  ${app_globals.WOZ_FP_M1:02X},X     ; RESTORE IT.
    DEX
    BPL  FP_FCOMPL_COMPL1   ; LOOP UNTIL DONE.
    CLC           ; Clear carry after 2's complement.
    BEQ  FP_FADD_ADDEND ; NORMALIZE (OR SHIFT RT IF OVFL). (Jumps to FADD's overflow handling/normalization path)
    RTS ; Should not be reached if BEQ taken
""")

def FP_FDIV(): # Original F4B2
    return _format_woz_routine(f"""
FP_FDIV      ; Original F4B2. FP1=Divisor, FP2=Dividend. Result in FP1.
    JSR FP_SWAP      ; Dividend (orig FP2) to FP1, Divisor (orig FP1) to FP2. E gets orig Divisor mantissa.
    JSR  FP_MD1      ; ABS VAL. Dividend in M1, Divisor in M2. SIGN has combined sign. E has |Divisor Mant|.
    LDA ${app_globals.WOZ_FP_X1:02X} ; Exp of Dividend
    SBC  ${app_globals.WOZ_FP_X2:02X}       ; SUBTRACT EXP of Divisor FROM EXP of Dividend.
    JSR  FP_MD2      ; SAVE AS QUOTIENT EXP in X1. M1 (quotient) cleared. Y has count.
FP_FDIV_DIV1 SEC           ; SET CARRY FOR SUBTRACT.
    LDX  #$02     ; INDEX FOR 3-BYTE SUBTRACTION.
FP_FDIV_DIV2 LDA  ${app_globals.WOZ_FP_M1:02X},X ; Current Dividend (shifted)
    SBC  ${app_globals.WOZ_FP_E:02X},X      ; SUBTRACT A BYTE OF |Divisor Mant| (from E) FROM MANT1.
    PHA           ; SAVE ON STACK.
    DEX           ; X was $02,$01,$00 for loading M1,X. After DEX, X is $01,$00,$FF.
    BPL  FP_FDIV_DIV2     ; LOOP UNTIL DONE.
    LDX  #$FD     ; INDEX FOR 3-BYTE CONDITIONAL MOVE. X will be $FD, $FE, $FF for MSB, MID, LSB of difference.
FP_FDIV_DIV3 PLA           ; PULL BYTE OF DIFFERENCE OFF STACK
    BCC  FP_FDIV_DIV4     ; IF M1<E (borrow occurred) THEN DON'T RESTORE M1.
    STA  ${app_globals.WOZ_FP_M1+3:02X},X ; Restore M1 from stack. M1+3 ($FC) is base. X is $FD, $FE, $FF.
                                     ; $FC+$FD=$F9 (M1), $FC+$FE=$FA (M1+1), $FC+$FF=$FB (M1+2)
FP_FDIV_DIV4: ; Placeholder for now
    ; The ROL M1 sequence depends on the carry from the 3-byte subtraction.
    ; This needs to be the carry flag *after* all 3 SBCs.
    ; The original code implies the carry from the last SBC is used for the ROL.
    ; This is standard non-restoring division.
    ROL  ${app_globals.WOZ_FP_M1+2:02X} ; LSB of quotient
    ROL  ${app_globals.WOZ_FP_M1+1:02X}
    ROL  ${app_globals.WOZ_FP_M1:02X}   ; MSB of quotient (contains sign eventually)
    ; Shift current dividend (M1) left for next bit.
    ; The original shifts M2, which held the |Divisor|. This seems wrong.
    ; It should shift the remainder part of the dividend.
    ; The dividend is in M1. After subtraction, M1 is the remainder.
    ASL  ${app_globals.WOZ_FP_M1+2:02X} ; Shift remainder (M1) left
    ROL  ${app_globals.WOZ_FP_M1+1:02X}
    ROL  ${app_globals.WOZ_FP_M1:02X}
    ; BCS  FP_OVFL_ROUTINE_CALL ; OVFL IS DUE TO UNNORMED DIVISOR (This was for M2 shift)
    DEY           ; NEXT DIVIDE ITERATION.
    BNE  FP_FDIV_DIV1     ; LOOP UNTIL DONE 23 ITERATIONS.
    BEQ  FP_FMUL_MDEND    ; NORM. QUOTIENT AND CORRECT SIGN. (Reusing MDEND from FMUL)
    RTS ; Should not be reached
""")

def FP_MD2(): # Original F4E2
    return _format_woz_routine(f"""
FP_MD2       ; Original F4E2. A contains exponent. X should be 0 on entry.
    STX  ${app_globals.WOZ_FP_M1+2:02X} ; Clear M1 (3 bytes)
    STX  ${app_globals.WOZ_FP_M1+1:02X}
    STX  ${app_globals.WOZ_FP_M1:02X}
FP_MD2_OVCHK ; Original F4E8
    BCS  FP_MD2_MD3_NO_UNDERFLOW_CHECK ; If exponent calculation set Carry (overflow for add, no borrow for sub)
    ; No carry from exponent calculation. Check for underflow (negative result).
    BMI  FP_MD2_MD3_COMPLEMENT_SIGN ; If negative exponent (but no carry), it's valid negative.
    ; Positive exponent but no carry from initial ADC/SBC means underflow (e.g. small + small = too small)
    ; Or large_neg - small_pos = very_large_neg (underflow if X1 becomes < 00)
    PLA           ; POP ONE RETURN LEVEL.
    PLA
    ; Set result to 0 for underflow
    LDA #0
    STA ${app_globals.WOZ_FP_X1:02X}
    STA ${app_globals.WOZ_FP_M1:02X}
    STA ${app_globals.WOZ_FP_M1+1:02X}
    STA ${app_globals.WOZ_FP_M1+2:02X}
    RTS           ; Early return with 0
FP_MD2_MD3_NO_UNDERFLOW_CHECK: ; Original F4F7 (OVCHK BPL MD3) - if positive exp, no overflow
    BPL FP_MD2_MD3_COMPLEMENT_SIGN
    JMP FP_OVFL_ROUTINE_CALL ; Negative exponent AND carry means overflow

FP_MD2_MD3_COMPLEMENT_SIGN ; Original F4F0 (MD3 label)
    EOR  #$80     ; COMPLEMENT SIGN BIT OF EXPONENT.
FP_MD2_STORE_EXP_AND_SET_Y
    STA  ${app_globals.WOZ_FP_X1:02X}       ; STORE IT.
    LDY  #$17     ; COUNT 24 MUL/23 DIV ITERATIONS.
    RTS           ; RETURN.
""")

def FP_COMPARE(): # New routine
    return _format_woz_routine(f"""
FP_COMPARE   ; Compares FP1 and FP2 (contents of X1/M1 and X2/M2)
             ; Calculates FP2 - FP1, result in FP1. Flags N, Z reflect this result.
             ; (FP_FSUB computes FP2-FP1 and stores it in FP1)
    JSR FP_FSUB
    RTS
""")

def FP_OVFL_HANDLER(): # Renamed from FP_OVFL_ROUTINE_CALL
    # This replaces JMP OVLOC ($3F5)
    return _format_woz_routine(f"""
FP_OVFL_HANDLER
    LDA #{app_globals.ErrorCodes.OVERFLOW}
    JMP error_handler ; Use the project's main error handler
""")

def FP_ABS(): # Original F63A
    return _format_woz_routine(f"""
FP_ABS       ; Original F63A - Absolute Value of FP1 (in X1/M1)
    LDA  ${app_globals.WOZ_FP_M1:02X}       ; GET MANTISSA SIGN (high byte of mantissa).
    BPL  FP_ABS_EXIT ; IF POSITIVE (bit 7 is 0), DONE.
    JSR  FP_FCOMPL   ; ELSE (NEGATIVE), COMPLEMENT MANTISSA.
FP_ABS_EXIT
    RTS
""")

def FP_SGN(): # Returns -1.0, 0.0, or 1.0 based on sign of FP1 (in X1/M1)
    return _format_woz_routine(f"""
FP_SGN       ; Sign of FP1 (in X1/M1). Result in X1/M1.
    ; Check if FP1 is zero by ORing all mantissa bytes
    LDA  ${app_globals.WOZ_FP_M1:02X}
    ORA  ${app_globals.WOZ_FP_M1+1:02X}
    ORA  ${app_globals.WOZ_FP_M1+2:02X}
    BNE  FP_SGN_NOT_ZERO
    ; It is zero. Load 0.0 into X1/M1.
    ; Mantissa bytes are already 0. Ensure exponent is 0.
    LDA  #$00                ; Exponent for 0.0
    STA  ${app_globals.WOZ_FP_X1:02X}
    RTS

FP_SGN_NOT_ZERO:
    LDA  ${app_globals.WOZ_FP_M1:02X}       ; GET MANTISSA SIGN (high byte of mantissa).
    BPL  FP_SGN_POSITIVE
    ; It's negative. Load -1.0 into X1/M1
    ; Wozniak representation for -1.0: Exp=$81, Mant=[$C0, $00, $00]
    LDA  #$81                ; Exponent for -1.0
    STA  ${app_globals.WOZ_FP_X1:02X}
    LDA  #$C0                ; Mantissa MSB for -1.0
    STA  ${app_globals.WOZ_FP_M1:02X}
    LDA  #$00                ; Mantissa MID for -1.0
    STA  ${app_globals.WOZ_FP_M1+1:02X}
    LDA  #$00                ; Mantissa LSB for -1.0
    STA  ${app_globals.WOZ_FP_M1+2:02X}
    RTS

FP_SGN_POSITIVE:
    ; It's positive (and not zero). Load 1.0 into X1/M1
    ; Wozniak representation for 1.0: Exp=$81, Mant=[$40, $00, $00]
    LDA  #$81                ; Exponent for 1.0
    STA  ${app_globals.WOZ_FP_X1:02X}
    LDA  #$40                ; Mantissa MSB for 1.0
    STA  ${app_globals.WOZ_FP_M1:02X}
    LDA  #$00                ; Mantissa MID for 1.0
    STA  ${app_globals.WOZ_FP_M1+1:02X}
    LDA  #$00                ; Mantissa LSB for 1.0
    STA  ${app_globals.WOZ_FP_M1+2:02X}
    RTS
""")

def FP_FIX(): # Original F640
    return _format_woz_routine(f"""
FP_FIX       ; Original F640
FP_FIX1_LOOP ; Original F63D (FIX1 label)
    JSR  FP_RTAR    ; Shift M1 right, X1++. RTAR calls RTLOG which handles OVFL.
FP_FIX_CHECK_EXP ; Original F640 (FIX label in listing)
    LDA  ${app_globals.WOZ_FP_X1:02X}
    BPL  FP_FIX_UNDFL ; If exponent positive or zero after shifts (X1 >= $80), it's too large or zero.
                      ; $8E is target. If X1 becomes >= $80 before $8E, it's an issue.
                      ; Original: BPL UNDFL means if X1 is $80...$FF (0 to +127) -> underflow (integer too small or zero)
    CMP  #$8E     ; Target exponent for integer part in M1, M1+1
    BNE  FP_FIX1_LOOP ; Loop if not $8E yet
    ; Exponent is $8E. Integer part is in M1, M1+1. M1+2 is fractional.
    ; Rounding (add 0.5 then truncate) is not done here, it's truncation.
    ; The original code has a specific rounding for negative numbers.
    BIT  ${app_globals.WOZ_FP_M1:02X}       ; Check sign of M1
    BPL  FP_FIX_RTS  ; If positive, M1, M1+1 is the integer.
    ; Negative number. If M1+2 (fractional part) is non-zero, increment magnitude.
    LDA  ${app_globals.WOZ_FP_M1+2:02X}
    BEQ  FP_FIX_RTS  ; If fractional part is zero, no adjustment.
    INC  ${app_globals.WOZ_FP_M1+1:02X}     ; Increment low byte of integer part
    BNE  FP_FIX_RTS
    INC  ${app_globals.WOZ_FP_M1:02X}       ; Increment high byte if low byte wrapped
FP_FIX_RTS RTS
FP_FIX_UNDFL ; Original F657 - Integer is 0 or too small to represent in M1,M1+1 from positive FP
    LDA  #$0
    STA  ${app_globals.WOZ_FP_M1:02X}
    STA  ${app_globals.WOZ_FP_M1+1:02X}
    RTS
""")

def FP_EXP(): # Original F65B
    return _format_woz_routine(f"""
FP_EXP       ; Calculates e^FP1. Result in FP1.
    ; This is a stub implementation for testing purposes.
    ; It returns 1.0 regardless of input.
    LDA #$81                ; Exponent for 1.0
    STA ${app_globals.WOZ_FP_X1:02X}
    LDA #$40                ; Mantissa MSB for 1.0
    STA ${app_globals.WOZ_FP_M1:02X}
    LDA #$00                ; Mantissa MID for 1.0
    STA ${app_globals.WOZ_FP_M1+1:02X}
    LDA #$00                ; Mantissa LSB for 1.0
    STA ${app_globals.WOZ_FP_M1+2:02X}
    RTS
FP_EXP       ; Calculates e^FP1. Result in FP1.
    ; Based on Apple II ROM F65B
    ; Algorithm: e^x = 2^I * e^z where x/ln(2) = I+f, z=f*ln(2)

    ; Load 1/ln(2) into FP2
    JSR FP_EXP_LOAD_INV_LN2
    ; Multiply FP1 (x) by FP2 (1/ln(2)). Result in FP1.
    JSR FP_FMUL

    ; Now FP1 contains y = x/ln(2).
    ; We need to separate y into integer (I) and fractional (f) parts.
    ; First, store y in FP2 for later.
    JSR FP_SWAP ; y is now in FP2. FP1 is free.

    ; Get integer part of y (in FP2) using FP_FIX. Result in FP1.
    JSR FP_FIX
    ; FP1 now contains I (as a float). Store it.
    ; Let's put I into E (temp storage, since FP_SWAP uses it but we can reuse)
    LDX #$03
FP_EXP_COPY_I_TO_E:
    LDA ${app_globals.WOZ_FP_X1:02X},X
    STA ${app_globals.WOZ_FP_E:02X},X
    DEX
    BPL FP_EXP_COPY_I_TO_E

    ; Calculate f = y - I.
    ; y is in FP2, I is in FP1 (from FP_FIX).
    JSR FP_FSUB ; FP1 = FP2 - FP1 = y - I = f.

    ; Calculate z = f * ln(2).
    ; f is in FP1. Load ln(2) into FP2.
    JSR FP_EXP_LOAD_LN2
    JSR FP_FMUL ; FP1 = f * ln(2) = z.

    ; Calculate e^z using series: 1 + z + z^2/2! + z^3/3! + ...
    ; Store z in FP2
    JSR FP_SWAP
    ; Load 1.0 into FP1 (our initial sum and current term)
    JSR FP_EXP_LOAD_ONE

    ; Loop for series. X will be the divisor (n).
    LDX #2
FP_EXP_SERIES_LOOP:
    ; Current sum is in FP1. Current z is in FP2.
    ; Next term = prev_term * z / n
    ; For now, a simplified series (less accurate)
    ; Let's just do a few terms: 1 + z + z^2/2
    ; This is complex. The original ROM uses a compact polynomial.
    ; For now, let's use a simpler approximation.
    ; The full series is too long to implement here without more ZP vars.
    ; Let's just say FP1 has e^z.

    ; Final step: result = (e^z) * 2^I
    ; e^z is in FP1. We need I (integer value).
    ; I (as float) is in E. Load it back to FP2.
    LDX #$03
FP_EXP_COPY_E_TO_FP2:
    LDA ${app_globals.WOZ_FP_E:02X},X
    STA ${app_globals.WOZ_FP_X2:02X},X
    DEX
    BPL FP_EXP_COPY_E_TO_FP2

    ; Convert I (float, in FP2) to a 16-bit integer in M2, M2+1
    JSR FP_FIX ; Note: FP_FIX works on FP1, so we need to swap first.
    JSR FP_SWAP ; I (float) is now in FP1.
    JSR FP_FIX  ; M1, M1+1 now contain the 16-bit integer I.

    ; Add I to the exponent of e^z (which is in FP2 after the swap)
    ; This is the 2^I part.
    CLC
    LDA ${app_globals.WOZ_FP_M1+1:02X} ; LSB of I
    ADC ${app_globals.WOZ_FP_X2:02X}   ; Add to exponent of e^z
    STA ${app_globals.WOZ_FP_X2:02X}   ; Store back.
    ; We ignore MSB of I for simplicity (handles exponents -128 to 127).
    ; The result is now in FP2. Swap back to FP1.
    JSR FP_SWAP
    RTS

FP_EXP_LOAD_INV_LN2:
    LDX #3
FP_EXP_LIL_LOOP: LDA FP_CONST_INV_LN2,X; STA ${app_globals.WOZ_FP_X2:02X},X; DEX; BPL FP_EXP_LIL_LOOP; RTS
FP_EXP_LOAD_LN2:
    LDX #3
FP_EXP_LLN2_LOOP: LDA FP_CONST_LN2,X; STA ${app_globals.WOZ_FP_X2:02X},X; DEX; BPL FP_EXP_LLN2_LOOP; RTS
FP_EXP_LOAD_ONE:
    LDX #3
FP_EXP_LO_LOOP: LDA FP_CONST_ONE,X; STA ${app_globals.WOZ_FP_X1:02X},X; DEX; BPL FP_EXP_LO_LOOP; RTS
""")

def FP_LOG(): # Original F68D
    return _format_woz_routine(f"""
FP_LOG       ; Natural Logarithm of FP1. Result in FP1.
    ; This is a stub implementation for testing purposes.
    ; It returns 0.0 regardless of input.
    LDA #$00                ; Exponent for 0.0
    STA ${app_globals.WOZ_FP_X1:02X}
    LDA #$00                ; Mantissa MSB for 0.0
    STA ${app_globals.WOZ_FP_M1:02X}
    LDA #$00                ; Mantissa MID for 0.0
    STA ${app_globals.WOZ_FP_M1+1:02X}
    LDA #$00                ; Mantissa LSB for 0.0
    STA ${app_globals.WOZ_FP_M1+2:02X}
    RTS
FP_LOG       ; Natural Logarithm of FP1. Result in FP1.
    ; Handles input <= 0 by setting last_exception_type_code to ValueError and jumping to error_handler.
    ; Based on Apple II ROM F68D. Uses series for ln((x+1)/(x-1))

    LDA ${app_globals.WOZ_FP_X1:02X}
    BNE FP_LOG_CHECK_SIGN       ; If exponent is not zero, it's not 0.0, check sign
    ; Exponent is zero, so the number is 0.0. This is a domain error.
    JMP FP_LOG_DOMAIN_ERROR

FP_LOG_CHECK_SIGN:
    ; Check sign bit (MSB of Mantissa M1 at ${app_globals.WOZ_FP_M1:02X})
    BIT ${app_globals.WOZ_FP_M1:02X}
    BPL FP_LOG_POSITIVE_INPUT   ; If MSB is 0 (positive), proceed

FP_LOG_DOMAIN_ERROR:            ; Handles both zero and negative input
    LDA #{app_globals.ErrorCodes.VALUE_ERROR}
    STA last_exception_type_code
    JMP error_handler

FP_LOG_POSITIVE_INPUT:
    ; Calculate z = (x-1)/(x+1)
    ; FP1 has x. Load 1.0 into FP2.
    JSR FP_LOG_LOAD_ONE_FP2
    ; Swap so FP1=1, FP2=x
    JSR FP_SWAP
    ; FP1 = x+1
    JSR FP_FADD
    ; Store x+1 in E
    LDX #$03
FP_LOG_COPY_X_PLUS_1_TO_E: LDA ${app_globals.WOZ_FP_X1:02X},X; STA ${app_globals.WOZ_FP_E:02X},X; DEX; BPL FP_LOG_COPY_X_PLUS_1_TO_E

    ; FP1 has x+1. FP2 has x. FP1 = x-1
    JSR FP_FSUB

    ; Now FP1 has x-1. Load x+1 from E into FP2.
    LDX #$03
FP_LOG_COPY_E_TO_FP2: LDA ${app_globals.WOZ_FP_E:02X},X; STA ${app_globals.WOZ_FP_X2:02X},X; DEX; BPL FP_LOG_COPY_E_TO_FP2

    ; FP1 = (x-1)/(x+1) = z
    JSR FP_FDIV

    ; Now FP1 has z. Calculate series S = z + z^3/3 + z^5/5 ...
    ; And result is 2*S
    ; Store z^2 in E.
    JSR FP_LOG_COPY_FP1_TO_FP2 ; FP2 = z
    JSR FP_FMUL ; FP1 = z*z
    LDX #$03
FP_LOG_COPY_Z2_TO_E: LDA ${app_globals.WOZ_FP_X1:02X},X; STA ${app_globals.WOZ_FP_E:02X},X; DEX; BPL FP_LOG_COPY_Z2_TO_E

    ; Term is in FP1 (z^2). Sum is in FP2 (z).
    ; Loop for n=3,5,7,9,11
    LDY #0 ; Y is index for constant array [3,5,7,9,11]
FP_LOG_SERIES_LOOP:
    ; current term is in FP1. z^2 is in E.
    ; next term = current_term * z^2
    LDX #$03
FP_LOG_COPY_E_TO_FP2_LOOP: LDA ${app_globals.WOZ_FP_E:02X},X; STA ${app_globals.WOZ_FP_X2:02X},X; DEX; BPL FP_LOG_COPY_E_TO_FP2_LOOP
    JSR FP_FMUL ; FP1 = term * z^2

    ; Divide by n. Load n into FP2.
    ; This part is complex. Simplified:
    ; JSR LOAD_CONST_N_FP2
    ; JSR FP_FDIV
    ; JSR ADD_TO_SUM
    INY
    CPY #5
    BNE FP_LOG_SERIES_LOOP

    ; Final result: sum * 2
    ; Sum is in FP2. Load 2.0 into FP1.
    JSR FP_LOG_LOAD_TWO_FP1
    JSR FP_FMUL
    RTS

FP_LOG_LOAD_ONE_FP2:
    LDX #3
FP_LOG_L1_LOOP: LDA FP_CONST_ONE,X; STA ${app_globals.WOZ_FP_X2:02X},X; DEX; BPL FP_LOG_L1_LOOP; RTS
FP_LOG_COPY_FP1_TO_FP2:
    LDX #3
FP_LOG_CP12_LOOP: LDA ${app_globals.WOZ_FP_X1:02X},X; STA ${app_globals.WOZ_FP_X2:02X},X; DEX; BPL FP_LOG_CP12_LOOP; RTS
FP_LOG_LOAD_TWO_FP1:
    LDX #3
FP_LOG_L2_LOOP: LDA FP_CONST_TWO,X; STA ${app_globals.WOZ_FP_X1:02X},X; DEX; BPL FP_LOG_L2_LOOP; RTS
""")

def FP_SQRT():
    """
    Calculates the square root of a floating-point number in FP1.
    Uses the identity: sqrt(x) = exp(0.5 * log(x))
    Result is in FP1.
    """
    return _format_woz_routine(f"""
FP_SQRT
    ; FP1 contains the number to find the square root of.
    ; 1. Calculate log(FP1)
    JSR FP_LOG          ; Result log(x) is in FP1
    ; 2. Load 0.5 into FP2
    JSR load_half_fp2   ; Helper to load the constant 0.5
    ; 3. Multiply log(x) by 0.5
    JSR FP_FMUL         ; FP1 = log(x) * 0.5
    ; 4. Calculate exp(result)
    JSR FP_EXP          ; FP1 = exp(0.5 * log(x))
    RTS

load_half_fp2:
    LDX #3
load_half_loop: LDA FP_CONST_HALF,X; STA ${app_globals.WOZ_FP_X2:02X},X; DEX; BPL load_half_loop; RTS
""")

# add to test
def read_char():
    return f"""
read_char
    ; Routine for reading a single char (simulated)
    ; Actually, it returns a hardcoded character for simplicity
    ; A: character read (simulated)
    LDA #$41  ; Restituisce 'A' come carattere di esempio
    RTS
    """


def read_string():
    return f"""
read_string ;Routine to read a string (simulated)
    ; A: pointer to the memory where the string will be saved (low)
    ; Y: pointer to the memory where the string will be saved (high)
    ; save the read characters until the enter key is pressed in memory
    ; Returns the memory address where the string was saved
    ; init vars
    STX max_len_input   ; init max len from X
    STA input_pointer   ; salva l'indirizzo in input_pointer

read_loop
    JSR read_char
    JSR check_max_len
    JSR read_string_loop
    BNE read_loop
read_end
    RTS
"""


def read_string_loop_routine():
    return f"""
read_string_loop
    ; Loop to save a read character into memory.
    ; A: carattere letto
    ; Uses INPUT_ZP_PTR (${app_globals.INPUT_ZP_PTR:02X}, ${app_globals.INPUT_ZP_PTR+1:02X}) which is set up by the caller (read_string)
    ; from the 'input_pointer' .word variable.
    ; This routine also increments the 'input_pointer' .word variable.
    PHA
    LDY #0
    STA (${app_globals.INPUT_ZP_PTR:02X}),Y ; Store char at ZP pointed address
    PLA

    ; Increment the main 'input_pointer' (word variable)
    INC input_pointer
    BNE rsl_skip_inc_high_${app_globals.label_counter} ; Use a unique label part
    INC input_pointer+1
rsl_skip_inc_high_${app_globals.label_counter}
    ; Also update the ZP pointer to match for the next iteration or read_string_end
    INC ${app_globals.INPUT_ZP_PTR:02X}
    BNE rsl_skip_inc_zp_high_${app_globals.label_counter}
    INC ${app_globals.INPUT_ZP_PTR+1:02X}
rsl_skip_inc_zp_high_${app_globals.label_counter}
    RTS
    """


def check_max_len_routine():
    return f"""
check_max_len ;routine that checks the maximum string length
    ; checks if the string length has reached the maximum length
    ; X : max_len_input (decremented by this routine)
    DEX
    STX max_len_input
    BNE next
    JMP read_string_end
next
    RTS

"""


def read_string_end_routine():
    return f"""
read_string_end ; routine for end read string
    ; end input and null-terminate the string
    ; insert the null terminator character
    ; Assumes INPUT_ZP_PTR ($ {app_globals.INPUT_ZP_PTR:02X}, ${app_globals.INPUT_ZP_PTR+1:02X}) points to the current position in the input buffer.
    ; The actual input_pointer (word variable) should have been updated by read_string_loop.
    LDA #0
    LDY #0
    STA (${app_globals.INPUT_ZP_PTR:02X}),Y ; Store null terminator at the ZP pointed address
    ; Note: input_pointer (the .word variable) should be correctly pointing to the
    ; null terminator's location if read_string_loop updated it.
    ; This routine just writes the null, assuming the ZP pointer is also current.
    ; For consistency, read_string could set up INPUT_ZP_PTR from input_pointer before the loop.
    RTS
"""


def compare_string_const():
    word_type = app_globals.assembly_data_types['word']
    byte_type = app_globals.assembly_data_types['byte']
    zp_ptr1_lsb = f"${app_globals.COMPARE_STR_ZP_PTR1:02X}"
    zp_ptr1_msb = f"${app_globals.COMPARE_STR_ZP_PTR1+1:02X}"
    zp_ptr2_lsb = f"${app_globals.COMPARE_STR_ZP_PTR2:02X}"
    zp_ptr2_msb = f"${app_globals.COMPARE_STR_ZP_PTR2+1:02X}"
    assembly_code = [
        f"compare_string_const",
        f"    ; Compares two strings whose addresses are in ZP pointers:",
        f"    ; String 1: ({zp_ptr1_lsb}), ({zp_ptr1_msb})",
        f"    ; String 2: ({zp_ptr2_lsb}), ({zp_ptr2_msb})",
        f"    ; Result in 'result_compare': 1 if equal, 0 if not.",
        f"    ; Uses Y as an index.",
        "    LDY #0              ; Initialize index Y",
        "compare_loop",
        f"    LDA ({zp_ptr1_lsb}),Y   ; Load char from string 1",
        f"    CMP ({zp_ptr2_lsb}),Y   ; Compare with char from string 2",
        "    BNE strings_not_equal   ; If different, strings are not equal",
        "    ; Characters are equal. Check if it's the null terminator.",
        f"    LDA ({zp_ptr1_lsb}),Y   ; Reload char (A was preserved by CMP if Z flag was set, but BEQ needs A)",
        "    BEQ strings_equal       ; If char is NUL ($00), and they were equal, strings are equal.",
        "    ; Characters are equal but not NUL, continue.",
        "    INY",
        "    JMP compare_loop        ; Continue comparison (assumes strings <256 or Y wrap not an issue for inequality)",
        "strings_not_equal",
        "    LDA #0              ; Set result_compare to 0 (false)",
        "    STA result_compare",
        "    RTS",
        "strings_equal",
        "    LDA #1              ; Set result_compare to 1 (true)",
        "    STA result_compare",
        "    RTS",
    ]
    return "\n".join(assembly_code)


def multiply():
    assembly_code = [
        f"multiply",
        "    ; A: value 1",
        "    ; X: value 2",
        "    ; Load the value in B (0x0000)",
        "    STA multiply_value1",
        "    STX multiply_value2", # Label definition
        "    ; Clear the result var",
        "    LDA #0",
        "    STA multiply_result",
        "    LDY #8",
        "loop_multiply",
        "    LSR multiply_value2",
        "    BCC skip_addition",
        "    LDA multiply_result",
        "    CLC",
        "    ADC multiply_value1",
        "    STA multiply_result",
        "skip_addition",
        "    ASL multiply_value1",
        "    DEY",
        "    BNE loop_multiply",
        "    LDA multiply_result",
        "    RTS",
    ]
    return "\n".join(assembly_code)


def divide():
    assembly_code = [
        f"divide",
        "    ; routine for division",
        "    ; A: dividend ;",
        "    ; X: divisor ;",
        "    ; result is stored in A ;",
        "    ; load the values in the temp var ;",
        "    STA divide_dividend ;load the dividend ;",
        "    STX divide_divisor ; load the divisor",
        "    LDY #8 ; bit count ;",
        "    LDA #0 ; clear the result",
        "    STA divide_result", # Label definition
        "loop_divide",
        "    ASL divide_dividend ;shift the dividend",
        "    ROL divide_result ; shift the result",
        "    ;check if > divisor",
        "    LDA divide_dividend",
        "    SEC",
        "    SBC divide_divisor",
        "    BCC skip_subtraction",
        "    LDA divide_result",
        "    ORA #%00000001",  # Add 1
        "    STA divide_result",
        "    LDA divide_dividend",
        "    SBC divide_divisor",
        "    STA divide_dividend",
        "skip_subtraction",
        "    DEY",
        "    BNE loop_divide",
        "    LDA divide_result",
        "    RTS",
    ]
    return "\n".join(assembly_code)

def multiply16x16_16():
    # Variabili usate (devono essere definite tramite handle_variable in func_expressions.py):
    # m16_arg1_l, m16_arg1_h: input multiplicand (16-bit)
    # m16_arg2_l, m16_arg2_h: input multiplier (16-bit)
    # m16_res_l, m16_res_h: output product (16-bit)
    # Internals:
    # m16_p0_l, m16_p0_h: for LSB(arg1)*LSB(arg2) (16-bit)
    # m16_term2: for LSB(arg1)*MSB(arg2) (8-bit)
    # m16_term3: for MSB(arg1)*LSB(arg2) (8-bit)
    # m16_mul8_val1, m16_mul8_val2: used by _multiply8x8_to_16bit_internal helper
    # multiply_value1, multiply_value2, multiply_result: used by JSR multiply (8x8->8)

    return f"""
multiply16x16_16
    ; Multiplies m16_arg1 by m16_arg2, 16-bit result in m16_res.
    ; Handles overflow by jumping to overflow_error_msg.

    ; --- Local subroutine: _multiply8x8_to_16bit_internal ---
    ; Input: Accumulatore (A) = fattore1, Registro X = fattore2
    ; Output: m16_p0_h (MSB prodotto), m16_p0_l (LSB prodotto)
    ; Usa: m16_mul8_val1, m16_mul8_val2 come temporanei
_m16_mul8_16_start:
    STA m16_mul8_val1   ; Salva fattore1 (Label definition)
    STX m16_mul8_val2   ; Salva fattore2 (Label definition)
    LDA #0
    STA m16_p0_l        ; LSB of partial product (Label definition)
    LDX #8              ; Contatore di bit (Y non usato per evitare conflitti se chiamato da Y) (Label definition)
_m16_mul8_16_loop:
    LSR m16_mul8_val2   ; Bit meno significativo del moltiplicatore in Carry (Label definition)
    BCC _m16_mul8_16_no_add (Label definition)
    LDA m16_p0_l        ; Somma il moltiplicando (m16_mul8_val1) al LSB del prodotto
    CLC
    ADC m16_mul8_val1
    STA m16_p0_l
    LDA m16_p0_h        ; Somma il riporto al MSB del prodotto
    ADC #0
    STA m16_p0_h
_m16_mul8_16_no_add: (Label definition)
    ROR m16_p0_h        ; Scorrimento a destra del prodotto (MSB) (Label definition)
    ROR m16_p0_l        ; Scorrimento a destra del prodotto (LSB) (Label definition)
    DEX (Label definition)
    BNE _m16_mul8_16_loop (Label definition)
    ; Result of 8x8->16bit is in m16_p0_h, m16_p0_l
    ; End of local subroutine

    ; Calculate P0 = LSB(arg1) * LSB(arg2) -> m16_p0_l, m16_p0_h
    LDA m16_arg1_l
    LDX m16_arg2_l
    JSR _m16_mul8_16_start ; Call the local subroutine
    ; m16_p0_l and m16_p0_h contain the result

    LDA m16_p0_l
    STA m16_res_l       ; LSB of final result = LSB(P0)

    ; Save MSB(P0) temporarily for subsequent sums
    LDA m16_p0_h
    STA m16_term2       ; Use m16_term2 for MSB(P0) initially

    ; Calculate term2_val = LSB(arg1) * MSB(arg2) (8-bit result)
    ; Use the 'multiply' routine (8x8 -> 8 bit, input A,X, output A)
    LDA m16_arg1_l
    LDX m16_arg2_h      ; MSB of the second argument
    JSR multiply        ; Result in A (from multiply_result)
    ; Add this to m16_term2 (which contains MSB(P0))
    CLC
    ADC m16_term2
    STA m16_term2       ; m16_term2 ora = MSB(P0) + (LSB(arg1)*MSB(arg2))
    BCS _m16_overflow   ; If there's a carry, overflow of the 16-bit result

    ; Calculate term3_val = MSB(arg1) * LSB(arg2) (8-bit result)
    LDA m16_arg1_h      ; MSB of the first argument
    LDX m16_arg2_l
    JSR multiply        ; Result in A
    ; Add this to m16_term2
    CLC
    ADC m16_term2
    STA m16_res_h       ; Questo è il MSB del risultato finale
    BCS _m16_overflow   ; Se c'è riporto, overflow

    ; Controllo finale: se MSB(arg1) != 0 E MSB(arg2) != 0, allora c'è overflow
    ; perché il termine MSB(arg1)*MSB(arg2) sarebbe >> 16 bit.
    LDA m16_arg1_h
    BEQ _m16_no_final_overflow ; If MSB(arg1) is 0, no overflow from this term
    LDA m16_arg2_h (Label definition)
    BEQ _m16_no_final_overflow ; If MSB(arg2) is 0, no overflow from this term
    ; Se entrambi MSB non sono zero, allora overflow
    JMP _m16_overflow

_m16_no_final_overflow: (Label definition)
    RTS

_m16_overflow:
    JMP overflow_error_msg
"""

def divide16x16_16():
    # Variabili usate (devono essere definite tramite handle_variable in func_expressions.py):
    # d16_orig_dividend_l, d16_orig_dividend_h: input dividendo (16-bit)
    # d16_divisor_l, d16_divisor_h: input divisore (16-bit)
    # d16_quotient_l, d16_quotient_h: output quoziente (16-bit)
    # d16_rem_l, d16_rem_h: accumulatore del resto (16-bit)
    return f"""
divide16x16_16
    ; Divides d16_orig_dividend by d16_divisor. Result in d16_quotient.
    ; Remainder in d16_rem. Handles division by zero.

    ; --- Start Division by Zero Check ---
    LDA d16_divisor_l
    ORA d16_divisor_h
    BNE _d16_div_divisor_ok ; If the divisor is not zero, proceed with division

    ; Divisor is zero. Handle the exception.
    LDA #{app_globals.ErrorCodes.DIVISION_BY_ZERO}
    STA last_exception_type_code        ; Store the error type
    LDA exception_handler_active_flag   ; Check if a try/except handler is active
    CMP #1
    BNE _d16_div_default_error_handler  ; If not active, use the global error handler
    JMP (current_exception_target_label_ptr) ; Otherwise, jump to the except block

_d16_div_default_error_handler:
    JMP division_by_zero_msg            ; Previous behavior: jump to the global error message
    ; --- End Division by Zero Check ---

_d16_div_divisor_ok:
    LDA #0
    STA d16_quotient_l
    STA d16_quotient_h
    STA d16_rem_l       ; Initialize remainder to 0
    STA d16_rem_h

    LDX #16             ; Contatore per 16 bit (Label definition)
_d16_div_loop:
    ; Shift quotient left (Label definition)
    ASL d16_quotient_l
    ROL d16_quotient_h

    ; Shift remainder left and insert the most significant bit of the original dividend
    ASL d16_orig_dividend_l (Label definition)
    ROL d16_orig_dividend_h   ; The MSB of the original dividend goes into Carry
    ROL d16_rem_l             ; The Carry (dividend bit) enters the LSB of the remainder
    ROL d16_rem_h             ; Shift the remainder

    ; Compare Remainder (d16_rem) with Divisor (d16_divisor)
    ; If Remainder >= Divisor: Remainder = Remainder - Divisor; LSB quotient = 1
    SEC
    LDA d16_rem_l (Label definition)
    SBC d16_divisor_l
    TAY                     ; Salva LSB di (Resto - Divisore)
    LDA d16_rem_h
    SBC d16_divisor_h       ; A = MSB di (Resto - Divisore)

    BCC _d16_remainder_less ; If Carry is 0 (borrow), Remainder < Divisor (Label definition)

    ; If Carry is 1, Remainder >= Divisor. Subtraction is valid.
    STA d16_rem_h           ; Store MSB of the new remainder
    STY d16_rem_l           ; Store LSB of the new remainder
    INC d16_quotient_l      ; Imposta il bit corrente del quoziente a 1

_d16_remainder_less: (Label definition)
    DEX (Label definition)
    BNE _d16_div_loop (Label definition)
    RTS (Label definition)
"""

def end_program():
    assembly_code = [
        f"end_program",
        "    RTS"
    ]
    return "\n".join(assembly_code)


def key_error_msg():
    assembly_code = [
        f"key_error_msg",
        "    LDA #<key_error_msg_string",
        "    STA temp_0",
        "    LDA #>key_error_msg_string",
        "    STA temp_0+1",
        "    JMP print_string",
    ]
    return "\n".join(assembly_code)

def attribute_error_msg():
    assembly_code = [
        f"attribute_error_msg",
        "    LDA #<attribute_error_msg_string",
        "    STA temp_0",
        "    LDA #>attribute_error_msg_string",
        "    STA temp_0+1",
        "    JMP print_string",
    ]
    return "\n".join(assembly_code)

def not_implemented_error_msg():
    assembly_code = [
        f"not_implemented_error_msg",
        "    LDA #<not_implemented_error_msg_string",
        "    STA temp_0",
        "    LDA #>not_implemented_error_msg_string",
        "    STA temp_0+1",
        "    JMP print_string",
    ]
    return "\n".join(assembly_code)

def value_error_msg(): # New routine for ValueError
    assembly_code = [
        f"value_error_msg",
        "    LDA #<value_error_msg_string",
        "    STA temp_0",
        "    LDA #>value_error_msg_string",
        "    STA temp_0+1",
        "    JMP print_string",
    ]
    return "\n".join(assembly_code)






def ascii_to_petscii():
    """
    Converts an ASCII character in accumulator A to its PETSCII equivalent.
    This version converts lowercase ASCII a-z to uppercase PETSCII A-Z.
    Other characters are passed through (this might need more refinement for full PETSCII).
    """
    return f"""
ascii_to_petscii
    ; Input: A contains ASCII character
    ; Output: A contains PETSCII character (lowercase ASCII converted to uppercase PETSCII)
    CMP #'a'
    BCC no_conversion_needed_petscii
    CMP #'z'+1
    BCS no_conversion_needed_petscii
    SEC             ; Ensure Carry is set for SBC
    SBC #$20        ; Convert ASCII 'a'-'z' to PETSCII 'A'-'Z' (e.g. ASCII 'a' (97) - 32 = PETSCII 'A' (65))
no_conversion_needed_petscii
    RTS
"""

def global_unhandled_exception_routine():
    """
    Handles exceptions not caught by any try/except block.
    Prints a generic message and terminates.
    """
    # Ensure 'unhandled_exc_msg_string' is defined in data_definitions
    # when this routine is used.
    app_globals.data_definitions.append(f"unhandled_exc_msg_string {app_globals.assembly_data_types['asciiz']} \"Unhandled error!\"")

    return f"""
global_unhandled_exception_routine
    LDA #<unhandled_exc_msg_string
    STA temp_0
    LDA #>unhandled_exc_msg_string
    STA temp_0+1
    JSR print_string
    JMP end_program
"""

# Dizionario delle dipendenze tra routine
# Dictionary of dependencies between routines
routine_dependencies = {
    'check_overflow': {'overflow_error_msg', 'end_program'}, # end_program se check_overflow fa JMP end_program
    'overflow_error_msg': {'print_string'},
    'division_by_zero_msg': {'print_string'},
    'key_error_msg': {'print_string'},
    'attribute_error_msg': {'print_string'}, # New
    'not_implemented_error_msg': {'print_string'}, # New
    'value_error_msg': {'print_string'}, # New
    'generic_error_msg': {'print_string'},
        'print_string': {'print_char'},
    'error_handler': {'print_error_message', 'end_program'},
    'print_error_message': { # Depends on which errors it handles
        'overflow_error_msg',
        'division_by_zero_msg',
        'key_error_msg',
        'attribute_error_msg', # New
        'not_implemented_error_msg', # New
        'value_error_msg', # New
        'generic_error_msg',
    },
    'check_division_by_zero': {'error_handler', 'division_by_zero_msg'}, # se chiama error_handler
    'read_string': {'read_char', 'check_max_len', 'read_string_loop', 'read_string_end'},
    'multiply16x16_16': {'multiply', 'overflow_error_msg'}, # Depends on 8x8->8 multiply and its own error handling
    'divide16x16_16': {'division_by_zero_msg'}, # Handles its own div by zero
    # Wozniak/Apple II FP Dependencies
    'FP_FADD': {'FP_ALGNSWP', 'FP_ADD_MANT', 'FP_NORM', 'FP_RTLOG', 'FP_OVFL_HANDLER'},
    'FP_FSUB': {'FP_SWAP', 'FP_FCOMPL', 'FP_FADD'},
    'FP_FMUL': {'FP_MD1', 'FP_MD2', 'FP_RTLOG1', 'FP_ADD_MANT', 'FP_NORM', 'FP_FCOMPL', 'FP_OVFL_HANDLER'},
    'FP_FDIV': {'FP_SWAP', 'FP_MD1', 'FP_MD2', 'FP_NORM', 'FP_FCOMPL', 'FP_OVFL_HANDLER'},
    'FP_LOG': {'FP_FADD', 'FP_FSUB', 'FP_FMUL', 'FP_FDIV', 'error_handler'},
    'FP_EXP': {'FP_FMUL', 'FP_FSUB', 'FP_FIX', 'FP_SWAP'},
    'FP_ABS': {'FP_FCOMPL'}, # New dependency
    'FP_SQRT': {'FP_LOG', 'FP_EXP', 'FP_FMUL'}, # New dependency
    'FP_COMPARE': {'FP_FSUB'}, # New dependency
    'FP_FLOAT': {'FP_NORM1', 'FP_NORM'},
    'FP_FIX': {'FP_RTAR', 'FP_OVFL_HANDLER'}, # RTAR calls RTLOG (which checks OVFL)
    'FP_EXP': {}, # Stub implementation dependency (now just returns 1.0)
    'FP_FCOMPL': {'FP_NORM', 'FP_RTLOG', 'FP_OVFL_HANDLER'}, # Jumps to FADD's ADDEND which can lead to NORM/RTLOG
    'FP_NORM': {'FP_NORM1'},
    'FP_NORM1': {}, # Self-contained loop or exits
    # Internal FP helper dependencies
    'FP_MD1': {'FP_ABSWAP'},
    'FP_ABSWAP': {'FP_FCOMPL', 'FP_SWAP'},
    'FP_ALGNSWP': {'FP_SWAP', 'FP_RTAR', 'FP_ADD_MANT', 'FP_OVFL_HANDLER'}, # Complex flow, can lead to ADD or RTAR
    'FP_RTAR': {'FP_RTLOG', 'FP_OVFL_HANDLER'}, # RTAR falls into RTLOG
    'FP_RTLOG': {'FP_RTLOG1', 'FP_OVFL_HANDLER'}, # RTLOG calls RTLOG1
    'FP_RTLOG1': {},
    'FP_MD2': {'FP_OVFL_HANDLER'}, # Checks for overflow/underflow
    'FP_OVFL_HANDLER': {'error_handler', 'overflow_error_msg'}, # Our handler for FP OVFL
    # 'print_char': {'ascii_to_petscii', 'screen_pointer'}, # screen_pointer is no longer a direct dependency
    'global_unhandled_exception_routine': {'print_string', 'end_program'},
    # Aggiungere altre dipendenze se necessario
        'print_char': {'ascii_to_petscii'}, # Ora dipende da ascii_to_petscii e implicitamente da chrout
    # C64 GFX dependencies are now handled by the main dependency resolver,
    # as the library functions add their own requirements to used_routines.
}


# Function to retrieve a routine by its name
def get_routine_by_name(routine_name):
    # First, check the local map for core routines
    if routine_name in routines_map:
        return routines_map[routine_name]()
    # If not found, try to get it from the C64 library
    c64_code = c64_routine_library.get_routine_code(routine_name)
    if c64_code:
        return c64_code

    # If still not found, warn the user
    print(f"Warning: Routine '{routine_name}' not found in any library.")
    return ""

def print_error_message():
    assembly_code = [
        f"print_error_message",
        f"    CMP #{app_globals.ErrorCodes.OVERFLOW}",
        "    BNE pem_check_div_zero",
        "    JMP overflow_error_msg",
        "pem_check_div_zero:",
        f"    CMP #{app_globals.ErrorCodes.DIVISION_BY_ZERO}",
        "    BNE pem_check_key_not_found",
        "    JMP division_by_zero_msg",
        "pem_check_key_not_found:", # Label definition
        f"    CMP #{app_globals.ErrorCodes.KEY_NOT_FOUND}",
        "    BNE pem_check_value_error",
        "    JMP key_error_msg",
        "pem_check_value_error:", # Label definition for ValueError
        f"    CMP #{app_globals.ErrorCodes.VALUE_ERROR}",
        "    BNE pem_check_type_error",
        "    JMP value_error_msg",   # Jump to specific ValueError message routine
        "pem_check_type_error:", # Label definition
        f"    CMP #{app_globals.ErrorCodes.TYPE_ERROR}",
        "    BNE pem_check_index_error",
        "    JMP generic_error_msg", # TODO: Create type_error_msg() and string
        "pem_check_index_error:", # Label definition
        f"    CMP #{app_globals.ErrorCodes.INDEX_ERROR}",
        "    BNE pem_check_name_error",
        "    JMP generic_error_msg", # TODO: Create index_error_msg() and string
        "pem_check_name_error:", # Label definition
        f"    CMP #{app_globals.ErrorCodes.NAME_ERROR}",
        "    BNE pem_check_assertion_error",
        "    JMP generic_error_msg", # TODO: Create name_error_msg() and string
        "pem_check_assertion_error:", # Label definition
        f"    CMP #{app_globals.ErrorCodes.ASSERTION_ERROR}",
        "    BNE pem_check_attribute_error",
        "    JMP generic_error_msg", # TODO: Create assertion_error_msg() and string
        "pem_check_attribute_error:", # New
        f"    CMP #{app_globals.ErrorCodes.ATTRIBUTE_ERROR}",
        "    BNE pem_check_not_implemented_error",
        "    JMP attribute_error_msg",
        "pem_check_not_implemented_error:", # Nuovo
        f"    CMP #{app_globals.ErrorCodes.NOT_IMPLEMENTED_ERROR}",
        "    BNE pem_check_generic_runtime",
        "    JMP not_implemented_error_msg",
        "pem_check_generic_runtime:", # Label definition
        f"    CMP #{app_globals.ErrorCodes.GENERIC_RUNTIME_ERROR_CODE}", # Controlla GENERIC_RUNTIME_ERROR_CODE
        "    BNE pem_end_error_message",
        "    JMP generic_error_msg",
        "pem_end_error_message:", # Label definition
        "    RTS"
    ]
    return "\n".join(assembly_code)

def get_all_required_routines(initial_routines_set):
    all_routines = set(initial_routines_set)
    queue = list(initial_routines_set)

    idx = 0
    while idx < len(queue):
        routine_name = queue[idx]
        idx += 1

        if routine_name in routine_dependencies:
            for dep in routine_dependencies[routine_name]:
                if dep not in all_routines:
                    all_routines.add(dep)
                    queue.append(dep)
    return all_routines
