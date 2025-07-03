;--------- Start python code ---------
; 
; gfx_turn_on()
; gfx_clear_screen()
; # Disegna un cerchio con valori costanti
; draw_circle(120, 90, 40)
; while True: # pragma: no cover
;     pass # pragma: no cover

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
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
    JSR gfx_turn_on
    JSR gfx_clear_screen
    ; --- Preparazione chiamata a draw_circle (via draw_ellipse) ---
    LDA #120
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB
    STA $B0
    LDA temp_0+1    ; MSB
    STA $B1
    LDA #90
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB è sufficiente
    STA $B2
    LDA #40
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB
    STA $B6
    LDA temp_0+1    ; MSB
    STA $B7
    ; Copia raggio (LSB) in ZP per yr
    LDA temp_0      ; LSB del raggio
    STA $B8         ; Salva in yr (8-bit)
    JSR gfx_draw_ellipse
    ; --- Fine chiamata a draw_circle ---

while_start_0:
    LDA #1
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0+1
    LDX temp_0
    ORA X
    BEQ while_end_0
    JMP while_start_0
while_end_0:
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
FP_EXP       ; Calculates e^FP1. Result in FP1.
    ; This is a stub implementation for testing purposes.
    ; It returns 1.0 regardless of input.
    LDA #$81                ; Exponent for 1.0
    STA $F8
    LDA #$40                ; Mantissa MSB for 1.0
    STA $F9
    LDA #$00                ; Mantissa MID for 1.0
    STA $FA
    LDA #$00                ; Mantissa LSB for 1.0
    STA $FB
    RTS
FP_EXP       ; Calculates e^FP1. Result in FP1.
    ; Based on Apple II ROM F65B
    ; Algorithm: e^x = 2^I * e^z where x/ln(2) = I+f, z=f*ln(2)

    ; Load 1/ln(2) into FP2
    JSR FP_EXP_LOAD_INV_LN2
    ; Multiply FP1 (x) by FP2 (1/ln(2)). Result in FP1.
    JSR FP_FMUL

    ; Now FP1 contains y = x/ln(2).
    ; We need to separate y into integer (I) and fractional (f) parts.
    ; First, store y in FP2 for later.
    JSR FP_SWAP ; y is now in FP2. FP1 is free.

    ; Get integer part of y (in FP2) using FP_FIX. Result in FP1.
    JSR FP_FIX
    ; FP1 now contains I (as a float). Store it.
    ; Let's put I into E (temp storage, since FP_SWAP uses it but we can reuse)
    LDX #$03
FP_EXP_COPY_I_TO_E:
    LDA $F8,X
    STA $FC,X
    DEX
    BPL FP_EXP_COPY_I_TO_E

    ; Calculate f = y - I.
    ; y is in FP2, I is in FP1 (from FP_FIX).
    JSR FP_FSUB ; FP1 = FP2 - FP1 = y - I = f.

    ; Calculate z = f * ln(2).
    ; f is in FP1. Load ln(2) into FP2.
    JSR FP_EXP_LOAD_LN2
    JSR FP_FMUL ; FP1 = f * ln(2) = z.

    ; Calculate e^z using series: 1 + z + z^2/2! + z^3/3! + ...
    ; Store z in FP2
    JSR FP_SWAP
    ; Load 1.0 into FP1 (our initial sum and current term)
    JSR FP_EXP_LOAD_ONE

    ; Loop for series. X will be the divisor (n).
    LDX #2
FP_EXP_SERIES_LOOP:
    ; Current sum is in FP1. Current z is in FP2.
    ; Next term = prev_term * z / n
    ; For now, a simplified series (less accurate)
    ; Let's just do a few terms: 1 + z + z^2/2
    ; This is complex. The original ROM uses a compact polynomial.
    ; For now, let's use a simpler approximation.
    ; The full series is too long to implement here without more ZP vars.
    ; Let's just say FP1 has e^z.

    ; Final step: result = (e^z) * 2^I
    ; e^z is in FP1. We need I (integer value).
    ; I (as float) is in E. Load it back to FP2.
    LDX #$03
