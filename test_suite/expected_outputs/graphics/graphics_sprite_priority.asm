;--------- Start python code ---------
; 
; # Set sprite 0 to be behind background graphics (mask=1)
; sprite_set_priority(1)
; 
; # Set sprite 3 to be behind background using a variable
; prio_mask = 8 # bit 3
; sprite_set_priority(prio_mask)
; 
; while True: # pragma: no cover
;     pass # pragma: no cover

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
prio_mask * = * + 2
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
    ; --- Preparazione chiamata a sprite_set_priority ---
    LDA #1
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; Carica maschera in A
    JSR sprite_set_priority
    ; --- Fine chiamata a sprite_set_priority ---
    LDA #8
    STA prio_mask
    LDA #0
    STA prio_mask+1
    ; --- Preparazione chiamata a sprite_set_priority ---
    LDA prio_mask
    STA temp_0
    LDA prio_mask+1
    STA temp_0+1
    LDA temp_0      ; Carica maschera in A
    JSR sprite_set_priority
    ; --- Fine chiamata a sprite_set_priority ---

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
sprite_set_priority
    ; Input: A = maschera di bit (1=dietro, 0=davanti)
    PHA
    LDA $D01B
    ORA PLA
    STA $D01B
    RTS
