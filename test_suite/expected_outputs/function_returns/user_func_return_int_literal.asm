;--------- Start python code ---------
; 
; def get_int():
;     return 100
; 
; c = get_int()
; # 'c' should be treated as an int (2 bytes copied)

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
c * = * + 2
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

func_get_int_0:
    ; --- Function Prologue for get_int ---
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
    LDA #100
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0+1
    LDX temp_0

func_ret_get_int_0:
    ; --- Function Epilogue for get_int ---
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
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