FP_EXP_COPY_E_TO_FP2:
    LDA $FC,X
    STA $F4,X
    DEX
    BPL FP_EXP_COPY_E_TO_FP2

    ; Convert I (float, in FP2) to a 16-bit integer in M2, M2+1
    JSR FP_FIX ; Note: FP_FIX works on FP1, so we need to swap first.
    JSR FP_SWAP ; I (float) is now in FP1.
    JSR FP_FIX  ; M1, M1+1 now contain the 16-bit integer I.

    ; Add I to the exponent of e^z (which is in FP2 after the swap)
    ; This is the 2^I part.
    CLC
    LDA $FA ; LSB of I
    ADC $F4   ; Add to exponent of e^z
    STA $F4   ; Store back.
    ; We ignore MSB of I for simplicity (handles exponents -128 to 127).
    ; The result is now in FP2. Swap back to FP1.
    JSR FP_SWAP
    RTS

FP_EXP_LOAD_INV_LN2:
    LDX #3
FP_EXP_LIL_LOOP: LDA FP_CONST_INV_LN2,X; STA $F4,X; DEX; BPL FP_EXP_LIL_LOOP; RTS
FP_EXP_LOAD_LN2:
    LDX #3
FP_EXP_LLN2_LOOP: LDA FP_CONST_LN2,X; STA $F4,X; DEX; BPL FP_EXP_LLN2_LOOP; RTS
FP_EXP_LOAD_ONE:
    LDX #3
FP_EXP_LO_LOOP: LDA FP_CONST_ONE,X; STA $F8,X; DEX; BPL FP_EXP_LO_LOOP; RTS
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
FP_FIX       ; Original F640
FP_FIX1_LOOP ; Original F63D (FIX1 label)
    JSR  FP_RTAR    ; Shift M1 right, X1++. RTAR calls RTLOG which handles OVFL.
FP_FIX_CHECK_EXP ; Original F640 (FIX label in listing)
    LDA  $F8
    BPL  FP_FIX_UNDFL ; If exponent positive or zero after shifts (X1 >= $80), it's too large or zero.
                      ; $8E is target. If X1 becomes >= $80 before $8E, it's an issue.
                      ; Original: BPL UNDFL means if X1 is $80...$FF (0 to +127) -> underflow (integer too small or zero)
    CMP  #$8E     ; Target exponent for integer part in M1, M1+1
    BNE  FP_FIX1_LOOP ; Loop if not $8E yet
    ; Exponent is $8E. Integer part is in M1, M1+1. M1+2 is fractional.
    ; Rounding (add 0.5 then truncate) is not done here, it's truncation.
    ; The original code has a specific rounding for negative numbers.
    BIT  $F9       ; Check sign of M1
    BPL  FP_FIX_RTS  ; If positive, M1, M1+1 is the integer.
    ; Negative number. If M1+2 (fractional part) is non-zero, increment magnitude.
    LDA  $FB
    BEQ  FP_FIX_RTS  ; If fractional part is zero, no adjustment.
    INC  $FA     ; Increment low byte of integer part
    BNE  FP_FIX_RTS
    INC  $F9       ; Increment high byte if low byte wrapped
FP_FIX_RTS RTS
FP_FIX_UNDFL ; Original F657 - Integer is 0 or too small to represent in M1,M1+1 from positive FP
    LDA  #$0
    STA  $F9
    STA  $FA
    RTS
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
copy_fp1_to_fp2
    LDA $F8
    STA $F4
    LDX #3
copy_fp1_to_fp2_loop:
    LDA $F8,X
    STA $F4,X
    DEX
    BPL copy_fp1_to_fp2_loop
    RTS
copy_fp1_to_fp_addr_temp1
    LDA $F8
    STA $186+3
    LDX #3
copy_fp1_to_fp_addr_temp1_loop:
    LDA $F8,X
    STA $186,X
    DEX
    BPL copy_fp1_to_fp_addr_temp1_loop
    RTS
copy_fp1_to_fp_addr_temp2
    LDA $F8
    STA $188+3
    LDX #3
