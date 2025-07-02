;--------- Start python code ---------
; 
; # Abilita sprite 0 e 2 (maschera 1+4=5)
; sprite_enable(5)
; 
; # Imposta il colore dello sprite 0 a blu (6)
; sprite_num = 0
; color_code = 6
; sprite_set_color(sprite_num, color_code)
; 
; # Imposta il colore dello sprite 2 a giallo (7) con costanti
; sprite_set_color(2, 7)
; 
; while True: # pragma: no cover
;     pass # pragma: no cover

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
sprite_num * = * + 2
color_code * = * + 2
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
    ; --- Preparazione chiamata a sprite_enable ---
    LDA #5
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; Carica maschera in A
    JSR sprite_enable
    ; --- Fine chiamata a sprite_enable ---
    LDA #0
    STA sprite_num
    LDA #0
    STA sprite_num+1
    LDA #6
    STA color_code
    LDA #0
    STA color_code+1
    ; --- Preparazione chiamata a sprite_set_color ---
    LDA sprite_num
    STA temp_0
    LDA sprite_num+1
    STA temp_0+1
    LDA color_code+0
    STA temp_1+0
    LDA color_code+1
    STA temp_1+1
    LDX temp_0      ; Carica numero sprite in X
    LDA temp_1      ; Carica colore in A
    JSR sprite_set_color
    ; --- Fine chiamata a sprite_set_color ---
    ; --- Preparazione chiamata a sprite_set_color ---
    LDA #2
    STA temp_1
    LDA #0
    STA temp_1+1
    LDA #7
    STA temp_0
    LDA #0
    STA temp_0+1
    LDX temp_1      ; Carica numero sprite in X
    LDA temp_0      ; Carica colore in A
    JSR sprite_set_color
    ; --- Fine chiamata a sprite_set_color ---

while_start_0:
    LDA #1
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0+1
    LDX temp_0
    ORA X
    BEQ while_end_0
    JMP while_start_0
while_end_0:
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
sprite_enable
    ; Input: A = maschera di bit
    PHA ; Salva la maschera
    LDA $D015
    ORA PLA ; Applica la maschera
    STA $D015
    RTS
sprite_set_color
    ; Input: X=sprite_num, A=colore
    STA $D027,X
    RTS
