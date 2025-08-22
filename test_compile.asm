*=$0801
    !byte $0c, $08, $0a, $00, $9e, $20, $28, $32, $30, $36, $31, $29, $00, $00, $00
PROGRAM_START:
; --- CODE SECTION ---
  LDA #<10
  STA TEMP_0
  LDA #10>>8
  STA TEMP_0+1
  LDA TEMP_0
  STA x
  LDA TEMP_0+1
  STA x+1
  LDA x
  STA TEMP_1
  LDA x+1
  STA TEMP_1+1
  LDA TEMP_1
  STA PRINT_VALUE
  LDA TEMP_1+1
  STA PRINT_VALUE+1
  JSR print_int16
; --- ROUTINES SECTION ---
PRINT_INT16:
  LDX #0
  LDA PRINT_VALUE+1
  BNE print_nonzero
  LDA PRINT_VALUE
  BNE print_nonzero
  LDA #'0'
  JSR $FFD2
  RTS
print_nonzero:
  LDA PRINT_VALUE+1
  PHA
  LDA PRINT_VALUE
  PHA
  JSR $BDCD
  RTS
; --- DATA SECTION ---
PRINT_VALUE:    .word 0
PRINT_BUFFER:   .res 8
RETURN_VALUE:   .word 0
TEMP_0:        .word 0
TEMP_1:        .word 0
x:        .word 0