;--------- Start python code ---------
; 
; # Set multicolor colors using variables
; mc1 = 1 # black
; mc2 = 7 # yellow
; sprite_set_multicolor_colors(mc1, mc2)
; 
; # Set multicolor colors using constants
; sprite_set_multicolor_colors(2, 11) # red, light cyan
; 
; while True: # pragma: no cover
;     pass # pragma: no cover

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
mc1 * = * + 2
mc2 * = * + 2
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
    STA mc1
    LDA #0
    STA mc1+1
    LDA #7
    STA mc2
    LDA #0
    STA mc2+1
    LDA mc1+0
    STA temp_0+0
    LDA mc1+1
    STA temp_0+1
    LDA mc2+0
    STA temp_1+0
    LDA mc2+1
    STA temp_1+1
    LDA #2
    STA temp_1
    LDA #0
    STA temp_1+1
    LDA #11
    STA temp_0
    LDA #0
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
sprite_set_multicolor_colors
    STA $D025 ; Imposta colore multicolor 1
    STX $D026 ; Imposta colore multicolor 2
    RTS
