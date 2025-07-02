;--------- Start python code ---------
; 
; int_val = 5
; float_val = 4.99
; is_greater = int_val > float_val

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
int_val * = * + 2
float_val * = * + 2
is_greater * = * + 2
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
    STA int_val
    LDA #0
    STA int_val+1
    LDA #$00
    STA float_val+0
    LDA #$00
    STA float_val+1
    LDA #$00
    STA float_val+2
    LDA #$00
    STA float_val+3
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
