;--------- Start python code ---------
; a = 10 # 00001010
; b = 5  # 00000101
; c = a ^ b # Expected result: 15 (00001111)

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
a * = * + 2
b * = * + 2
c * = * + 2
temp_0 * = * + 2
exception_handler_active_flag * = * + 2
current_exception_target_label_ptr * = * + 2
last_exception_type_code * = * + 1

main_program_entry_point:
; --- Code Section ---
    LDA #<02FF
    STA $E0
    LDA #>02FF
    STA $E1
    LDA #10
    STA a
    LDA #0
    STA a+1
    LDA #5
    STA b
    LDA #0
    STA b+1
    LDA a
    EOR b
    STA c
    LDA a+1
    EOR b+1
    STA c+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
