;--------- Start python code ---------
; t = (1, 2, 3)

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
t * = * + 2
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
    STA t
    LDA #0
    STA t+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
