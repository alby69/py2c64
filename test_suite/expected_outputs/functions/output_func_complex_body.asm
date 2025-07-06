;--------- Start python code ---------
; def check_sign(num):
;   if num > 0:
;     return 1
;   elif num < 0:
;     return -1
;   else:
;     return 0
; res_pos = check_sign(10)
; res_neg = check_sign(-5)
; res_zero = check_sign(0)
; # Expected: res_pos = 1, res_neg = -1, res_zero = 0

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
res_pos * = * + 2
res_neg * = * + 2
res_zero * = * + 2
temp_0 * = * + 4
__func_arg_0 * = * + 2
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
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #1
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #0
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #0
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #10
    STA __func_arg_0
    LDA #0
    STA __func_arg_0+1
    LDA #0
    STA __func_arg_0
    LDA #0
    STA __func_arg_0+1
    LDA #0
    STA __func_arg_0
    LDA #0
    STA __func_arg_0+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
