;--------- Start python code ---------
; my_dict = {'a': 1, 'b': 2}
; x1 = my_dict['a']

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
my_dict * = * + 2
x1 * = * + 2
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
    STA my_dict
    LDA #0
    STA my_dict+1
    LDA #0
    STA x1
    LDA #0
    STA x1+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
