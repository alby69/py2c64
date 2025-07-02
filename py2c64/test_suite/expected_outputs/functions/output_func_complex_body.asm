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

func_check_sign_0:
    ; --- Function Prologue for check_sign ---
    LDA #<00E2
    STA $F2
    LDA #>00E2
    STA $F3
    JSR push_word_from_addr
    LDA $E0
    STA $E2
    LDA $E1
    STA $E3
    ; --- End Function Prologue ---
    LDA temp_0+1
    LDX temp_0
    ORA X
    BEQ if_else_1
    LDA #1
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0+1
    LDX temp_0
    JMP func_ret_check_sign_0
    JMP if_end_1
if_else_1:
    LDA temp_0+1
    LDX temp_0
    ORA X
    BEQ if_else_2
    LDA temp_0+1
    LDX temp_0
    JMP func_ret_check_sign_0
    JMP if_end_2
if_else_2:
if_end_2:
if_end_1:

func_ret_check_sign_0:
    ; --- Function Epilogue for check_sign ---
    LDA $E2
    STA $E0
    LDA $E3
    STA $E1
    LDA #<00E2
    STA $F2
    LDA #>00E2
    STA $F3
    JSR pop_word_to_addr
    RTS
    ; --- End Function Epilogue ---
    LDA #10
    STA __func_arg_0
    LDA #0
    STA __func_arg_0+1
    JSR func_check_sign_0
    STX res_pos
    STA res_pos+1
    JSR func_check_sign_0
    STX res_neg
    STA res_neg+1
    LDA #0
    STA __func_arg_0
    LDA #0
    STA __func_arg_0+1
    JSR func_check_sign_0
    STX res_zero
    STA res_zero+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
