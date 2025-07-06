;--------- Start python code ---------
; res = 0
; def my_func():
;   global res
;   res = 10
; my_func()
; # Expected: res = 10

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
res * = * + 2
__my_func_res * = * + 2
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
    STA res
    LDA #0
    STA res+1
    LDA #10
    STA __my_func_res
    LDA #0
    STA __my_func_res+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
