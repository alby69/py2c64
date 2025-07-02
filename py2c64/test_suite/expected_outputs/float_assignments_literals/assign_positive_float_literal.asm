;--------- Start python code ---------
; 
; x = 3.5
; y = -0.25
; z = 0.0
; # Verification of byte patterns for x, y, z in the .asm data section
; # would be done by inspecting the generated expected_outputs/float_assignments_literals/assign_positive_float_literal.asm

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
x * = * + 2
y * = * + 2
z * = * + 2
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
    STA x+0
    LDA #$00
    STA x+1
    LDA #$70
    STA x+2
    LDA #$82
    STA x+3
    LDA #$00
    STA z+0
    LDA #$00
    STA z+1
    LDA #$00
    STA z+2
    LDA #$00
    STA z+3
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
