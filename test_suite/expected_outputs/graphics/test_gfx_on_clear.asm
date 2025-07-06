;--------- Start python code ---------
; 
; gfx_turn_on()
; gfx_clear_screen()
; while True: # pragma: no cover
;     pass # pragma: no cover

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
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
    LDA #1
    STA temp_0
    LDA #0
    STA temp_0+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
gfx_clear_screen
    ; --- Clear 8K HGR screen from $2000 to $3F3F ---
    ; Based on "The Graphics Book for the Commodore 64", Sec 4.2.1.2
    LDA #$00        ; Value to clear memory with
    LDX #$20        ; High byte of start address ($2000)
    STX gfx_clear_loop_1_hi_byte+1 ; Store high byte for the loop

gfx_clear_loop_1:
    LDY #$00        ; Low byte index
gfx_clear_loop_1_inner:
    STA (gfx_clear_loop_1_hi_byte),Y
    INY
    BNE gfx_clear_loop_1_inner ; Clear one 256-byte page

    INC gfx_clear_loop_1_hi_byte+1 ; Move to next page
    LDA gfx_clear_loop_1_hi_byte+1
    CMP #$40        ; Have we cleared up to $3FFF?
    BNE gfx_clear_loop_1
    RTS

gfx_clear_loop_1_hi_byte:
    .word $0000 ; Self-modifying pointer for the loop
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