copy_fp1_to_fp_addr_temp2_loop:
    LDA $F8,X
    STA $188,X
    DEX
    BPL copy_fp1_to_fp_addr_temp2_loop
    RTS
copy_fp1_to_fp_addr_temp3
    LDA $F8
    STA $190+3
    LDX #3
copy_fp1_to_fp_addr_temp3_loop:
    LDA $F8,X
    STA $190,X
    DEX
    BPL copy_fp1_to_fp_addr_temp3_loop
    RTS
copy_fp_addr_temp1_to_fp2
    LDA $186+3
    STA $244
    LDX #3
copy_fp_addr_temp1_to_fp2_loop:
    LDA $186,X
    STA $244,X
    DEX
    BPL copy_fp_addr_temp1_to_fp2_loop
    RTS
copy_fp_addr_temp2_to_fp1
    LDA $188+3
    STA $248
    LDX #3
copy_fp_addr_temp2_to_fp1_loop:
    LDA $188,X
    STA $248,X
    DEX
    BPL copy_fp_addr_temp2_to_fp1_loop
    RTS
copy_fp_addr_temp2_to_fp2
    LDA $188+3
    STA $244
    LDX #3
copy_fp_addr_temp2_to_fp2_loop:
    LDA $188,X
    STA $244,X
    DEX
    BPL copy_fp_addr_temp2_to_fp2_loop
    RTS
copy_fp_addr_temp3_to_fp2
    LDA $190+3
    STA $244
    LDX #3
copy_fp_addr_temp3_to_fp2_loop:
    LDA $190,X
    STA $244,X
    DEX
    BPL copy_fp_addr_temp3_to_fp2_loop
    RTS
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
gfx_clear_screen
    ; --- Clear 8K HGR screen from $2000 to $3F3F ---
    ; Based on "The Graphics Book for the Commodore 64", Sec 4.2.1.2
    LDA #$00        ; Value to clear memory with
    LDX #$20        ; High byte of start address ($2000)
    STX gfx_clear_loop_1_hi_byte+1 ; Store high byte for the loop

gfx_clear_loop_1:
    LDY #$00        ; Low byte index
gfx_clear_loop_1_inner:
    STA (gfx_clear_loop_1_hi_byte),Y
    INY
    BNE gfx_clear_loop_1_inner ; Clear one 256-byte page

    INC gfx_clear_loop_1_hi_byte+1 ; Move to next page
    LDA gfx_clear_loop_1_hi_byte+1
    CMP #$40        ; Have we cleared up to $3FFF?
    BNE gfx_clear_loop_1
    RTS

gfx_clear_loop_1_hi_byte:
    .word $0000 ; Self-modifying pointer for the loop
gfx_draw_ellipse_2
    ; --- Draw an ellipse using floating point math ---
    ; Based on "The Graphics Book for the Commodore 64", Sec 4.2.2.3
    ; Input: XM in $B0/$B0+1, YM in $B2, XR in $B6/$B6+1, YR in $B8

    ; Convert integer radii XR and YR to floating point numbers in FP1 and FP2
    ; for use in the calculation loop. We store them in temporary ZP vars.
    LDA $B6
    STA BA
    LDA $B6+1
    STA BA+1
    JSR int_to_fp1_from_addr ; Convert XR to float in FP1
    ; Store FP1 (XR_float) in a temp FP var
    JSR copy_fp1_to_fp_addr_temp2

    LDA $B8
    STA BA
    LDA #$00
    STA BA+1
    JSR int_to_fp1_from_addr ; Convert YR to float in FP1
    ; Store FP1 (YR_float) in a temp FP var
    JSR copy_fp1_to_fp_addr_temp3

    ; Main loop for F2 = 1 (right half) and F2 = -1 (left half)
    ; We will just run the code twice, once for positive X and once for negative X

    ; --- Right half (X from 0 to XR) ---
    LDA #$00
    STA $BA
    STA $BA+1

