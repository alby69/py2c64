;--------- Start python code ---------
; 
; # Abilita sprite 0 e 1 (maschera 1+2=3)
; sprite_enable(3)
; 
; # Imposta la posizione dello sprite 1 a X>255
; # LSB di X = 300-256 = 44
; sprite_set_pos(1, 44, 100)
; # Imposta il bit MSB per lo sprite 1 (maschera 2)
; sprite_set_x_msb(2)
; 
; # Disabilita lo sprite 0 (maschera 1)
; sprite_disable(1)
; 
; while True: # pragma: no cover
;     pass # pragma: no cover

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
temp_0 * = * + 4
temp_1 * = * + 4
temp_2 * = * + 4
temp_3 * = * + 4
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
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #1
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #44
    STA temp_1
    LDA #0
    STA temp_1+1
    LDA #100
    STA temp_2
    LDA #0
    STA temp_2+1
    LDA #2
    STA temp_3
    LDA #0
    STA temp_3+1
    LDA #1
    STA temp_3
    LDA #0
    STA temp_3+1
    LDA #1
    STA temp_3
    LDA #0
    STA temp_3+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
sprite_disable
    ; Input: A = maschera di bit
    EOR #$FF ; Inverte i bit della maschera (0s per gli sprite da disabilitare)
    PHA      ; Salva la maschera invertita
    LDA $D015
    AND PLA  ; Applica la maschera per CANCELLARE i bit
    STA $D015
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
sprite_set_x_msb
    ; Input: A = maschera di bit degli sprite da impostare
    PHA ; Salva la maschera
    LDA $D010
    ORA PLA ; Applica la maschera per SETTARE i bit
    STA $D010
    RTS
