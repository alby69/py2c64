;--------- Start python code ---------
; x1 = "world"
; s = f"hello {x1}"

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
x1 * = * + 2
s * = * + 2
str_lit_0 text "world"
exception_handler_active_flag * = * + 2
current_exception_target_label_ptr * = * + 2
last_exception_type_code * = * + 1

main_program_entry_point:
; --- Code Section ---
    LDA #<02FF
    STA $E0
    LDA #>02FF
    STA $E1
    LDA #<str_lit_0
    STA x1
    LDA #>str_lit_0
    STA x1+1
    LDA #0
    STA s
    LDA #0
    STA s+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
