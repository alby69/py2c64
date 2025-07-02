;--------- Start python code ---------
; a1 = 5
; b = 3
; c = a1 * b + (a1 - b) // 2

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
a1 * = * + 2
b * = * + 2
c * = * + 2
temp_0 * = * + 2
m16_arg1_l * = * + 2
m16_arg1_h * = * + 2
m16_arg2_l * = * + 2
m16_arg2_h * = * + 2
m16_res_l * = * + 2
m16_res_h * = * + 2
m16_p0_l * = * + 2
m16_p0_h * = * + 2
m16_term2 * = * + 2
m16_term3 * = * + 2
m16_mul8_val1 * = * + 2
m16_mul8_val2 * = * + 2
temp_1 * = * + 4
temp_2 * = * + 4
temp_3 * = * + 4
d16_orig_dividend_l * = * + 2
d16_orig_dividend_h * = * + 2
d16_divisor_l * = * + 2
d16_divisor_h * = * + 2
d16_quotient_l * = * + 2
d16_quotient_h * = * + 2
d16_rem_l * = * + 2
d16_rem_h * = * + 2
multiply_value1 * = * + 1
multiply_value2 * = * + 1
multiply_result * = * + 1
exception_handler_active_flag * = * + 2
current_exception_target_label_ptr * = * + 2
last_exception_type_code * = * + 1
overflow_msg text "Error: Arithmetic overflow!"
division_by_zero_msg_string text "Error: Division by zero!"
chrout = $FFD2

main_program_entry_point:
; --- Code Section ---
    LDA #<02FF
    STA $E0
    LDA #>02FF
    STA $E1
    LDA #5
    STA a1
    LDA #0
    STA a1+1
    LDA #3
    STA b
    LDA #0
    STA b+1
    LDA a1
    STA m16_arg1_l
    LDA a1+1
    STA m16_arg1_h
    LDA b
    STA m16_arg2_l
    LDA b+1
    STA m16_arg2_h
    JSR multiply16x16_16
    LDA m16_res_l
    STA temp_0
    LDA m16_res_h
    STA temp_0+1
    LDA a1
    SEC
    SBC b
    STA temp_2
    LDA a1+1
    SBC b+1
    JSR check_overflow
    STA temp_2+1
    LDA #2
    STA temp_3
    LDA #0
    STA temp_3+1
    LDA temp_2
    STA d16_orig_dividend_l
    LDA temp_2+1
    STA d16_orig_dividend_h
    LDA temp_3
    STA d16_divisor_l
    LDA temp_3+1
    STA d16_divisor_h
    JSR divide16x16_16
    LDA d16_quotient_l
    STA temp_1
    LDA d16_quotient_h
    STA temp_1+1
    LDA temp_0
    CLC
    ADC temp_1
    STA c
    LDA temp_0+1
    ADC temp_1+1
    JSR check_overflow
    STA c+1
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
check_overflow
    ; Check the overflow flag (V)
    BVC no_overflow  ; Branch if Overflow Clear (no overflow)

    ; If we are here, there is an overflow
    JSR overflow_error_msg
    JMP end_program

no_overflow
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
multiply
    ; A: value 1
    ; X: value 2
    ; Load the value in B (0x0000)
    STA multiply_value1
    STX multiply_value2
    ; Clear the result var
    LDA #0
    STA multiply_result
    LDY #8
loop_multiply
    LSR multiply_value2
    BCC skip_addition
    LDA multiply_result
    CLC
    ADC multiply_value1
    STA multiply_result
skip_addition
    ASL multiply_value1
    DEY
    BNE loop_multiply
    LDA multiply_result
    RTS
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
overflow_error_msg
    LDA #<overflow_msg
    STA temp_0
    LDA #>overflow_msg
    STA temp_0+1
    JMP print_string
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
