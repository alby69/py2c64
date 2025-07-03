;--------- Start python code ---------
; def set_val_to_zero():
;   return
; x = 5
; x = set_val_to_zero()
; # Expected: x = 0

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
x * = * + 2
exception_handler_active_flag * = * + 2
current_exception_target_label_ptr * = * + 2
last_exception_type_code * = * + 1

main_program_entry_point:
; --- Code Section ---
    LDA #<02FF
    STA $E0
    LDA #>02FF
    STA $E1

func_set_val_to_zero_0:
    ; --- Function Prologue for set_val_to_zero ---
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

func_ret_set_val_to_zero_0:
    ; --- Function Epilogue for set_val_to_zero ---
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
    LDA #5
    STA x
    LDA #0
    STA x+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
