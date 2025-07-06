;--------- Start python code ---------
; 
; def get_pi():
;     return 3.14
; 
; a = get_pi()
; # 'a' should be treated as a float (4 bytes copied from __func_retval)

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
a * = * + 2
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
    LDA #$5C
    STA temp_0+0
    LDA #$8F
    STA temp_0+1
    LDA #$64
    STA temp_0+2
    LDA #$82
    STA temp_0+3
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
