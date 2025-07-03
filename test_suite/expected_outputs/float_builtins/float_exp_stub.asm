;--------- Start python code ---------
; # Test exp() stub - should call FP_EXP and handle type.
; # FP_EXP itself will signal NotImplementedError at runtime.
; # We are testing the compilation path to FP_EXP.
; res_exp_float = exp(1.0)
; res_exp_int = exp(2) # Test integer to float coercion for argument

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
res_exp_float * = * + 2
res_exp_int * = * + 2
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
    STA res_exp_float
    LDA #0
    STA res_exp_float+1
    LDA #0
    STA res_exp_int
    LDA #0
    STA res_exp_int+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
