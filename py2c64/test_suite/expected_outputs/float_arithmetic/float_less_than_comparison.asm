;--------- Start python code ---------
; 
; a_float = 3.14
; b_float = 2.71
; result = a_float < b_float

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
a_float * = * + 2
b_float * = * + 2
result * = * + 2
exception_handler_active_flag * = * + 2
current_exception_target_label_ptr * = * + 2
last_exception_type_code * = * + 1

main_program_entry_point:
; --- Code Section ---
    LDA #<02FF
    STA $E0
    LDA #>02FF
    STA $E1
    LDA #$5C
    STA a_float+0
    LDA #$8F
    STA a_float+1
    LDA #$64
    STA a_float+2
    LDA #$82
    STA a_float+3
    LDA #$00
    STA b_float+0
    LDA #$00
    STA b_float+1
    LDA #$00
    STA b_float+2
    LDA #$00
    STA b_float+3
    LDA #0
    STA result
    LDA #0
    STA result+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
