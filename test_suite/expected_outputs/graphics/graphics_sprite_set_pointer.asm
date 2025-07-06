;--------- Start python code ---------
; 
; # Set pointer for sprite 0 to point to data block at $3000 (pointer value $C0 = 192)
; sprite_set_pointer(0, 192)
; 
; # Set pointer for sprite 1 using variables
; s_num = 1
; ptr_val = 193 # for data at $3040
; sprite_set_pointer(s_num, ptr_val)
; 
; while True: # pragma: no cover
;     pass # pragma: no cover

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
s_num * = * + 2
ptr_val * = * + 2
temp_0 * = * + 4
temp_1 * = * + 4
exception_handler_active_flag * = * + 2
current_exception_target_label_ptr * = * + 2
last_exception_type_code * = * + 1

main_program_entry_point:
; --- Code Section ---
    LDA #<02FF
    STA $E0
    LDA #>02FF
    STA $E1
    LDA #0
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #192
    STA temp_1
    LDA #0
    STA temp_1+1
    LDA #1
    STA s_num
    LDA #0
    STA s_num+1
    LDA #193
    STA ptr_val
    LDA #0
    STA ptr_val+1
    LDA s_num
    STA temp_1
    LDA s_num+1
    STA temp_1+1
    LDA ptr_val
    STA temp_0
    LDA ptr_val+1
    STA temp_0+1
    LDA #1
    STA temp_0
    LDA #0
    STA temp_0+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
sprite_set_pointer
    ; Input: X=sprite_num, A=valore puntatore
    STA 2040,X
    RTS
