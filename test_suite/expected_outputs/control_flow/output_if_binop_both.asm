;--------- Start python code ---------
; x = 3
; y = 1
; res = 0
; if x * 2 == y + 5:
;   res = 1
; # Expected: 6 == 6 -> res = 1

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
    LDA #3
    STA x
    LDA #0
    STA x+1
    LDA #1
    STA y
    LDA #0
    STA y+1
    LDA #0
    STA res
    LDA #0
    STA res+1
    LDA #0
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #1
    STA res
    LDA #0
    STA res+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