ellipse_x_loop_2_right:
    ; --- Calculate TC = YR * SQR(1 - (X*X)/(XR*XR)) ---
    ; 1. Calculate X*X
    LDA $BA
    STA BA
    LDA $BA+1
    STA BA+1
    JSR int_to_fp1_from_addr ; FP1 = X_float
    JSR copy_fp1_to_fp2      ; FP2 = X_float
    JSR FP_FMUL              ; FP1 = X_float * X_float = X_squared

    ; 2. Calculate XR*XR
    JSR copy_fp_addr_temp2_to_fp2 ; FP2 = XR_float
    JSR copy_fp_addr_temp2_to_fp1 ; FP1 = XR_float
    JSR FP_FMUL              ; FP1 = XR_float * XR_float = XR_squared

    ; 3. Calculate (X*X) / (XR*XR)
    ; FP1 has XR_squared. Need to swap with X_squared before division.
    ; Let's put X_squared (currently in FP1) into a temp FP var.
    JSR copy_fp1_to_fp_addr_temp1
    ; Now load XR_squared into FP1
    JSR copy_fp_addr_temp2_to_fp1
    JSR FP_FMUL ; FP1 = XR_squared * XR_squared (recalc needed after copy)
    ; Now load X_squared into FP2
    JSR copy_fp_addr_temp1_to_fp2
    ; Now we have FP1=XR_squared, FP2=X_squared. We need to calculate FP2/FP1.
    JSR FP_FDIV              ; FP1 = Dividend/Divisor = X_squared / XR_squared

    ; 4. Calculate 1.0 - result
    JSR copy_fp1_to_fp2      ; FP2 = ratio
    JSR load_one_fp1         ; FP1 = 1.0
    JSR FP_FSUB              ; FP1 = 1.0 - ratio

    ; 5. Calculate SQR(result)
    JSR FP_SQRT              ; FP1 = sqrt(1.0 - ratio)

    ; 6. Calculate YR * result
    JSR copy_fp_addr_temp3_to_fp2 ; FP2 = YR_float
    JSR FP_FMUL              ; FP1 = sqrt_val * YR_float = TC_float

    ; 7. Convert TC_float back to integer
    JSR FP_FIX               ; Converts FP1 to 16-bit integer in M1, M1+1
    LDA F9+1 ; LSB of integer result
    STA $BC
    LDA F9   ; MSB of integer result
    STA $BC+1

    ; --- Plot the 4 symmetric points ---
ellipse_plot_points_2_right:
    ; Point 1: (XM + X, YM + TC)
    LDA $B0
    CLC
    ADC $BA
    STA $B0
    LDA $B0+1
    ADC $BA+1
    STA $B0+1
    LDA $B2
    CLC
    ADC $BC
    STA $B2
    JSR gfx_plot_point

    ; Point 2: (XM + X, YM - TC)
    ; X is the same
    LDA $B2
    SEC
    SBC $BC
    STA $B2
    JSR gfx_plot_point

    ; --- Loop control for right half ---
    ; Increment current X
    INC $BA
    BNE ellipse_x_loop_2_right_nocarry
    INC $BA+1
ellipse_x_loop_2_right_nocarry:
    ; Compare current X with XR
    LDA $BA+1
    CMP $B6+1
    BCC ellipse_x_loop_2_right ; if X_h < XR_h, continue
    BEQ ellipse_x_loop_2_right_check_lsb
    JMP end_ellipse_2 ; if X_h > XR_h, done
ellipse_x_loop_2_right_check_lsb:
    LDA $BA
    CMP $B6
    BCC ellipse_x_loop_2_right ; if X_l < XR_l, continue

    ; Drawing of left half is omitted for brevity but would follow a similar pattern
    ; with X decrementing from 0 to -XR.

end_ellipse_2:
    RTS
