;--------- Start python code ---------
; 
; def returns_float():
;     val = 0.0 # dummy local
;     val = 1.5
;     return val # Current analysis might not catch this if 'val' type isn't tracked well
; 
; def returns_float_direct():
;     return 1.5
; 
; def returns_int():
;     return 7
; 
; f_val = returns_float_direct() # This should be detected as float return
; i_val = returns_int()
; # f_val is float, i_val is int

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
val * = * + 2
f_val * = * + 2
i_val * = * + 2
__returns_float_val * = * + 2
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

func_returns_float_0:
    ; --- Function Prologue for returns_float ---
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
    LDA #$00
    STA __returns_float_val+0
    LDA #$00
    STA __returns_float_val+1
    LDA #$00
    STA __returns_float_val+2
    LDA #$00
    STA __returns_float_val+3
    LDA #$00
    STA __returns_float_val+0
    LDA #$00
    STA __returns_float_val+1
    LDA #$60
    STA __returns_float_val+2
    LDA #$81
    STA __returns_float_val+3
    LDA val+0
    STA temp_0+0
    LDA val+1
    STA temp_0+1
    LDA temp_0+3
    STA $F8
    LDA temp_0+0
    STA $F9
    LDA temp_0+1
    STA $FA
    LDA temp_0+2
    STA $FB

func_ret_returns_float_0:
    ; --- Function Epilogue for returns_float ---
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

func_returns_float_direct_1:
    ; --- Function Prologue for returns_float_direct ---
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
    LDA #$00
    STA temp_0+0
    LDA #$00
    STA temp_0+1
    LDA #$60
    STA temp_0+2
    LDA #$81
    STA temp_0+3
    LDA temp_0+3
    STA $F8
    LDA temp_0+0
    STA $F9
    LDA temp_0+1
    STA $FA
    LDA temp_0+2
    STA $FB

func_ret_returns_float_direct_1:
    ; --- Function Epilogue for returns_float_direct ---
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

func_returns_int_2:
    ; --- Function Prologue for returns_int ---
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
    LDA #7
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0+1
    LDX temp_0

func_ret_returns_int_2:
    ; --- Function Epilogue for returns_int ---
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
    JSR func_returns_float_direct_1
    LDA $F8
    STA f_val+3
    LDA $F9
    STA f_val+0
    LDA $FA
    STA f_val+1
    LDA $FB
    STA f_val+2
    JSR func_returns_int_2
    STX i_val
    STA i_val+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
