;--------- Start python code ---------
; glob_var = 50
; def modify_global():
;   global glob_var
;   glob_var = 100
; modify_global()
; # Expected: glob_var = 100

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
glob_var * = * + 2
__modify_global_glob_var * = * + 2
exception_handler_active_flag * = * + 2
current_exception_target_label_ptr * = * + 2
last_exception_type_code * = * + 1

main_program_entry_point:
; --- Code Section ---
    LDA #<02FF
    STA $E0
    LDA #>02FF
    STA $E1
    LDA #50
    STA glob_var
    LDA #0
    STA glob_var+1
    LDA #100
    STA __modify_global_glob_var
    LDA #0
    STA __modify_global_glob_var+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
