;--------- Start python code ---------
; my_dict = {}
; my_dict['c'] = 3
; del my_dict['d']

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
my_dict * = * + 2
my_dict_key_0_str * = * + 2
my_dict_key_0 * = * + 2
exception_handler_active_flag * = * + 2
current_exception_target_label_ptr * = * + 2
last_exception_type_code * = * + 1

main_program_entry_point:
; --- Code Section ---
    LDA #<02FF
    STA $E0
    LDA #>02FF
    STA $E1
    LDA #<my_dict_key_0_str
    STA my_dict_key_0
    LDA #>my_dict_key_0_str
    STA my_dict_key_0+1
    LDA #'c'
    STA $C390
    LDA #0
    STA $C391
    LDA #3
    STA $C38E
; Placeholder per Delete
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
