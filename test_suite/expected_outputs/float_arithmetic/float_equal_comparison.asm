;--------- Start python code ---------
; 
; x_float = 1.5
; y_float = 1.5
; is_equal = x_float == y_float

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
x_float * = * + 2
y_float * = * + 2
is_equal * = * + 2
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
    STA x_float+0
    LDA #$00
    STA x_float+1
    LDA #$60
    STA x_float+2
    LDA #$81
    STA x_float+3
    LDA #$00
    STA y_float+0
    LDA #$00
    STA y_float+1
    LDA #$60
    STA y_float+2
    LDA #$81
    STA y_float+3
    LDA #0
    STA is_equal
    LDA #0
    STA is_equal+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
