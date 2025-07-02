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
; while True:
;     pass

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
    ; --- Preparazione chiamata a draw_line ---
    LDA #160
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB
    STA $B0
    LDA temp_0+1    ; MSB
    STA $B1
    LDA #100
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB è sufficiente
    STA $B2
    LDA #240
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB
    STA $B6
    LDA temp_0+1    ; MSB
    STA $B7
    LDA #40
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB è sufficiente
    STA $B8
    JSR gfx_draw_line
    ; --- Fine chiamata a draw_line ---
    ; --- Preparazione chiamata a draw_line ---
    LDA #240
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB
    STA $B0
    LDA temp_0+1    ; MSB
    STA $B1
    LDA #40
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB è sufficiente
    STA $B2
    LDA #4
    STA temp_0
    LDA #1
    STA temp_0+1
    LDA temp_0      ; LSB
    STA $B6
    LDA temp_0+1    ; MSB
    STA $B7
    LDA #120
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB è sufficiente
    STA $B8
    JSR gfx_draw_line
    ; --- Fine chiamata a draw_line ---
    ; --- Preparazione chiamata a draw_line ---
    LDA #4
    STA temp_0
    LDA #1
    STA temp_0+1
    LDA temp_0      ; LSB
    STA $B0
    LDA temp_0+1    ; MSB
    STA $B1
    LDA #120
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB è sufficiente
    STA $B2
    LDA #160
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB
    STA $B6
    LDA temp_0+1    ; MSB
    STA $B7
    LDA #160
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB è sufficiente
    STA $B8
    JSR gfx_draw_line
    ; --- Fine chiamata a draw_line ---
    ; --- Preparazione chiamata a draw_line ---
    LDA #160
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB
    STA $B0
    LDA temp_0+1    ; MSB
    STA $B1
    LDA #160
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB è sufficiente
    STA $B2
    LDA #60
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB
    STA $B6
    LDA temp_0+1    ; MSB
    STA $B7
    LDA #120
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB è sufficiente
    STA $B8
    JSR gfx_draw_line
    ; --- Fine chiamata a draw_line ---
    ; --- Preparazione chiamata a draw_line ---
    LDA #60
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB
    STA $B0
    LDA temp_0+1    ; MSB
    STA $B1
    LDA #120
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB è sufficiente
    STA $B2
    LDA #80
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB
    STA $B6
    LDA temp_0+1    ; MSB
    STA $B7
    LDA #40
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB è sufficiente
    STA $B8
    JSR gfx_draw_line
    ; --- Fine chiamata a draw_line ---
    ; --- Preparazione chiamata a draw_line ---
    LDA #80
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB
    STA $B0
    LDA temp_0+1    ; MSB
    STA $B1
    LDA #40
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB è sufficiente
    STA $B2
    LDA #160
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB
    STA $B6
    LDA temp_0+1    ; MSB
    STA $B7
    LDA #100
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA temp_0      ; LSB è sufficiente
    STA $B8
    JSR gfx_draw_line
    ; --- Fine chiamata a draw_line ---
; Placeholder per While loop
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
gfx_draw_line_0
    ; --- Draw a line using Bresenham's algorithm ---
    ; Input: X1 in $B0/$B0+1, Y1 in $B2, X2 in $B6/$B6+1, Y2 in $B8

    ; 1. Calculate deltas (DX, DY)
    LDA $B6       ; Calculate DX
    SEC
    SBC $B0
    STA $BA
    LDA $B6+1
    SBC $B0+1
    STA $BA+1

    LDA $B8       ; Calculate DY (only 8-bit)
    SEC
    SBC $B2
    STA $BB

    ; 2. Initialize X, Y with start coordinates
    LDA $B0
    STA $BC
    LDA $B0+1
    STA $BC+1
    LDA $B2
    STA $BD

    ; 3. Determine X and Y increments (direction)
    LDA #$01          ; Default: positive increment (for X and Y)
    STA $BE
    STA $BF

    LDA $BA+1      ; Check sign of DX (MSB)
    BPL x_major_0 ; If positive or zero (bit 7 clear)
    LDA #$FF
    STA $BE     ; If negative (bit 7 set), decrement X

x_major_0        ; Determine which axis is major (X or Y). Use DX's MSB
    LDA $BA+1      ; Use MSB of DX for calculation (MSB represents sign)
    BPL y_major_0 ; If positive or zero, DX >= 0, X is major

    ; X is the major axis
    LDX #$01          ; Increment 1 for X-major
    STX $BE
    LDX #$00          ; -1
    DEX
    STX $BF

    LDA $BA+1
    BPL y_major_0
    LDA $BF
    EOR #$FF          ; Negate the value
    ADC #$01          ; Add one to complete two's complement
    STA $BF

    JMP plot_loop_0_setup

y_major_0        ; Y is the major axis, but the implementation has a Y-major bias and skips calculation of DY's MSB
    LDX #$00          ; -1
    DEX
    STX $BE
    LDX #$01          ; Increment 1
    STX $BF
    LDA $BB       ; Assuming DY is always positive in current implementation
    CMP #0
    BPL plot_loop_0_setup
    LDA $BF
    EOR #$FF          ; Negate the value
    ADC #$01          ; Add one to complete two's complement
    STA $BF

plot_loop_0_setup   ; 4. Initialize error term
    LDA $BA       ; Init error term (for X-major, DX is error; for Y-major, DY is used)
    STA $C0
    LDA $BA+1
    STA $C0+1

plot_loop_0:   ; 5. Plotting Loop
    JSR gfx_plot_point  ; Plot current point (X, Y). Assumes plot_point uses X/Y directly from $BC/$BC+1 and $BD

    ; Check if we've reached the end (check X if X-major, Y if Y-major)
    ; For now, we compare x2 to x and y2 to y, but should be dived from DY, DX
    LDA $BC
    CMP $B6
    BNE plot_loop_0_continue
    LDA $BC+1
    CMP $B6+1
    BNE plot_loop_0_continue
    LDA $BD
    CMP $B8
    BNE plot_loop_0_continue
    JMP end_plot_0 ; If Y == Y2, we're done

plot_loop_0_continue   ; Update line variables and error
    LDA $BC
    CLC
    ADC $BE     ; Conditional X increment
    STA $BC

    LDA $BD
    CLC
    ADC $BF    ; Conditional Y increment
    STA $BD

    JMP plot_loop_0  ; Continue the loop

end_plot_0:
    RTS
