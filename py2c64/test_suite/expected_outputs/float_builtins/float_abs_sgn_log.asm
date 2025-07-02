;--------- Start python code ---------
; a = -5.25
; abs_a = abs(a)  # Expected: 5.25
; b = 0.0
; sgn_a = sgn(a)    # Expected: -1.0
; sgn_b = sgn(b)    # Expected: 0.0
; sgn_c = sgn(10.0) # Expected: 1.0
; d = 2.0 # Placeholder for log, as FP_LOG is a stub
; log_d = log(d)
; log_int = log(1) # Test coercion

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
a * = * + 2
abs_a * = * + 2
b * = * + 2
sgn_a * = * + 2
sgn_b * = * + 2
sgn_c * = * + 2
d * = * + 2
log_d * = * + 2
log_int * = * + 2
temp_0 * = * + 4
FP_CONST_ONE byte $00, $00, $40, $81
FP_CONST_TWO byte $00, $00, $40, $82
FP_CONST_LN2 byte $9E, $E0, $58, $80
FP_CONST_INV_LN2 byte $1F, $85, $5B, $81
FP_CONST_3 byte $00, $00, $60, $82
FP_CONST_5 byte $00, $00, $50, $83
FP_CONST_7 byte $00, $00, $70, $83
FP_CONST_9 byte $00, $00, $48, $84
FP_CONST_11 byte $00, $00, $58, $84
error_code * = * + 1
exception_handler_active_flag * = * + 2
current_exception_target_label_ptr * = * + 2
last_exception_type_code * = * + 1
error_msg text "Generic error!"
overflow_msg text "Error: Arithmetic overflow!"
division_by_zero_msg_string text "Error: Division by zero!"
key_error_msg_string text "Error: Key not found!"
value_error_msg_string text "Error: Invalid value!"
attribute_error_msg_string text "Error: Attribute not found!"
not_implemented_error_msg_string text "Error: Not implemented!"
chrout = $FFD2

main_program_entry_point:
; --- Code Section ---
    LDA #<02FF
    STA $E0
    LDA #>02FF
    STA $E1
    LDA a+0
    STA temp_0+0
    LDA a+1
    STA temp_0+1
    LDA temp_0+1
    BPL abs_int_pos_rec_0
    LDA temp_0
    EOR #$FF
    STA abs_a
    LDA temp_0+1
    EOR #$FF
    STA abs_a+1
    LDA abs_a
    CLC
    ADC #1
    STA abs_a
    LDA abs_a+1
    ADC #0
    STA abs_a+1
    JMP abs_int_done_rec_0
abs_int_pos_rec_0:
    LDA temp_0
    STA abs_a
    LDA temp_0+1
    STA abs_a+1
abs_int_done_rec_0:
    LDA #$00
    STA b+0
    LDA #$00
    STA b+1
    LDA #$00
    STA b+2
    LDA #$00
    STA b+3
    LDA #0
    STA sgn_a
    LDA #0
    STA sgn_a+1
    LDA #0
    STA sgn_b
    LDA #0
    STA sgn_b+1
    LDA #0
    STA sgn_c
    LDA #0
    STA sgn_c+1
    LDA #$00
    STA d+0
    LDA #$00
    STA d+1
    LDA #$40
    STA d+2
    LDA #$82
    STA d+3
    LDA d+0
    STA temp_0+0
    LDA d+1
    STA temp_0+1
    LDA d+2
    STA temp_0+2
    LDA d+3
    STA temp_0+3
    LDA temp_0+3
    STA $F8
    LDA temp_0+0
    STA $F9
    LDA temp_0+1
    STA $FA
    LDA temp_0+2
    STA $FB
    JSR FP_LOG
    LDA $F8
    STA log_d+3
    LDA $F9
    STA log_d+0
    LDA $FA
    STA log_d+1
    LDA $FB
    STA log_d+2
    LDA #1
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0+3
    STA $F8
    LDA temp_0+0
    STA $F9
    LDA temp_0+1
    STA $FA
    LDA temp_0+2
    STA $FB
    JSR FP_LOG
    LDA $F8
    STA log_int+3
    LDA $F9
    STA log_int+0
    LDA $FA
    STA log_int+1
    LDA $FB
    STA log_int+2
    JMP end_program

