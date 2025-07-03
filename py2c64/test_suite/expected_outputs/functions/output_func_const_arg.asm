;--------- Start python code ---------
; def identity(n):
;   return n
; result = identity(100)
; # Expected: result = 100

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
result * = * + 2
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

func_identity_0:
    ; --- Function Prologue for identity ---
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
    LDA __identity_n+0
    STA temp_0+0
    LDA __identity_n+1
    STA temp_0+1
    LDA temp_0+1
    LDX temp_0

func_ret_identity_0:
    ; --- Function Epilogue for identity ---
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
    LDA #100
    STA __func_arg_0
    LDA #0
    STA __func_arg_0+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
