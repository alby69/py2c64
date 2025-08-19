; === DATA SECTION ===
LIST_ROUTINE_ARG1: .word 0
LIST_ROUTINE_ARG2: .word 0
LIST_ROUTINE_RET1: .word 0
RETURN_VALUE:   .word 0
FRAME_POINTER:  .byte 0
HEAP_POINTER:   .word $C000 ; Start of heap memory for dynamic allocation
TEMP_0:        .word 0
TEMP_1:        .word 0
TEMP_2:        .word 0
TEMP_3:        .word 0
TEMP_4:        .word 0
TEMP_5:        .word 0
TEMP_6:        .word 0
TEMP_7:        .word 0
TEMP_8:        .word 0
my_list:        .word 0
val:        .word 0

; === CODE SECTION ===
; py2c64 - Generated 6502 Assembly
; Target: Commodore 64

    LDA HEAP_POINTER
    STA TEMP_0
    LDA HEAP_POINTER+1
    STA TEMP_0+1
    LDY #0
    LDA #3
    STA (TEMP_0),Y
    LDA #<10
    STA TEMP_1
    LDA #10>>8
    STA TEMP_1+1
    LDA TEMP_1
    LDY #1
    STA (TEMP_0),Y
    LDA TEMP_1+1
    INY
    STA (TEMP_0),Y
    LDA #<20
    STA TEMP_2
    LDA #20>>8
    STA TEMP_2+1
    LDA TEMP_2
    LDY #3
    STA (TEMP_0),Y
    LDA TEMP_2+1
    INY
    STA (TEMP_0),Y
    LDA #<30
    STA TEMP_3
    LDA #30>>8
    STA TEMP_3+1
    LDA TEMP_3
    LDY #5
    STA (TEMP_0),Y
    LDA TEMP_3+1
    INY
    STA (TEMP_0),Y
    LDA #<7
    STA TEMP_4
    LDA #7>>8
    STA TEMP_4+1
    CLC
    LDA HEAP_POINTER
    ADC TEMP_4
    STA HEAP_POINTER
    LDA HEAP_POINTER+1
    ADC TEMP_4+1
    STA HEAP_POINTER+1
    LDA TEMP_0
    STA my_list
    LDA TEMP_0+1
    STA my_list+1
    LDA my_list
    STA TEMP_5
    LDA my_list+1
    STA TEMP_5+1
    LDA #<1
    STA TEMP_6
    LDA #1>>8
    STA TEMP_6+1
    LDA TEMP_5
    STA LIST_ROUTINE_ARG1
    LDA TEMP_5+1
    STA LIST_ROUTINE_ARG1+1
    LDA TEMP_6
    STA LIST_ROUTINE_ARG2
    LDA TEMP_6+1
    STA LIST_ROUTINE_ARG2+1
    JSR GET_LIST_ELEMENT
    LDA LIST_ROUTINE_RET1
    STA TEMP_7
    LDA LIST_ROUTINE_RET1+1
    STA TEMP_7+1
    LDA TEMP_7
    STA val
    LDA TEMP_7+1
    STA val+1
    LDA val
    STA TEMP_8
    LDA val+1
    STA TEMP_8+1
    LDA TEMP_8
    STA PRINT_VALUE
    LDA TEMP_8+1
    STA PRINT_VALUE+1
    JSR PRINT_INT16

; === ROUTINES SECTION ===
; Routine to get an element from a list
; Input:
;   LIST_ROUTINE_ARG1: 16-bit pointer to the list
;   LIST_ROUTINE_ARG2: 16-bit index
; Output:
;   LIST_ROUTINE_RET1: 16-bit value of the element
GET_LIST_ELEMENT:
; 1. Calculate offset = index * 2
    LDA LIST_ROUTINE_ARG2
    ASL A
    STA $FB
    LDA LIST_ROUTINE_ARG2+1
    ROL A
    STA $FC
; 2. Add 1 to offset to get past the length byte
    CLC
    LDA $FB
    ADC #1
    STA $FB
    BCC GET_ELEM_NO_CARRY
    INC $FC
GET_ELEM_NO_CARRY:
; 3. Calculate final address = base_ptr + offset
    CLC
    LDA LIST_ROUTINE_ARG1
    ADC $FB
    STA $FD
    LDA LIST_ROUTINE_ARG1+1
    ADC $FC
    STA $FE
; 4. Dereference pointer to get the value
    LDY #0
    LDA ($FD),Y
    STA LIST_ROUTINE_RET1
    INY
    LDA ($FD),Y
    STA LIST_ROUTINE_RET1+1
    RTS