; --- Routines Section ---
    * = $8000
FP_ABSWAP    ; Original F437
    BIT  $F9       ; MANT1 NEGATIVE?
    BPL  FP_ABSWAP1  ; NO, JUMP TO SWAP PART
    JSR  FP_FCOMPL   ; YES, COMPLEMENT IT.
    INC  $F3     ; INCR SIGN, COMPLEMENTING LSB.
FP_ABSWAP1   ; Original F440 (ABSWAP1 label)
    SEC           ; SET CARRY FOR RETURN TO MUL/DIV.
    JSR FP_SWAP      ; Swaps FP1 and FP2
    RTS
FP_ADD_MANT  ; Original F425
    CLC           ; CLEAR CARRY
    LDX  #$2      ; INDEX FOR 3-BYTE ADD.
FP_ADD1_MANT      LDA  $F9,X
    ADC  $F5,X     ; ADD A BYTE OF MANT2 TO MANT1
    STA  $F9,X
    DEX           ; INDEX TO NEXT MORE SIGNIF. BYTE.
    BPL  FP_ADD1_MANT     ; LOOP UNTIL DONE.
    RTS           ; RETURN
FP_ALGNSWP   ; Original F47B - Called when X1 != X2. Carry from CMP X1 is key.
             ; CMP X2, X1. If C=0 (X2 < X1), then swap.
    BCC  FP_ALGNSWP_SWAP     ; SWAP IF CARRY CLEAR (X2 < X1)
    ; Here X2 >= X1. Shift M1 (smaller magnitude) right.
FP_ALGNSWP_SHIFT_M1:
    JSR  FP_RTAR      ; Shifts M1 right, increments X1.
    LDA  $F4   ; Compare X2 with new X1
    CMP  $F8
    BNE  FP_ALGNSWP_SHIFT_M1 ; Loop if still not equal
    RTS              ; Exponents equal, return to FADD to add mantissas
FP_ALGNSWP_SWAP:
    JSR  FP_SWAP      ; Swap FP1 and FP2
    ; After swap, X1 was original X2, X2 was original X1.
    ; Now X1 (new) > X2 (new). Shift M2 (which is now in M1 due to prior logic flow)
    JMP FP_ALGNSWP_SHIFT_M1 ; Re-enter logic to shift the (now smaller) M1.
FP_FADD      ; Original F46E
    LDA  $F4
    CMP  $F8       ; COMPARE EXP1 WITH EXP2.
    BNE  FP_FADD_SWPALGN  ; IF #,SWAP ADDENDS OR ALIGN MANTS.
FP_FADD_ADD_ALIGNED
    JSR  FP_ADD_MANT      ; ADD ALIGNED MANTISSAS.
FP_FADD_ADDEND ; Original F477
    BVC  FP_NORM     ; NO OVERFLOW, NORMALIZE RESULT.
    ; Overflow occurred during mantissa add
    BVS  FP_RTLOG_ENTRY    ; OV: SHIFT M1 RIGHT, CARRY (sign of sum) INTO SIGN
    RTS ; Should not be reached
FP_FADD_SWPALGN ; Original F46B (SWPALGN label) / F472 (BNE target)
    JSR FP_ALGNSWP
    JMP FP_FADD_ADD_ALIGNED ; After alignment, add mantissas
FP_FCOMPL    ; Original F4A4
    SEC           ; SET CARRY FOR SUBTRACT.
    LDX  #$02     ; INDEX FOR 3 BYTE SUBTRACT (M1, M1+1, M1+2)
