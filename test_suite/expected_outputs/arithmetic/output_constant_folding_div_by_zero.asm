;--------- Start python code ---------
; y = 10 // 0

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
y * = * + 2
temp_0 * = * + 2
temp_1 * = * + 4
d16_orig_dividend_l * = * + 2
d16_orig_dividend_h * = * + 2
d16_divisor_l * = * + 2
d16_divisor_h * = * + 2
d16_quotient_l * = * + 2
d16_quotient_h * = * + 2
d16_rem_l * = * + 2
d16_rem_h * = * + 2
exception_handler_active_flag * = * + 2
current_exception_target_label_ptr * = * + 2
last_exception_type_code * = * + 1
division_by_zero_msg_string text "Error: Division by zero!"
chrout = $FFD2

main_program_entry_point:
; --- Code Section ---
    LDA #<02FF
    STA $E0
    LDA #>02FF
    STA $E1
    LDA #10
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #0
    STA temp_1
    LDA #0
    STA temp_1+1
    JMP end_program

; --- Routines Section ---
    * = $8000
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
divide16x16_16
    ; Divides d16_orig_dividend by d16_divisor. Result in d16_quotient.
    ; Remainder in d16_rem. Handles division by zero.

    ; --- Start Division by Zero Check ---
    LDA d16_divisor_l
    ORA d16_divisor_h
    BNE _d16_div_divisor_ok ; If the divisor is not zero, proceed with division

    ; Divisor is zero. Handle the exception.
    LDA #2
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
division_by_zero_msg
    LDA #<division_by_zero_msg_string
    STA temp_0
    LDA #>division_by_zero_msg_string
    STA temp_0+1
    JMP print_string
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
