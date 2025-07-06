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
    LDA #$00
    STA temp_0+0
    LDA #$00
    STA temp_0+1
    LDA #$60
    STA temp_0+2
    LDA #$81
    STA temp_0+3
    LDA #7
    STA temp_0
    LDA #0
    STA temp_0+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
