;--------- Start python code ---------
; 
; gfx_turn_on()
; gfx_clear_screen()
; 
; # Draw the lines that form the star
; draw_line(160, 100, 240, 40)
; draw_line(240, 40, 260, 120)
; draw_line(260, 120, 160, 160)
; draw_line(160, 160, 60, 120)
; draw_line(60, 120, 80, 40)
; draw_line(80, 40, 160, 100)
; 
; # Loop forever to keep the image on screen
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
    LDA #160
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #100
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #240
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #40
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #240
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #40
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #4
    STA temp_0
    LDA #1
    STA temp_0+1
    LDA #120
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #4
    STA temp_0
    LDA #1
    STA temp_0+1
    LDA #120
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #160
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #160
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #160
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #160
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #60
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #120
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #60
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #120
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #80
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #40
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #80
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #40
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #160
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #100
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
gfx_draw_line_2
    ; --- Draw a line using Bresenham's algorithm ---
    ; Input: X1($B0), Y1($B2), X2($B6), Y2($B8)

    ; --- Setup Phase ---
    ; 1. Calculate dx = x2 - x1 and dy = y2 - y1
    LDA $B6
    SEC
    SBC $B0
    STA $BF
    LDA $B6+1
    SBC $B0+1
    STA $BF+1

    LDA $B8
    SEC
    SBC $B2
    STA $C1

    ; 2. Determine step directions (sx, sy) and get absolute values of dx, dy
    LDA $BF+1       ; Check sign of dx
    BPL dx_pos_2
dx_neg_2:
    LDA #$FF            ; sx = -1
    STA $C2
    ; Negate dx (2's complement) to get abs(dx)
    LDA $BF
    EOR #$FF
    STA $BF
    LDA $BF+1
    EOR #$FF
    STA $BF+1
    INC $BF
    BNE dy_pos_2
    INC $BF+1
    JMP dy_pos_2
dx_pos_2:
    LDA #$01            ; sx = 1
    STA $C2

dy_pos_2:
    LDA $C1         ; Check sign of dy
    BPL dy_neg_2
    LDA #$FF            ; sy = -1
    STA $C3
    LDA $C1         ; Negate dy to get abs(dy)
    EOR #$FF
    CLC
    ADC #$01
    STA $C1
    JMP plot_loop_2
dy_neg_2:
    LDA #$01            ; sy = 1
    STA $C3

    ; 3. Initialize current coordinates and error term
plot_loop_2:
    LDA $B0         ; current_x = x1
    STA $BC
    LDA $B0+1
    STA $BC+1
    LDA $B2         ; current_y = y1
    STA $BE

    LDA $BF         ; err = dx - dy
    SEC
    SBC $C1
    STA $C4
    LDA $BF+1       ; No high byte for dy, so just subtract borrow
    SBC #$00
    STA $C4+1

    ; --- Main Plotting Loop ---
plot_loop_2_main:
    ; Plot current point. Must copy current coords to plot_point's ZP inputs.
    LDA $BC
    STA $B0
    LDA $BC+1
    STA $B0+1
    LDA $BE
    STA $B2
    JSR gfx_plot_point

    ; Check if we've reached the end point
    LDA $BC
    CMP $B6
    BNE plot_loop_2_continue_check
    LDA $BC+1
    CMP $B6+1
    BNE plot_loop_2_continue_check
    LDA $BE
    CMP $B8
    BEQ end_plot_2 ; If all match, we are done

plot_loop_2_continue_check:
    ; Calculate e2 = 2 * err
    ASL $C4
    ROL $C4+1
    LDA $C4
    STA $C6
    LDA $C4+1
    STA $C6+1

    ; if (e2 > -dy)
    LDA $C1         ; Get -dy
    EOR #$FF
    CLC
    ADC #$01
    SEC
    SBC $C6         ; Compare by subtracting: (-dy) - e2
    LDA #$00
    SBC $C6+1       ; High byte comparison
    BPL update_y_2 ; If result is positive or zero, e2 <= -dy, so skip x update
update_x_2:
    LDA $C4        ; err -= dy
    SEC
    SBC $C1
    STA $C4
    LDA $C4+1
    SBC #$00
    STA $C4+1
    LDA $BC  ; x += sx
    CLC
    ADC $C2
    STA $BC
    BCC update_y_2
    INC $BC+1

update_y_2:
    ; if (e2 < dx)
    LDA $C6
    SEC
    SBC $BF
    LDA $C6+1
    SBC $BF+1
    BCS plot_loop_2_main ; If result has no borrow, e2 >= dx, so skip y update

    LDA $C4        ; err += dx
    CLC
    ADC $BF
    STA $C4
    LDA $C4+1
    ADC $BF+1
    STA $C4+1
    LDA $BE  ; y += sy
    CLC
    ADC $C3
    STA $BE

    JMP plot_loop_2_main

end_plot_2:
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
