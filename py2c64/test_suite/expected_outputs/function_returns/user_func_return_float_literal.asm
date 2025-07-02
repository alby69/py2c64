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

func_get_pi_0:
    ; --- Function Prologue for get_pi ---
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
    LDA #$5C
    STA temp_0+0
    LDA #$8F
    STA temp_0+1
    LDA #$64
    STA temp_0+2
    LDA #$82
    STA temp_0+3
    LDA temp_0+3
    STA $F8
    LDA temp_0+0
    STA $F9
    LDA temp_0+1
    STA $FA
    LDA temp_0+2
    STA $FB

func_ret_get_pi_0:
    ; --- Function Epilogue for get_pi ---
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
    JSR func_get_pi_0
    LDA $F8
    STA a+3
    LDA $F9
    STA a+0
    LDA $FA
    STA a+1
    LDA $FB
    STA a+2
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
