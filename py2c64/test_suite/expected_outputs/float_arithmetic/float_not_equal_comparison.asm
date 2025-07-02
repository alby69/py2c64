;--------- Start python code ---------
; 
; p_float = 10.0
; q_float = 10.000001
; is_not_equal = p_float != q_float

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
p_float * = * + 2
q_float * = * + 2
is_not_equal * = * + 2
exception_handler_active_flag * = * + 2
current_exception_target_label_ptr * = * + 2
last_exception_type_code * = * + 1

main_program_entry_point:
; --- Code Section ---
    LDA #<02FF
    STA $E0
    LDA #>02FF
    STA $E1
    LDA #$00
    STA p_float+0
    LDA #$00
    STA p_float+1
    LDA #$00
    STA p_float+2
    LDA #$00
    STA p_float+3
    LDA #$00
    STA q_float+0
    LDA #$00
    STA q_float+1
    LDA #$00
    STA q_float+2
    LDA #$00
    STA q_float+3
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