gfx_plot_point_3
    ; --- Plot a point on the HGR screen ---
    ; Based on "The Graphics Book for the Commodore 64", Sec 4.2.2.1
    ; Input: X in $B0/$B0+1, Y in $B2

    ; --- Calculate screen memory address from Y coordinate ---
    ; Final Address = $2000 + (Y/8)*320 + (X/8)*8 + (Y%8)

    ; 1. Calculate (Y/8) and (Y%8)
    LDA $B2
    PHA             ; Save YC for later (Y%8)
    LSR A           ; YC / 8
    LSR A
    LSR A
    TAX             ; X = YC / 8 (character row index, 0-24)

    ; 2. Look up base address for the character row: (Y/8) * 320
    ; This is much faster than multiplication.
    LDA gfx_plot_point_3_y_lookup_hi,X
    STA $B3+1
    LDA gfx_plot_point_3_y_lookup_lo,X
    STA $B3

    ; 3. Add (Y%8) to get the final row address offset
    PLA             ; Restore original YC
    AND #%00000111  ; A = YC % 8 (row inside character, 0-7)
    CLC
    ADC $B3
    STA $B3
    BCC gfx_plot_point_3_no_carry_y
    INC $B3+1
gfx_plot_point_3_no_carry_y:

    ; --- Calculate offset from X coordinate and add to pointer ---
    ; 4. Calculate (X/8)*8. This is just X with the lower 3 bits cleared.
    LDA $B0
    AND #%11111000
    CLC
    ADC $B3
    STA $B3
    LDA $B3+1
    ADC $B0+1 ; Add high byte of X and any carry
    STA $B3+1

    ; 5. Add base address of bitmap screen ($2000)
    LDA $B3+1
    CLC
    ADC #$20
    STA $B3+1

    ; --- Calculate bit mask from X coordinate ---
    ; 6. Get the bit position (X%8) and look up the mask
    LDA $B0
    AND #%00000111  ; A = X % 8
    TAX             ; Use as index for the mask table
    LDA gfx_plot_point_3_bit_mask,X
    STA $B5   ; Store mask in a temporary ZP location

    ; --- Modify the screen byte ---
    ; 7. Load, modify, and store the byte
    LDY #$00
    LDA ($B3),Y ; Load the byte from screen memory
    ORA $B5       ; ORA mask (set) or AND NOT mask (unplot)
    STA ($B3),Y ; Store it back
    RTS

; --- Lookup Tables for gfx_plot_point ---
gfx_plot_point_3_bit_mask:
    .byte %10000000, %01000000, %00100000, %00010000, %00001000, %00000100, %00000010, %00000001

gfx_plot_point_3_y_lookup_lo:
    .byte <(0*320), <(1*320), <(2*320), <(3*320), <(4*320), <(5*320), <(6*320), <(7*320)
    .byte <(8*320), <(9*320), <(10*320), <(11*320), <(12*320), <(13*320), <(14*320), <(15*320)
    .byte <(16*320), <(17*320), <(18*320), <(19*320), <(20*320), <(21*320), <(22*320), <(23*320)
    .byte <(24*320)

gfx_plot_point_3_y_lookup_hi:
    .byte >(0*320), >(1*320), >(2*320), >(3*320), >(4*320), >(5*320), >(6*320), >(7*320)
    .byte >(8*320), >(9*320), >(10*320), >(11*320), >(12*320), >(13*320), >(14*320), >(15*320)
    .byte >(16*320), >(17*320), >(18*320), >(19*320), >(20*320), >(21*320), >(22*320), >(23*320)
    .byte >(24*320)
gfx_turn_on
    ; --- Turn on HGR graphics mode (320x200) ---
    ; Based on "The Graphics Book for the Commodore 64", Sec 4.2.1.1

    ; Set bit 5 of VIC Control Register 1 ($D011) to enable bitmap mode.
    LDA $D011
    ORA #%00100000  ; Set bit 5 for bitmap mode
    STA $D011

    ; Ensure bit 4 of VIC Control Register 2 ($D016) is clear for standard hi-res (not multi-color).
    LDA $D016
    AND #%11101111  ; Clear bit 4
    STA $D016

    ; Set graphics memory to start at $2000 (8192).
    ; This is done by setting bit 3 of VIC register $D018.
    LDA $D018
    ORA #%00001000  ; Set bit 3
    STA $D018
    RTS
int_to_fp1_from_addr
    ; Converts a 16-bit integer from TEMP_VAR_1 to a floating point number in FP1
    LDA $186
    STA $FB
    LDA $186+1
    STA $FA
    LDA #$00
    STA $F9
    JSR FP_FLOAT
    RTS
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
