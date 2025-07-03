;--------- Start python code ---------
; val1 = 255 # 11111111 00000000
; val2 = 85  # 01010101 00000000
; # 255 (00FF) ^ 85 (0055) = 170 (00AA)
; res_xor = val1 ^ val2

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
val1 * = * + 2
val2 * = * + 2
res_xor * = * + 2
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
    LDA #255
    STA val1
    LDA #0
    STA val1+1
    LDA #85
    STA val2
    LDA #0
    STA val2+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
