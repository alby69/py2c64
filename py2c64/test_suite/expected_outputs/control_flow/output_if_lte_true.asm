;--------- Start python code ---------
; x = 5
; y = 5
; res = 0
; if x <= y:
;   res = 1
; # Expected: res = 1

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
x * = * + 2
y * = * + 2
res * = * + 2
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
    STA x
    LDA #0
    STA x+1
    LDA #5
    STA y
    LDA #0
    STA y+1
    LDA #0
    STA res
    LDA #0
    STA res+1
    LDA temp_0+1
    LDX temp_0
    ORA X
    BEQ if_end_0
    LDA #1
    STA res
    LDA #0
    STA res+1
if_end_0:
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
