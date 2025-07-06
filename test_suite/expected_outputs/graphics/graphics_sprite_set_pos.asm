;--------- Start python code ---------
; 
; # Imposta la posizione dello sprite 0 a (150, 100) usando variabili
; sprite_num = 0
; x_pos = 150
; y_pos = 100
; sprite_set_pos(sprite_num, x_pos, y_pos)
; 
; # Imposta la posizione dello sprite 1 a (180, 120) con costanti
; sprite_set_pos(1, 180, 120)
; 
; while True: # pragma: no cover
;     pass # pragma: no cover

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
sprite_num * = * + 2
x_pos * = * + 2
y_pos * = * + 2
temp_0 * = * + 4
temp_1 * = * + 4
temp_2 * = * + 4
temp_3 * = * + 4
temp_4 * = * + 4
temp_5 * = * + 4
temp_6 * = * + 4
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
    STA sprite_num
    LDA #0
    STA sprite_num+1
    LDA #150
    STA x_pos
    LDA #0
    STA x_pos+1
    LDA #100
    STA y_pos
    LDA #0
    STA y_pos+1
    LDA sprite_num+0
    STA temp_0+0
    LDA sprite_num+1
    STA temp_0+1
    LDA x_pos+0
    STA temp_1+0
    LDA x_pos+1
    STA temp_1+1
    LDA y_pos+0
    STA temp_2+0
    LDA y_pos+1
    STA temp_2+1
    LDA #1
    STA temp_3
    LDA #0
    STA temp_3+1
    LDA #180
    STA temp_4
    LDA #0
    STA temp_4+1
    LDA #120
    STA temp_5
    LDA #0
    STA temp_5+1
    LDA #1
    STA temp_6
    LDA #0
    STA temp_6+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
sprite_set_pos
    ; Input: X=sprite_num, A=Y, $B0=X_LSB
    ; Imposta la posizione Y
    STA $D000 + 1,X
    ; Imposta la posizione X (LSB)
    LDA $B0 ; Prende la coordinata X da una locazione ZP
    STA $D000 + 0,X
    RTS
