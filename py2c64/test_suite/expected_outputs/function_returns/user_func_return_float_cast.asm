;--------- Start python code ---------
; 
; def to_float(x):
;     y = 1 # dummy local var
;     return float(x)
; 
; b_val = 10
; b = to_float(b_val)
; # 'b' should be treated as a float (4 bytes copied)

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
y * = * + 2
b_val * = * + 2
b * = * + 2
__to_float_y * = * + 2
temp_0 * = * + 4
temp_1 * = * + 4
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

func_to_float_0:
    ; --- Function Prologue for to_float ---
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
    LDA #1
    STA __to_float_y
    LDA #0
    STA __to_float_y+1
    LDA temp_1
    STA $FB
    LDA temp_1+1
    STA $FA
    LDA #0
    STA $F9
    JSR FP_FLOAT
    LDA $F8
    STA temp_0+0
    LDA $F9
    STA temp_0+1
    LDA $FA
    STA temp_0+2
    LDA $FB
    STA temp_0+3
    LDA temp_0+3
    STA $F8
    LDA temp_0+0
    STA $F9
    LDA temp_0+1
    STA $FA
    LDA temp_0+2
    STA $FB

func_ret_to_float_0:
    ; --- Function Epilogue for to_float ---
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
    STA b_val
    LDA #0
    STA b_val+1
    LDA b_val
    STA __func_arg_0
    LDA b_val+1
    STA __func_arg_0+1
    JSR func_to_float_0
    LDA $F8
    STA b+3
    LDA $F9
    STA b+0
    LDA $FA
    STA b+1
    LDA $FB
    STA b+2
    JMP end_program

; --- Routines Section ---
    * = $8000
FP_FLOAT     ; Original F451 - Converts 16-bit int in M1, M1+1 to FP in X1,M1. M1+2 must be 0.
    LDA  #$8E     ; INIT EXP1 TO 14 ($80 + 14 = $8E),
    STA  $F8       ; THEN NORMALIZE TO FLOAT.
    JMP FP_NORM1  ; Jump to the NORM1 section for normalization
FP_NORM      ; Original F463
FP_NORM_CHECK_X1
    LDA  $F8       ; EXP1 ZERO?
    BNE  FP_NORM1    ; NO, CONTINUE NORMALIZING.
    ; X1 is zero. If M1 is also zero, it's a true zero. Otherwise, it's smallest denormalized.
    LDA $F9
    ORA $FA
    ORA $FB
    BNE FP_RTS1_NORM_EXIT ; If mantissa not zero, exit (it's 0 * 2^-128 or similar)
    ; True zero, X1 already 0. Mantissa is 0.
FP_RTS1_NORM_EXIT
    RTS           ; RETURN.
FP_NORM1     ; Original F455
    LDA  $F9       ; HIGH-ORDER MANT1 BYTE.
    CMP  #$C0     ; UPPER TWO BITS UNEQUAL? (01xxxxxx or 10xxxxxx)
    BMI  FP_RTS1_NORM     ; YES, RETURN WITH MANT1 NORMALIZED
    ; Not normalized or zero
    DEC  $F8       ; DECREMENT EXP1.
    ASL  $FB
    ROL  $FA     ; SHIFT MANT1 (3 BYTES) LEFT.
    ROL  $F9
    ; Fall through to NORM's check
    JMP FP_NORM_CHECK_X1
FP_RTS1_NORM RTS
end_program
    RTS
