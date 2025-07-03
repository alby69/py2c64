;--------- Start python code ---------
; 
; # Enable some sprites to check for collisions
; sprite_enable(3) # sprite 0 and 1
; sprite_set_pos(0, 100, 100)
; sprite_set_pos(1, 102, 101) # Position them to collide
; 
; # Check for sprite-sprite collision and store the result
; sprite_collisions = sprite_check_collision_sprite()
; 
; # Check for sprite-data collision and store the result
; data_collisions = sprite_check_collision_data()
; 
; while True: # pragma: no cover
;     pass # pragma: no cover

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
sprite_collisions * = * + 2
data_collisions * = * + 2
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
    ; --- Preparazione chiamata a sprite_enable ---
    LDA #3
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; Carica maschera in A
    JSR sprite_enable
    ; --- Fine chiamata a sprite_enable ---
    ; --- Preparazione chiamata a sprite_set_pos ---
    LDA #0
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #100
    STA temp_1
    LDA #0
    STA temp_1+1
    LDA #100
    STA temp_2
    LDA #0
    STA temp_2+1
    LDA temp_1      ; Carica LSB della coordinata X
    STA $B0
    LDX temp_0      ; Carica numero sprite in X
    LDA temp_2      ; Carica coordinata Y in A
    JSR sprite_set_pos
    ; --- Fine chiamata a sprite_set_pos ---
    ; --- Preparazione chiamata a sprite_set_pos ---
    LDA #1
    STA temp_3
    LDA #0
    STA temp_3+1
    LDA #102
    STA temp_4
    LDA #0
    STA temp_4+1
    LDA #101
    STA temp_5
    LDA #0
    STA temp_5+1
    LDA temp_4      ; Carica LSB della coordinata X
    STA $B0
    LDX temp_3      ; Carica numero sprite in X
    LDA temp_5      ; Carica coordinata Y in A
    JSR sprite_set_pos
    ; --- Fine chiamata a sprite_set_pos ---
    ; --- Chiamata a sprite_check_collision_sprite con assegnazione a sprite_collisions ---
    JSR sprite_check_collision_sprite
    STA sprite_collisions      ; Salva il risultato (LSB)
    LDA #0
    STA sprite_collisions+1    ; Pulisce MSB (valore a 8 bit)
    ; --- Fine chiamata ---
    ; --- Chiamata a sprite_check_collision_data con assegnazione a data_collisions ---
    JSR sprite_check_collision_data
    STA data_collisions      ; Salva il risultato (LSB)
    LDA #0
    STA data_collisions+1    ; Pulisce MSB (valore a 8 bit)
    ; --- Fine chiamata ---

while_start_0:
    LDA #1
    STA temp_6
    LDA #0
    STA temp_6+1
    LDA temp_6+1
    LDX temp_6
    ORA X
    BEQ while_end_0
    JMP while_start_0
while_end_0:
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
sprite_check_collision_data
    LDA $D01F
    RTS
sprite_check_collision_sprite
    LDA $D01E
    RTS
sprite_enable
    ; Input: A = maschera di bit
    PHA ; Salva la maschera
    LDA $D015
    ORA PLA ; Applica la maschera
    STA $D015
    RTS
sprite_set_pos
    ; Input: X=sprite_num, A=Y, $B0=X_LSB
    ; Imposta la posizione Y
    STA $D000 + 1,X
    ; Imposta la posizione X (LSB)
    LDA $B0 ; Prende la coordinata X da una locazione ZP
    STA $D000 + 0,X
    RTS
