;--------- Start python code ---------
; 
; gfx_turn_on()
; gfx_turn_off()

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
exception_handler_active_flag * = * + 2
current_exception_target_label_ptr * = * + 2
last_exception_type_code * = * + 1

main_program_entry_point:
; --- Code Section ---
    LDA #<02FF
    STA $E0
    LDA #>02FF
    STA $E1
    JSR gfx_turn_on
    JSR gfx_turn_off
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
gfx_turn_off
    ; --- Turn off HGR graphics mode ---
    ; Based on "The Graphics Book for the Commodore 64", Sec 4.2.1.4

    ; Clear bit 5 of VIC Control Register 1 ($D011) to disable bitmap mode.
    LDA $D011
    AND #%11011111  ; Clear bit 5
    STA $D011

    ; Point character set back to default location.
    ; This is done by clearing bit 3 of VIC register $D018.
    LDA $D018
    AND #%11110111  ; Clear bit 3
    STA $D018
    RTS
gfx_turn_on
    ; --- Turn on HGR graphics mode (320x200) ---
    ; Based on "The Graphics Book for the Commodore 64", Sec 4.2.1.1

    ; Set bit 5 of VIC Control Register 1 ($D011) to enable bitmap mode.
    LDA $D011
    ORA #%00100000  ; Set bit 5 for bitmap mode
    STA $D011

    ; Ensure bit 4 of VIC Control Register 2 ($D016) is clear for standard hi-res (not multi-color).
    LDA $D016
    AND #%11101111  ; Clear bit 4
    STA $D016

    ; Set graphics memory to start at $2000 (8192).
    ; This is done by setting bit 3 of VIC register $D018.
    LDA $D018
    ORA #%00001000  ; Set bit 3
    STA $D018
    RTS
