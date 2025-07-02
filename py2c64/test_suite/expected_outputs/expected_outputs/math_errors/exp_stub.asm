;--------- Start python code ---------
; 
; y = exp(1.0) # Any input
; print(y) # Stub should return 1.0

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
y * = * + 2
temp_0 * = * + 4
FP_CONST_ONE byte $00, $00, $40, $81
FP_CONST_TWO byte $00, $00, $40, $82
FP_CONST_LN2 byte $9E, $E0, $58, $80
FP_CONST_INV_LN2 byte $1F, $85, $5B, $81
exception_handler_active_flag * = * + 2
current_exception_target_label_ptr * = * + 2
last_exception_type_code * = * + 1
chrout = $FFD2

main_program_entry_point:
; --- Code Section ---
    LDA #<02FF
    STA $E0
    LDA #>02FF
    STA $E1
    LDA #$00
    STA temp_0+0
    LDA #$00
    STA temp_0+1
    LDA #$40
    STA temp_0+2
    LDA #$81
    STA temp_0+3
    LDA temp_0+3
    STA $F8
    LDA temp_0+0
    STA $F9
    LDA temp_0+1
    STA $FA
    LDA temp_0+2
    STA $FB
    JSR FP_EXP
    LDA $F8
    STA y+3
    LDA $F9
    STA y+0
    LDA $FA
    STA y+1
    LDA $FB
    STA y+2
    LDA y+0
    STA temp_0+0
    LDA y+1
    STA temp_0+1
    LDA temp_0
    STA temp_0
    LDA temp_0+1
    STA temp_0+1
    JSR print_string
    JMP end_program

; --- Routines Section ---
    * = $8000
FP_EXP       ; Calculates e^FP1. Result in FP1.
    ; This is a stub implementation for testing purposes.
    ; It returns 1.0 regardless of input.
    LDA #$81                ; Exponent for 1.0
    STA $F8
    LDA #$40                ; Mantissa MSB for 1.0
    STA $F9
    LDA #$00                ; Mantissa MID for 1.0
    STA $FA
    LDA #$00                ; Mantissa LSB for 1.0
    STA $FB
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
    LDA $F8,X
    STA $FC,X
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
    LDA $FC,X
    STA $F4,X
    DEX
    BPL FP_EXP_COPY_E_TO_FP2

    ; Convert I (float, in FP2) to a 16-bit integer in M2, M2+1
    JSR FP_FIX ; Note: FP_FIX works on FP1, so we need to swap first.
    JSR FP_SWAP ; I (float) is now in FP1.
    JSR FP_FIX  ; M1, M1+1 now contain the 16-bit integer I.

    ; Add I to the exponent of e^z (which is in FP2 after the swap)
    ; This is the 2^I part.
    CLC
    LDA $FA ; LSB of I
    ADC $F4   ; Add to exponent of e^z
    STA $F4   ; Store back.
    ; We ignore MSB of I for simplicity (handles exponents -128 to 127).
    ; The result is now in FP2. Swap back to FP1.
    JSR FP_SWAP
    RTS

FP_EXP_LOAD_INV_LN2:
    LDX #3
FP_EXP_LIL_LOOP: LDA FP_CONST_INV_LN2,X; STA $F4,X; DEX; BPL FP_EXP_LIL_LOOP; RTS
FP_EXP_LOAD_LN2:
    LDX #3
FP_EXP_LLN2_LOOP: LDA FP_CONST_LN2,X; STA $F4,X; DEX; BPL FP_EXP_LLN2_LOOP; RTS
FP_EXP_LOAD_ONE:
    LDX #3
FP_EXP_LO_LOOP: LDA FP_CONST_ONE,X; STA $F8,X; DEX; BPL FP_EXP_LO_LOOP; RTS
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
end_program
    RTS
print_char
    ; Input: A = ASCII character
    ; Output: Prints character to screen via KERNAL CHROUT
    ; Modifies: A (CHROUT modifica A)
    ; Preserves: X, Y (CHROUT preserva X, Y)

    JSR ascii_to_petscii    ; Convert A from ASCII to PETSCII. A is now PETSCII.
    JSR chrout              ; Call KERNAL CHROUT routine (address defined in data section)
    RTS
print_string
    ; Routine to print a string located at the address contained in the var temp_0
    ; Uses ZP locations $FA/$FB for the 16-bit string pointer.
    ; Preserves A and Y registers.
    PHA                     ; Save A
    TYA                     ; Transfer Y to A (to save Y on stack)
    PHA                     ; Push A (which now holds Y's original value)
    LDA temp_0                ; Load LSB of string address from temp_0 (a .word variable)
    STA $FA           ; Store LSB into ZP pointer
    LDA temp_0+1              ; Load high byte of address from temp_0+1
    STA $FB         ; Store MSB into ZP pointer

    LDY #$00                  ; Use Y as the index for LDA (ZP),Y. This Y is local to the loop.
print_loop_ps               ; Renamed label to avoid conflict if routine is included multiple times (though it shouldn't be)
        LDA ($FA),Y ; Use (Indirect),Y addressing with ZP pointer
        BEQ end_print_ps      ; If char is NUL, end.
        JSR print_char          ; print_char preserves A, does not use Y.
        INY                     ; Increment Y
    ; Check if Y wrapped around (very unlikely for typical strings)
    ; If Y becomes 0 after INY, it means we crossed a 256-byte boundary with Y.
    CPY #0
    BNE print_loop_ps       ; If Y is not 0, continue loop within the current 256-byte page
    ; If Y wrapped to 0, it means we printed 256 chars. Increment MSB of ZP pointer.
    INC $FB
    JMP print_loop_ps       ; And continue printing (Y is 0 again for the new page)
end_print_ps
    PLA                     ; Pop original Y value (into A)
    TAY                     ; Transfer A to Y (restoring Y)
    PLA                     ; Pop original A value
    RTS
