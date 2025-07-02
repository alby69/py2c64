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

func_modify_global_0:
    ; --- Function Prologue for modify_global ---
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
    LDA #100
    STA __modify_global_glob_var
    LDA #0
    STA __modify_global_glob_var+1

func_ret_modify_global_0:
    ; --- Function Epilogue for modify_global ---
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
    ; --- Preparazione chiamata a modify_global ---
    JSR func_modify_global_0
    ; --- Fine chiamata a modify_global (valore di ritorno in A/X scartato) ---
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
