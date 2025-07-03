;--------- Start python code ---------
; 
; # Set sprite 1 to multicolor mode using a constant
; sprite_set_multicolor(2) # mask for sprite 1 is bit 1 = 2
; 
; # Set sprite 2 to multicolor mode using a variable
; mc_mask = 4 # mask for sprite 2 is bit 2 = 4
; sprite_set_multicolor(mc_mask)
; 
; while True: # pragma: no cover
;     pass # pragma: no cover

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
mc_mask * = * + 2
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
    ; --- Preparazione chiamata a sprite_set_multicolor ---
    LDA #2
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; Carica maschera in A
    JSR sprite_set_multicolor
    ; --- Fine chiamata a sprite_set_multicolor ---
    LDA #4
    STA mc_mask
    LDA #0
    STA mc_mask+1
    ; --- Preparazione chiamata a sprite_set_multicolor ---
    LDA mc_mask
    STA temp_0
    LDA mc_mask+1
    STA temp_0+1
    LDA temp_0      ; Carica maschera in A
    JSR sprite_set_multicolor
    ; --- Fine chiamata a sprite_set_multicolor ---

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
sprite_set_multicolor
    ; Input: A = maschera di bit
    PHA
    LDA $D01C
    ORA PLA
    STA $D01C
    RTS
