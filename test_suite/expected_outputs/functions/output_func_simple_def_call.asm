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

func_my_func_0:
    ; --- Function Prologue for my_func ---
    LDA #<00E2
    STA $F2
    LDA #>00E2
    STA $F3
    JSR push_word_from_addr
    LDA $E0
    STA $E2
    LDA $E1
    STA $E3
    ; Allocate 2 bytes for local variables
    SEC
    LDA $E0
    SBC #2
    STA $E0
    LDA $E1
    SBC #0
    STA $E1
    ; --- End Function Prologue ---
    LDA #10
    STA __my_func_res
    LDA #0
    STA __my_func_res+1

func_ret_my_func_0:
    ; --- Function Epilogue for my_func ---
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
    ; --- Preparazione chiamata a my_func ---
    JSR func_my_func_0
    ; --- Fine chiamata a my_func (valore di ritorno in A/X scartato) ---
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
