;--------- Start python code ---------
; 
; # Espande lo sprite 0 in Y e lo sprite 1 in X
; y_expand_mask = 1 # sprite 0
; x_expand_mask = 2 # sprite 1
; sprite_expand_xy(y_expand_mask, x_expand_mask)
; 
; # Espande lo sprite 2 sia in X che in Y usando costanti
; sprite_expand_xy(4, 4)
; 
; while True: # pragma: no cover
;     pass # pragma: no cover

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
y_expand_mask * = * + 2
x_expand_mask * = * + 2
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
    LDA #1
    STA y_expand_mask
    LDA #0
    STA y_expand_mask+1
    LDA #2
    STA x_expand_mask
    LDA #0
    STA x_expand_mask+1
    ; --- Preparazione chiamata a sprite_expand_xy ---
    LDA y_expand_mask+0
    STA temp_0+0
    LDA y_expand_mask+1
    STA temp_0+1
    LDA x_expand_mask+0
    STA temp_1+0
    LDA x_expand_mask+1
    STA temp_1+1
    LDX temp_1      ; Carica x_mask in X
    LDA temp_0      ; Carica y_mask in A
    JSR sprite_expand_xy
    ; --- Fine chiamata a sprite_expand_xy ---
    ; --- Preparazione chiamata a sprite_expand_xy ---
    LDA #4
    STA temp_1
    LDA #0
    STA temp_1+1
    LDA #4
    STA temp_0
    LDA #0
    STA temp_0+1
    LDX temp_0      ; Carica x_mask in X
    LDA temp_1      ; Carica y_mask in A
    JSR sprite_expand_xy
    ; --- Fine chiamata a sprite_expand_xy ---

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
sprite_expand_xy
    ; Input: A=maschera_Y, X=maschera_X
    ; Espansione Y
    PHA ; Salva maschera Y
    LDA $D017
    ORA PLA
    STA $D017
    ; Espansione X
    TXA ; Sposta maschera X in A
    PHA
    LDA $D01D
    ORA PLA
    STA $D01D
    RTS