FP_FCOMPL_COMPL1 LDA  #$00     ; CLEAR A.
    SBC  $F9,X     ; SUBTRACT BYTE OF M1 (0 - M1,X - C)
    STA  $F9,X     ; RESTORE IT.
    DEX
    BPL  FP_FCOMPL_COMPL1   ; LOOP UNTIL DONE.
    CLC           ; Clear carry after 2's complement.
    BEQ  FP_FADD_ADDEND ; NORMALIZE (OR SHIFT RT IF OVFL). (Jumps to FADD's overflow handling/normalization path)
    RTS ; Should not be reached if BEQ taken
FP_FDIV      ; Original F4B2. FP1=Divisor, FP2=Dividend. Result in FP1.
    JSR FP_SWAP      ; Dividend (orig FP2) to FP1, Divisor (orig FP1) to FP2. E gets orig Divisor mantissa.
    JSR  FP_MD1      ; ABS VAL. Dividend in M1, Divisor in M2. SIGN has combined sign. E has |Divisor Mant|.
    LDA $F8 ; Exp of Dividend
    SBC  $F4       ; SUBTRACT EXP of Divisor FROM EXP of Dividend.
    JSR  FP_MD2      ; SAVE AS QUOTIENT EXP in X1. M1 (quotient) cleared. Y has count.
FP_FDIV_DIV1 SEC           ; SET CARRY FOR SUBTRACT.
    LDX  #$02     ; INDEX FOR 3-BYTE SUBTRACTION.
FP_FDIV_DIV2 LDA  $F9,X ; Current Dividend (shifted)
    SBC  $FC,X      ; SUBTRACT A BYTE OF |Divisor Mant| (from E) FROM MANT1.
    PHA           ; SAVE ON STACK.
    DEX           ; X was $02,$01,$00 for loading M1,X. After DEX, X is $01,$00,$FF.
    BPL  FP_FDIV_DIV2     ; LOOP UNTIL DONE.
    LDX  #$FD     ; INDEX FOR 3-BYTE CONDITIONAL MOVE. X will be $FD, $FE, $FF for MSB, MID, LSB of difference.
FP_FDIV_DIV3 PLA           ; PULL BYTE OF DIFFERENCE OFF STACK
    BCC  FP_FDIV_DIV4     ; IF M1<E (borrow occurred) THEN DON'T RESTORE M1.
    STA  $FC,X ; Restore M1 from stack. M1+3 ($FC) is base. X is $FD, $FE, $FF.
                                     ; $FC+$FD=$F9 (M1), $FC+$FE=$FA (M1+1), $FC+$FF=$FB (M1+2)
FP_FDIV_DIV4: ; Placeholder for now
    ; The ROL M1 sequence depends on the carry from the 3-byte subtraction.
    ; This needs to be the carry flag *after* all 3 SBCs.
    ; The original code implies the carry from the last SBC is used for the ROL.
    ; This is standard non-restoring division.
    ROL  $FB ; LSB of quotient
    ROL  $FA
    ROL  $F9   ; MSB of quotient (contains sign eventually)
    ; Shift current dividend (M1) left for next bit.
    ; The original shifts M2, which held the |Divisor|. This seems wrong.
    ; It should shift the remainder part of the dividend.
    ; The dividend is in M1. After subtraction, M1 is the remainder.
    ASL  $FB ; Shift remainder (M1) left
    ROL  $FA
    ROL  $F9
    ; BCS  FP_OVFL_ROUTINE_CALL ; OVFL IS DUE TO UNNORMED DIVISOR (This was for M2 shift)
    DEY           ; NEXT DIVIDE ITERATION.
    BNE  FP_FDIV_DIV1     ; LOOP UNTIL DONE 23 ITERATIONS.
    BEQ  FP_FMUL_MDEND    ; NORM. QUOTIENT AND CORRECT SIGN. (Reusing MDEND from FMUL)
    RTS ; Should not be reached
FP_FMUL      ; Original F48C
    JSR  FP_MD1      ; ABS VAL OF MANT1, MANT2. Result sign in SIGN lsb. M1=|M1|, M2=|M2| (after swap)
    ADC  $F8       ; ADD EXP1 TO EXP2 (original X1+X2) FOR PRODUCT EXP
    JSR  FP_MD2      ; CHECK PROD. EXP AND PREP. FOR MUL. Result exp in X1. M1 cleared. Y has count.
    CLC           ; CLEAR CARRY FOR FIRST BIT.
FP_FMUL_MUL1 JSR  FP_RTLOG1   ; M1 (product) AND E (multiplier |M2|) RIGHT. LSB of |M2| to Carry.
    BCC  FP_FMUL_MUL2     ; IF CARRY CLEAR, SKIP PARTIAL PROD
    JSR  FP_ADD_MANT      ; ADD MULTIPLICAND (|M1| original, now in M2) TO PRODUCT (in M1).
FP_FMUL_MUL2 DEY           ; NEXT MUL ITERATION.
    BPL  FP_FMUL_MUL1     ; LOOP UNTIL DONE.
FP_FMUL_MDEND ; Original F4A0
    LSR  $F3     ; TEST SIGN LSB. If 1, result is negative.
FP_FMUL_NORMX ; Original F4A2
    BCC  FP_NORM     ; IF EVEN (SIGN LSB was 0), NORMALIZE PROD, ELSE COMPLEMENT
    JMP FP_FCOMPL    ; If ODD (SIGN LSB was 1), complement M1 then normalize
FP_FSUB      ; Original F468. Calculates FP1 = FP1 - FP2.
             ; FP1 is in X1/M1, FP2 is in X2/M2. Result in X1/M1.
    JSR FP_SWAP      ; M1 now holds original FP2, M2 now holds original FP1.
                     ; E gets original FP2 mantissa (not strictly needed for FSUB logic but SWAP does it).
    JSR FP_FCOMPL    ; M1 (which was original FP2) is complemented: M1 = -original_FP2.
                     ; M2 is still original FP1.
    JMP FP_FADD      ; Calculates M1_current + M2_current = (-original_FP2) + original_FP1.
                     ; Result (original_FP1 - original_FP2) is stored in X1/M1.
FP_LOG       ; Natural Logarithm of FP1. Result in FP1.
    ; This is a stub implementation for testing purposes.
    ; It returns 0.0 regardless of input.
    LDA #$00                ; Exponent for 0.0
    STA $F8
    LDA #$00                ; Mantissa MSB for 0.0
    STA $F9
    LDA #$00                ; Mantissa MID for 0.0
    STA $FA
    LDA #$00                ; Mantissa LSB for 0.0
    STA $FB
    RTS
FP_LOG       ; Natural Logarithm of FP1. Result in FP1.
    ; Handles input <= 0 by setting last_exception_type_code to ValueError and jumping to error_handler.
    ; Based on Apple II ROM F68D. Uses series for ln((x+1)/(x-1))

    LDA $F8
    BNE FP_LOG_CHECK_SIGN       ; If exponent is not zero, it's not 0.0, check sign
    ; Exponent is zero, so the number is 0.0. This is a domain error.
    JMP FP_LOG_DOMAIN_ERROR

FP_LOG_CHECK_SIGN:
    ; Check sign bit (MSB of Mantissa M1 at $F9)
    BIT $F9
    BPL FP_LOG_POSITIVE_INPUT   ; If MSB is 0 (positive), proceed

FP_LOG_DOMAIN_ERROR:            ; Handles both zero and negative input
    LDA #5
    STA last_exception_type_code
    JMP error_handler

FP_LOG_POSITIVE_INPUT:
    ; Calculate z = (x-1)/(x+1)
    ; FP1 has x. Load 1.0 into FP2.
    JSR FP_LOG_LOAD_ONE_FP2
    ; Swap so FP1=1, FP2=x
    JSR FP_SWAP
    ; FP1 = x+1
    JSR FP_FADD
    ; Store x+1 in E
    LDX #$03
FP_LOG_COPY_X_PLUS_1_TO_E: LDA $F8,X; STA $FC,X; DEX; BPL FP_LOG_COPY_X_PLUS_1_TO_E

    ; FP1 has x+1. FP2 has x. FP1 = x-1
    JSR FP_FSUB

    ; Now FP1 has x-1. Load x+1 from E into FP2.
    LDX #$03
FP_LOG_COPY_E_TO_FP2: LDA $FC,X; STA $F4,X; DEX; BPL FP_LOG_COPY_E_TO_FP2

    ; FP1 = (x-1)/(x+1) = z
    JSR FP_FDIV

    ; Now FP1 has z. Calculate series S = z + z^3/3 + z^5/5 ...
    ; And result is 2*S
    ; Store z^2 in E.
    JSR FP_LOG_COPY_FP1_TO_FP2 ; FP2 = z
    JSR FP_FMUL ; FP1 = z*z
    LDX #$03
FP_LOG_COPY_Z2_TO_E: LDA $F8,X; STA $FC,X; DEX; BPL FP_LOG_COPY_Z2_TO_E

    ; Term is in FP1 (z^2). Sum is in FP2 (z).
    ; Loop for n=3,5,7,9,11
    LDY #0 ; Y is index for constant array [3,5,7,9,11]
FP_LOG_SERIES_LOOP:
    ; current term is in FP1. z^2 is in E.
    ; next term = current_term * z^2
    LDX #$03
FP_LOG_COPY_E_TO_FP2_LOOP: LDA $FC,X; STA $F4,X; DEX; BPL FP_LOG_COPY_E_TO_FP2_LOOP
    JSR FP_FMUL ; FP1 = term * z^2

    ; Divide by n. Load n into FP2.
    ; This part is complex. Simplified:
    ; JSR LOAD_CONST_N_FP2
    ; JSR FP_FDIV
    ; JSR ADD_TO_SUM
    INY
    CPY #5
    BNE FP_LOG_SERIES_LOOP

    ; Final result: sum * 2
    ; Sum is in FP2. Load 2.0 into FP1.
    JSR FP_LOG_LOAD_TWO_FP1
    JSR FP_FMUL
    RTS

FP_LOG_LOAD_ONE_FP2:
    LDX #3
FP_LOG_L1_LOOP: LDA FP_CONST_ONE,X; STA $F4,X; DEX; BPL FP_LOG_L1_LOOP; RTS
FP_LOG_COPY_FP1_TO_FP2:
    LDX #3
FP_LOG_CP12_LOOP: LDA $F8,X; STA $F4,X; DEX; BPL FP_LOG_CP12_LOOP; RTS
FP_LOG_LOAD_TWO_FP1:
    LDX #3
FP_LOG_L2_LOOP: LDA FP_CONST_TWO,X; STA $F8,X; DEX; BPL FP_LOG_L2_LOOP; RTS
FP_MD1       ; Original F432
    ASL  $F3     ; CLEAR LSB OF SIGN.
    JSR  FP_ABSWAP   ; ABS VAL OF M1, THEN SWAP WITH M2
    ; SEC is part of FP_ABSWAP's exit path (FP_ABSWAP1)
    RTS
FP_MD2       ; Original F4E2. A contains exponent. X should be 0 on entry.
    STX  $FB ; Clear M1 (3 bytes)
    STX  $FA
    STX  $F9
FP_MD2_OVCHK ; Original F4E8
    BCS  FP_MD2_MD3_NO_UNDERFLOW_CHECK ; If exponent calculation set Carry (overflow for add, no borrow for sub)
    ; No carry from exponent calculation. Check for underflow (negative result).
    BMI  FP_MD2_MD3_COMPLEMENT_SIGN ; If negative exponent (but no carry), it's valid negative.
    ; Positive exponent but no carry from initial ADC/SBC means underflow (e.g. small + small = too small)
    ; Or large_neg - small_pos = very_large_neg (underflow if X1 becomes < 00)
    PLA           ; POP ONE RETURN LEVEL.
    PLA
    ; Set result to 0 for underflow
    LDA #0
    STA $F8
    STA $F9
    STA $FA
    STA $FB
    RTS           ; Early return with 0
FP_MD2_MD3_NO_UNDERFLOW_CHECK: ; Original F4F7 (OVCHK BPL MD3) - if positive exp, no overflow
    BPL FP_MD2_MD3_COMPLEMENT_SIGN
    JMP FP_OVFL_ROUTINE_CALL ; Negative exponent AND carry means overflow

FP_MD2_MD3_COMPLEMENT_SIGN ; Original F4F0 (MD3 label)
    EOR  #$80     ; COMPLEMENT SIGN BIT OF EXPONENT.
FP_MD2_STORE_EXP_AND_SET_Y
    STA  $F8       ; STORE IT.
    LDY  #$17     ; COUNT 24 MUL/23 DIV ITERATIONS.
    RTS           ; RETURN.
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
FP_OVFL_HANDLER
    LDA #1
    JMP error_handler ; Use the project's main error handler
FP_RTAR      ; Original F47D
    LDA  $F9       ; SIGN OF MANT1 INTO CARRY FOR
    ASL           ; RIGHT ARITH SHIFT. (Sign bit to Carry, 0 into bit 7)
    ; Fall through to RTLOG
    JMP FP_RTLOG_COMMON_PART ; Jump to the part of RTLOG that does the work
FP_RTLOG_COMMON_PART: ; Label for common logic of RTLOG and RTAR
    INC  $F8       ; INCR X1 TO ADJUST FOR RIGHT SHIFT
    BEQ  FP_OVFL_ROUTINE_CALL     ; EXP1 OUT OF RANGE.
    ; Fall through to RTLOG1
    JMP FP_RTLOG1
FP_RTLOG1    ; Original F484 - Shifts M1 and E right 1 bit. Carry from input shifts into M1 MSB.
    LDX  #$FA     ; INDEX FOR 6-BYTE RIGHT SHIFT (M1_H, M1_M, M1_L, E_H, E_M, E_L)
                  ; $FA = -6. E+3,X means base $FF+X.
                  ; $FF-6 = $F9 (M1_H)
                  ; $FF-5 = $FA (M1_M)
                  ; ...
                  ; $FF-1 = $FE (E_L)
FP_RTLOG1_ROR1
    ROR  $FF,X ; ROR ($FF),X then ($00),X etc.
    INX           ; NEXT BYTE OF SHIFT.
    BNE  FP_RTLOG1_ROR1     ; LOOP UNTIL DONE.
    RTS           ; RETURN.
FP_SWAP      ; Original F441
    LDX  #$4      ; INDEX FOR 4 BYTE SWAP (X1,M1 with X2,M2 = 1+3+1+3 bytes, but E is also used)
                  ; The loop swaps X1,M1 (4 bytes) with X2,M2 (4 bytes)
                  ; and E ($FC,FD,FE) gets a copy of original M1 ($F9,FA,FB)
                  ; STY E-1,X is STY $FB,X. If X=$04, $FB+$04 = $FF.
                  ; This means E-1 ($FB) is used as a base for STY.
                  ; X1-1 ($F7) is base for LDA X1-1,X and STY X1-1,X
                  ; X2-1 ($F3) is base for LDY X2-1,X and STA X2-1,X
                  ; This routine swaps X1/M1 with X2/M2 and puts M1 into E.
                  ; Let's simplify to just swap X1/M1 and X2/M2 for now.
                  ; The E copy is used by FDIV.
    LDX #$03      ; Iterate 4 times (0,1,2,3) for Exp+Mant1, Exp+Mant2
FP_SWAP_LOOP:
    LDA $F8,X  ; Load byte from FP1 (X1, M1, M1+1, M1+2)
    PHA                     ; Save it
    LDA $F4,X  ; Load byte from FP2 (X2, M2, M2+1, M2+2)
    STA $F8,X  ; Store into FP1
    PLA                     ; Get original FP1 byte
    STA $F4,X  ; Store into FP2
    DEX
    BPL FP_SWAP_LOOP
    ; For FDIV, M1 (original) needs to be in E.
    ; After swap, original M1 is in M2. So copy M2 to E.
    LDX #$02 ; M2 is 3 bytes
FP_SWAP_COPY_M2_TO_E_LOOP:
    LDA $F5,X
    STA $FC,X
    DEX
    BPL FP_SWAP_COPY_M2_TO_E_LOOP
    RTS
ascii_to_petscii
    ; Input: A contains ASCII character
    ; Output: A contains PETSCII character (lowercase ASCII converted to uppercase PETSCII)
    CMP #'a'
    BCC no_conversion_needed_petscii
    CMP #'z'+1
    BCS no_conversion_needed_petscii
    SEC             ; Ensure Carry is set for SBC
    SBC #$20        ; Convert ASCII 'a'-'z' to PETSCII 'A'-'Z' (e.g. ASCII 'a' (97) - 32 = PETSCII 'A' (65))
no_conversion_needed_petscii
    RTS
attribute_error_msg
    LDA #<attribute_error_msg_string
    STA temp_0
    LDA #>attribute_error_msg_string
    STA temp_0+1
    JMP print_string
division_by_zero_msg
    LDA #<division_by_zero_msg_string
    STA temp_0
    LDA #>division_by_zero_msg_string
    STA temp_0+1
    JMP print_string
end_program
    RTS
error_handler
    STA error_code
    ; Print error message
    ; Load the message pointer
    LDA error_code
    JSR print_error_message
    JMP end_program
generic_error_msg
    LDA #<error_msg
    STA temp_0
    LDA #>error_msg
    STA temp_0+1
    JMP print_string
key_error_msg
    LDA #<key_error_msg_string
    STA temp_0
    LDA #>key_error_msg_string
    STA temp_0+1
    JMP print_string
not_implemented_error_msg
    LDA #<not_implemented_error_msg_string
    STA temp_0
    LDA #>not_implemented_error_msg_string
    STA temp_0+1
    JMP print_string
overflow_error_msg
    LDA #<overflow_msg
    STA temp_0
    LDA #>overflow_msg
    STA temp_0+1
    JMP print_string
print_char
    ; Input: A = ASCII character
    ; Output: Prints character to screen via KERNAL CHROUT
    ; Modifies: A (CHROUT modifica A)
    ; Preserves: X, Y (CHROUT preserva X, Y)

    JSR ascii_to_petscii    ; Convert A from ASCII to PETSCII. A is now PETSCII.
    JSR chrout              ; Call KERNAL CHROUT routine (address defined in data section)
    RTS
print_error_message
    CMP #1
    BNE pem_check_div_zero
    JMP overflow_error_msg
pem_check_div_zero:
    CMP #2
    BNE pem_check_key_not_found
    JMP division_by_zero_msg
pem_check_key_not_found:
    CMP #4
    BNE pem_check_value_error
    JMP key_error_msg
pem_check_value_error:
    CMP #5
    BNE pem_check_type_error
    JMP value_error_msg
pem_check_type_error:
    CMP #6
    BNE pem_check_index_error
    JMP generic_error_msg
pem_check_index_error:
    CMP #7
    BNE pem_check_name_error
    JMP generic_error_msg
pem_check_name_error:
    CMP #8
    BNE pem_check_assertion_error
    JMP generic_error_msg
pem_check_assertion_error:
    CMP #9
    BNE pem_check_attribute_error
    JMP generic_error_msg
pem_check_attribute_error:
    CMP #10
    BNE pem_check_not_implemented_error
    JMP attribute_error_msg
pem_check_not_implemented_error:
    CMP #11
    BNE pem_check_generic_runtime
    JMP not_implemented_error_msg
pem_check_generic_runtime:
    CMP #255
    BNE pem_end_error_message
    JMP generic_error_msg
pem_end_error_message:
    RTS
print_string
    ; Routine to print a string located at the address contained in the var temp_0
    ; Uses ZP locations $FA/$FB for the 16-bit string pointer.
    ; Preserves A and Y registers.
    PHA                     ; Save A
    TYA                     ; Transfer Y to A (to save Y on stack)
    PHA                     ; Push A (which now holds Y's original value)
    LDA temp_0                ; Load LSB of string address from temp_0 (a .word variable)
    STA $FA           ; Store LSB into ZP pointer
    LDA temp_0+1              ; Load high byte of address from temp_0+1
    STA $FB         ; Store MSB into ZP pointer

    LDY #$00                  ; Use Y as the index for LDA (ZP),Y. This Y is local to the loop.
print_loop_ps               ; Renamed label to avoid conflict if routine is included multiple times (though it shouldn't be)
        LDA ($FA),Y ; Use (Indirect),Y addressing with ZP pointer
        BEQ end_print_ps      ; If char is NUL, end.
        JSR print_char          ; print_char preserves A, does not use Y.
        INY                     ; Increment Y
    ; Check if Y wrapped around (very unlikely for typical strings)
    ; If Y becomes 0 after INY, it means we crossed a 256-byte boundary with Y.
    CPY #0
    BNE print_loop_ps       ; If Y is not 0, continue loop within the current 256-byte page
    ; If Y wrapped to 0, it means we printed 256 chars. Increment MSB of ZP pointer.
    INC $FB
    JMP print_loop_ps       ; And continue printing (Y is 0 again for the new page)
end_print_ps
    PLA                     ; Pop original Y value (into A)
    TAY                     ; Transfer A to Y (restoring Y)
    PLA                     ; Pop original A value
    RTS
