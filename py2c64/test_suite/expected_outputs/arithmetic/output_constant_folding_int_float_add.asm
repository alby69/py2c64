;--------- Start python code ---------
; z = 5 + 3.14

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
z * = * + 2
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
    STA z+0
    LDA #$00
    STA z+1
    LDA #$00
    STA z+2
    LDA #$00
    STA z+3
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
