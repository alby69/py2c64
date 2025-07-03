;--------- Start python code ---------
; a = -5.25
; abs_a = abs(a)  # Expected: 5.25
; b = 0.0
; sgn_a = sgn(a)    # Expected: -1.0
; sgn_b = sgn(b)    # Expected: 0.0
; sgn_c = sgn(10.0) # Expected: 1.0
; d = 2.0 # Placeholder for log, as FP_LOG is a stub
; log_d = log(d)
; log_int = log(1) # Test coercion

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
a * = * + 2
abs_a * = * + 2
b * = * + 2
sgn_a * = * + 2
sgn_b * = * + 2
sgn_c * = * + 2
d * = * + 2
log_d * = * + 2
log_int * = * + 2
temp_0 * = * + 4
exception_handler_active_flag * = * + 2
current_exception_target_label_ptr * = * + 2
last_exception_type_code * = * + 1

main_program_entry_point:
; --- Code Section ---
    LDA #<02FF
    STA $E0
    LDA #>02FF
    STA $E1
    LDA #0
    STA a
    LDA #0
    STA a+1
    LDA a+0
    STA temp_0+0
    LDA a+1
    STA temp_0+1
    LDA #$00
    STA b+0
    LDA #$00
    STA b+1
    LDA #$00
    STA b+2
    LDA #$00
    STA b+3
    LDA #0
    STA sgn_a
    LDA #0
    STA sgn_a+1
    LDA #0
    STA sgn_b
    LDA #0
    STA sgn_b+1
    LDA #0
    STA sgn_c
    LDA #0
    STA sgn_c+1
    LDA #$00
    STA d+0
    LDA #$00
    STA d+1
    LDA #$40
    STA d+2
    LDA #$82
    STA d+3
    LDA #0
    STA log_d
    LDA #0
    STA log_d+1
    LDA #0
    STA log_int
    LDA #0
    STA log_int+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
