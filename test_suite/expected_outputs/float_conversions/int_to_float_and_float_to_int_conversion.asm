;--------- Start python code ---------
; 
; a_int = 5
; b_float = float(a_int)
; 
; c_float = -3.75
; d_int = int(c_float)
; 
; # Expected (for verification via print or debugger if available):
; # b_float should be 5.0
; # d_int should be -3 (due to truncation towards zero)

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
a_int * = * + 2
b_float * = * + 2
c_float * = * + 2
d_int * = * + 2
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
    LDA #5
    STA a_int
    LDA #0
    STA a_int+1
    LDA a_int+0
    STA temp_0+0
    LDA a_int+1
    STA temp_0+1
    LDA temp_0
    STA $FB
    LDA temp_0+1
    STA $FA
    LDA #0
    STA $F9
    JSR FP_FLOAT
    LDA $F8
    STA b_float+0
    LDA $F9
    STA b_float+1
    LDA $FA
    STA b_float+2
    LDA $FB
    STA b_float+3
    LDA #0
    STA c_float
    LDA #0
    STA c_float+1
    LDA c_float+0
    STA temp_0+0
    LDA c_float+1
    STA temp_0+1
    LDA temp_0+0
    STA d_int+0
    LDA temp_0+1
    STA d_int+1
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
