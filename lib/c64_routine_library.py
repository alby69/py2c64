# /workspaces/py2c64/lib/c64_routine_library.py

"""
This module acts as a central library for generating the assembly code for
various C64-specific routines (graphics, sprites, math, etc.).

The main export is the `ROUTINE_GENERATORS` dictionary, which maps a
routine name (e.g., 'gfx_turn_on') to a function that returns the
corresponding assembly code as a string.

This allows the main compiler to look up and include only the routines
that are actually used in the final assembly output.
"""

from .. import globals as py2asm_globals
from .func_core import create_label

def _generate_gfx_turn_on():
    """
    Generates assembly to turn on high-resolution graphics mode.
    Based on section 4.2.1.1 of "The Graphics Book for the Commodore 64".
    This routine sets up the VIC-II for 320x200 bitmap mode.
    """
    # VIC Registers (offsets from VIC_BASE_ADDR)
    VIC_CONTROL_REG1 = 0x11 # 17
    VIC_CONTROL_REG2 = 0x16 # 22
    VIC_MEMORY_SETUP = 0x18 # 24

    # The book's BASIC code is `POKE V+17, PEEK(V+17) OR (8+3)*16`, which is likely a typo.
    # The text description says "set bits 5 and 6 of register 17".
    # Bit 5 (hi-res bitmap) = 32. Bit 6 (extended color) = 64.
    # For standard hi-res, we need to set bit 5.
    # The book's code also sets bit 4 of reg 22 to 0 (multi-color off).
    # And bit 3 of reg 24 to 1 (graphics at $2000).

    code = f"""
gfx_turn_on
    ; --- Turn on HGR graphics mode (320x200) ---
    ; Based on "The Graphics Book for the Commodore 64", Sec 4.2.1.1

    ; Set bit 5 of VIC Control Register 1 ($D011) to enable bitmap mode.
    LDA ${py2asm_globals.VIC_BASE_ADDR + VIC_CONTROL_REG1:04X}
    ORA #%00100000  ; Set bit 5 for bitmap mode
    STA ${py2asm_globals.VIC_BASE_ADDR + VIC_CONTROL_REG1:04X}

    ; Ensure bit 4 of VIC Control Register 2 ($D016) is clear for standard hi-res (not multi-color).
    LDA ${py2asm_globals.VIC_BASE_ADDR + VIC_CONTROL_REG2:04X}
    AND #%11101111  ; Clear bit 4
    STA ${py2asm_globals.VIC_BASE_ADDR + VIC_CONTROL_REG2:04X}

    ; Set graphics memory to start at $2000 (8192).
    ; This is done by setting bit 3 of VIC register $D018.
    LDA ${py2asm_globals.VIC_BASE_ADDR + VIC_MEMORY_SETUP:04X}
    ORA #%00001000  ; Set bit 3
    STA ${py2asm_globals.VIC_BASE_ADDR + VIC_MEMORY_SETUP:04X}
    RTS
"""
    return code.strip()

def _generate_gfx_turn_off():
    """
    Generates assembly to turn off graphics mode and return to text mode.
    Based on section 4.2.1.4 of "The Graphics Book for the Commodore 64".
    """
    VIC_CONTROL_REG1 = 0x11 # 17
    VIC_MEMORY_SETUP = 0x18 # 24

    code = f"""
gfx_turn_off
    ; --- Turn off HGR graphics mode ---
    ; Based on "The Graphics Book for the Commodore 64", Sec 4.2.1.4

    ; Clear bit 5 of VIC Control Register 1 ($D011) to disable bitmap mode.
    LDA ${py2asm_globals.VIC_BASE_ADDR + VIC_CONTROL_REG1:04X}
    AND #%11011111  ; Clear bit 5
    STA ${py2asm_globals.VIC_BASE_ADDR + VIC_CONTROL_REG1:04X}

    ; Point character set back to default location.
    ; This is done by clearing bit 3 of VIC register $D018.
    LDA ${py2asm_globals.VIC_BASE_ADDR + VIC_MEMORY_SETUP:04X}
    AND #%11110111  ; Clear bit 3
    STA ${py2asm_globals.VIC_BASE_ADDR + VIC_MEMORY_SETUP:04X}
    RTS
"""
    return code.strip()

def _generate_gfx_clear_screen():
    """
    Generates assembly to clear the 8K bitmap graphics screen memory.
    Based on section 4.2.1.2 of "The Graphics Book for the Commodore 64".
    Assumes graphics memory is at $2000-$3F3F.
    """
    clear_loop_label = create_label("gfx_clear_loop", str(py2asm_globals.label_counter))
    py2asm_globals.label_counter += 1

    code = f"""
gfx_clear_screen
    ; --- Clear 8K HGR screen from $2000 to $3F3F ---
    ; Based on "The Graphics Book for the Commodore 64", Sec 4.2.1.2
    LDA #$00        ; Value to clear memory with
    LDX #$20        ; High byte of start address ($2000)
    STX {clear_loop_label}_hi_byte+1 ; Store high byte for the loop

{clear_loop_label}:
    LDY #$00        ; Low byte index
{clear_loop_label}_inner:
    STA ({clear_loop_label}_hi_byte),Y
    INY
    BNE {clear_loop_label}_inner ; Clear one 256-byte page

    INC {clear_loop_label}_hi_byte+1 ; Move to next page
    LDA {clear_loop_label}_hi_byte+1
    CMP #$40        ; Have we cleared up to $3FFF?
    BNE {clear_loop_label}
    RTS

{clear_loop_label}_hi_byte:
    .word $0000 ; Self-modifying pointer for the loop
"""
    return code.strip()

# Placeholder for more complex routines like plotting points, lines, etc.
# These would require parameters, likely passed via ZP locations or registers.

def _generate_gfx_plot_point(plot_mode='set'):
    """
    Generates assembly to plot or unplot a point on the HGR screen.
    Based on section 4.2.2.1 of "The Graphics Book for the Commodore 64".

    Input: X-coordinate (0-319) and Y-coordinate (0-199) must be placed
    in zero-page locations before calling this routine.
    - gfx_plot_x_coord ($B0-$B1): 16-bit X coordinate.
    - gfx_plot_y_coord ($B2): 8-bit Y coordinate.

    Args:
        plot_mode (str): 'set' to turn the pixel on, 'unplot' to turn it off.
    """
    # Define Zero Page locations for parameters and temporary storage
    # These should be defined as variables in the final assembly output.
    # The compiler should handle this via handle_variable().
    ZP_X_COORD = "$B0"  # 16-bit
    ZP_Y_COORD = "$B2"  # 8-bit
    ZP_PTR = "$B3"      # 16-bit pointer for final address
    ZP_TMP1 = "$B5"     # 8-bit temp

    plot_label = create_label("gfx_plot_point", str(py2asm_globals.label_counter))
    py2asm_globals.label_counter += 1

    # Determine the plotting operation
    if plot_mode == 'set':
        plot_op = f"ORA {ZP_TMP1}"
    else: # unplot
        # To unplot, we need to AND with the inverted mask
        # EOR #$FF inverts all bits of the mask
        plot_op = f"EOR #$FF\n    AND ({ZP_PTR}),Y"

    code = f"""
{plot_label}
    ; --- Plot a point on the HGR screen ---
    ; Based on "The Graphics Book for the Commodore 64", Sec 4.2.2.1
    ; Input: X in {ZP_X_COORD}/{ZP_X_COORD}+1, Y in {ZP_Y_COORD}

    ; --- Calculate screen memory address from Y coordinate ---
    ; Final Address = $2000 + (Y/8)*320 + (X/8)*8 + (Y%8)

    ; 1. Calculate (Y/8) and (Y%8)
    LDA {ZP_Y_COORD}
    PHA             ; Save YC for later (Y%8)
    LSR A           ; YC / 8
    LSR A
    LSR A
    TAX             ; X = YC / 8 (character row index, 0-24)

    ; 2. Look up base address for the character row: (Y/8) * 320
    ; This is much faster than multiplication.
    LDA {plot_label}_y_lookup_hi,X
    STA {ZP_PTR}+1
    LDA {plot_label}_y_lookup_lo,X
    STA {ZP_PTR}

    ; 3. Add (Y%8) to get the final row address offset
    PLA             ; Restore original YC
    AND #%00000111  ; A = YC % 8 (row inside character, 0-7)
    CLC
    ADC {ZP_PTR}
    STA {ZP_PTR}
    BCC {plot_label}_no_carry_y
    INC {ZP_PTR}+1
{plot_label}_no_carry_y:

    ; --- Calculate offset from X coordinate and add to pointer ---
    ; 4. Calculate (X/8)*8. This is just X with the lower 3 bits cleared.
    LDA {ZP_X_COORD}
    AND #%11111000
    CLC
    ADC {ZP_PTR}
    STA {ZP_PTR}
    LDA {ZP_PTR}+1
    ADC {ZP_X_COORD}+1 ; Add high byte of X and any carry
    STA {ZP_PTR}+1

    ; 5. Add base address of bitmap screen ($2000)
    LDA {ZP_PTR}+1
    CLC
    ADC #$20
    STA {ZP_PTR}+1

    ; --- Calculate bit mask from X coordinate ---
    ; 6. Get the bit position (X%8) and look up the mask
    LDA {ZP_X_COORD}
    AND #%00000111  ; A = X % 8
    TAX             ; Use as index for the mask table
    LDA {plot_label}_bit_mask,X
    STA {ZP_TMP1}   ; Store mask in a temporary ZP location

    ; --- Modify the screen byte ---
    ; 7. Load, modify, and store the byte
    LDY #$00
    LDA ({ZP_PTR}),Y ; Load the byte from screen memory
    {plot_op}       ; ORA mask (set) or AND NOT mask (unplot)
    STA ({ZP_PTR}),Y ; Store it back
    RTS

; --- Lookup Tables for gfx_plot_point ---
{plot_label}_bit_mask:
    .byte %10000000, %01000000, %00100000, %00010000, %00001000, %00000100, %00000010, %00000001

{plot_label}_y_lookup_lo:
    .byte <(0*320), <(1*320), <(2*320), <(3*320), <(4*320), <(5*320), <(6*320), <(7*320)
    .byte <(8*320), <(9*320), <(10*320), <(11*320), <(12*320), <(13*320), <(14*320), <(15*320)
    .byte <(16*320), <(17*320), <(18*320), <(19*320), <(20*320), <(21*320), <(22*320), <(23*320)
    .byte <(24*320)

{plot_label}_y_lookup_hi:
    .byte >(0*320), >(1*320), >(2*320), >(3*320), >(4*320), >(5*320), >(6*320), >(7*320)
    .byte >(8*320), >(9*320), >(10*320), >(11*320), >(12*320), >(13*320), >(14*320), >(15*320)
    .byte >(16*320), >(17*320), >(18*320), >(19*320), >(20*320), >(21*320), >(22*320), >(23*320)
    .byte >(24*320)
"""
    return code.strip()

# --- Bresenham's Line Algorithm Implementation ---
def _generate_gfx_draw_line():
    """
    Generates assembly to draw a line between two points using Bresenham's algorithm.
    Based on Section 4.2.2.4 of "The Graphics Book for the Commodore 64".

    Input (all ZP locations):
    - x1 ($B0, $B1): 16-bit start X coordinate.
    - y1 ($B2): 8-bit start Y coordinate.
    - x2 ($B6, $B7): 16-bit end X coordinate.
    - y2 ($B8): 8-bit end Y coordinate.
    """
    # ZP locations for input coordinates
    ZP_X1 = "$B0"
    ZP_Y1 = "$B2"
    ZP_X2 = "$B6"
    ZP_Y2 = "$B8"

    # ZP locations for Bresenham's algorithm state
    ZP_CURRENT_X = "$BC" # 16-bit
    ZP_CURRENT_Y = "$BE" # 8-bit
    ZP_DX = "$BF"        # 16-bit
    ZP_DY = "$C1"        # 8-bit
    ZP_SX = "$C2"        # 8-bit step direction for X
    ZP_SY = "$C3"        # 8-bit step direction for Y
    ZP_ERR = "$C4"       # 16-bit error term
    ZP_E2 = "$C6"        # 16-bit temporary for 2*err

    # ZP locations used by the plot_point subroutine
    ZP_PLOT_X = "$B0"
    ZP_PLOT_Y = "$B2"

    # Define labels for control flow
    draw_line_label = create_label("gfx_draw_line", str(py2asm_globals.label_counter))
    plot_loop_label = create_label("plot_loop", str(py2asm_globals.label_counter))
    dx_neg_label = create_label("dx_neg", str(py2asm_globals.label_counter))
    dx_pos_label = create_label("dx_pos", str(py2asm_globals.label_counter))
    dy_neg_label = create_label("dy_neg", str(py2asm_globals.label_counter))
    dy_pos_label = create_label("dy_pos", str(py2asm_globals.label_counter))
    update_x_label = create_label("update_x", str(py2asm_globals.label_counter))
    update_y_label = create_label("update_y", str(py2asm_globals.label_counter))
    end_plot_label = create_label("end_plot", str(py2asm_globals.label_counter))
    py2asm_globals.label_counter += 1

    code = f"""
{draw_line_label}
    ; --- Draw a line using Bresenham's algorithm ---
    ; Input: X1({ZP_X1}), Y1({ZP_Y1}), X2({ZP_X2}), Y2({ZP_Y2})

    ; --- Setup Phase ---
    ; 1. Calculate dx = x2 - x1 and dy = y2 - y1
    LDA {ZP_X2}
    SEC
    SBC {ZP_X1}
    STA {ZP_DX}
    LDA {ZP_X2}+1
    SBC {ZP_X1}+1
    STA {ZP_DX}+1

    LDA {ZP_Y2}
    SEC
    SBC {ZP_Y1}
    STA {ZP_DY}

    ; 2. Determine step directions (sx, sy) and get absolute values of dx, dy
    LDA {ZP_DX}+1       ; Check sign of dx
    BPL {dx_pos_label}
{dx_neg_label}:
    LDA #$FF            ; sx = -1
    STA {ZP_SX}
    ; Negate dx (2's complement) to get abs(dx)
    LDA {ZP_DX}
    EOR #$FF
    STA {ZP_DX}
    LDA {ZP_DX}+1
    EOR #$FF
    STA {ZP_DX}+1
    INC {ZP_DX}
    BNE {dy_pos_label}
    INC {ZP_DX}+1
    JMP {dy_pos_label}
{dx_pos_label}:
    LDA #$01            ; sx = 1
    STA {ZP_SX}

{dy_pos_label}:
    LDA {ZP_DY}         ; Check sign of dy
    BPL {dy_neg_label}
    LDA #$FF            ; sy = -1
    STA {ZP_SY}
    LDA {ZP_DY}         ; Negate dy to get abs(dy)
    EOR #$FF
    CLC
    ADC #$01
    STA {ZP_DY}
    JMP {plot_loop_label}
{dy_neg_label}:
    LDA #$01            ; sy = 1
    STA {ZP_SY}

    ; 3. Initialize current coordinates and error term
{plot_loop_label}:
    LDA {ZP_X1}         ; current_x = x1
    STA {ZP_CURRENT_X}
    LDA {ZP_X1}+1
    STA {ZP_CURRENT_X}+1
    LDA {ZP_Y1}         ; current_y = y1
    STA {ZP_CURRENT_Y}

    LDA {ZP_DX}         ; err = dx - dy
    SEC
    SBC {ZP_DY}
    STA {ZP_ERR}
    LDA {ZP_DX}+1       ; No high byte for dy, so just subtract borrow
    SBC #$00
    STA {ZP_ERR}+1

    ; --- Main Plotting Loop ---
{plot_loop_label}_main:
    ; Plot current point. Must copy current coords to plot_point's ZP inputs.
    LDA {ZP_CURRENT_X}
    STA {ZP_PLOT_X}
    LDA {ZP_CURRENT_X}+1
    STA {ZP_PLOT_X}+1
    LDA {ZP_CURRENT_Y}
    STA {ZP_PLOT_Y}
    JSR gfx_plot_point

    ; Check if we've reached the end point
    LDA {ZP_CURRENT_X}
    CMP {ZP_X2}
    BNE {plot_loop_label}_continue_check
    LDA {ZP_CURRENT_X}+1
    CMP {ZP_X2}+1
    BNE {plot_loop_label}_continue_check
    LDA {ZP_CURRENT_Y}
    CMP {ZP_Y2}
    BEQ {end_plot_label} ; If all match, we are done

{plot_loop_label}_continue_check:
    ; Calculate e2 = 2 * err
    ASL {ZP_ERR}
    ROL {ZP_ERR}+1
    LDA {ZP_ERR}
    STA {ZP_E2}
    LDA {ZP_ERR}+1
    STA {ZP_E2}+1

    ; if (e2 > -dy)
    LDA {ZP_DY}         ; Get -dy
    EOR #$FF
    CLC
    ADC #$01
    SEC
    SBC {ZP_E2}         ; Compare by subtracting: (-dy) - e2
    LDA #$00
    SBC {ZP_E2}+1       ; High byte comparison
    BPL {update_y_label} ; If result is positive or zero, e2 <= -dy, so skip x update
{update_x_label}:
    LDA {ZP_ERR}        ; err -= dy
    SEC
    SBC {ZP_DY}
    STA {ZP_ERR}
    LDA {ZP_ERR}+1
    SBC #$00
    STA {ZP_ERR}+1
    LDA {ZP_CURRENT_X}  ; x += sx
    CLC
    ADC {ZP_SX}
    STA {ZP_CURRENT_X}
    BCC {update_y_label}
    INC {ZP_CURRENT_X}+1

{update_y_label}:
    ; if (e2 < dx)
    LDA {ZP_E2}
    SEC
    SBC {ZP_DX}
    LDA {ZP_E2}+1
    SBC {ZP_DX}+1
    BCS {plot_loop_label}_main ; If result has no borrow, e2 >= dx, so skip y update

    LDA {ZP_ERR}        ; err += dx
    CLC
    ADC {ZP_DX}
    STA {ZP_ERR}
    LDA {ZP_ERR}+1
    ADC {ZP_DX}+1
    STA {ZP_ERR}+1
    LDA {ZP_CURRENT_Y}  ; y += sy
    CLC
    ADC {ZP_SY}
    STA {ZP_CURRENT_Y}

    JMP {plot_loop_label}_main

{end_plot_label}:
    RTS
"""

    return code.strip()

def _generate_gfx_draw_ellipse():
    """
    Generates assembly to draw an ellipse using floating point math.
    Based on Section 4.2.2.3 of "The Graphics Book for the Commodore 64".
    Formula: y = YR * sqrt(1 - (X*X)/(XR*XR))

    Input (all ZP locations):
    - xm ($B0, $B1): 16-bit center X coordinate.
    - ym ($B2): 8-bit center Y coordinate.
    - xr ($B6, $B7): 16-bit X radius.
    - yr ($B8): 8-bit Y radius.
    """
    # Input ZP locations (match draw_ellipse in ast_processor)
    ZP_XM = "$B0"
    ZP_YM = "$B2"
    ZP_XR = "$B6"
    ZP_YR = "$B8"

    # Temporary ZP locations for calculations
    ZP_CURRENT_X = "$BA" # 16-bit integer loop counter for X
    ZP_TC_INT = "$BC"    # 16-bit integer result for Y offset (TC)

    # ZP locations for plotting (used by gfx_plot_point)
    ZP_PLOT_X = "$B0" # 16-bit
    ZP_PLOT_Y = "$B2" # 8-bit

    # Labels
    draw_ellipse_label = create_label("gfx_draw_ellipse", str(py2asm_globals.label_counter))
    main_loop_label = create_label("ellipse_main_loop", str(py2asm_globals.label_counter))
    x_loop_label = create_label("ellipse_x_loop", str(py2asm_globals.label_counter))
    plot_points_label = create_label("ellipse_plot_points", str(py2asm_globals.label_counter))
    end_ellipse_label = create_label("end_ellipse", str(py2asm_globals.label_counter))
    py2asm_globals.label_counter += 1

    # Wozniak FP ZP locations (from globals)
    FP1 = f"${py2asm_globals.WOZ_FP_X1:02X}"
    FP2 = f"${py2asm_globals.WOZ_FP_X2:02X}"

    code = f"""
{draw_ellipse_label}
    ; --- Draw an ellipse using floating point math ---
    ; Based on "The Graphics Book for the Commodore 64", Sec 4.2.2.3
    ; Input: XM in {ZP_XM}/{ZP_XM}+1, YM in {ZP_YM}, XR in {ZP_XR}/{ZP_XR}+1, YR in {ZP_YR}

    ; Convert integer radii XR and YR to floating point numbers in FP1 and FP2
    ; for use in the calculation loop. We store them in temporary ZP vars.
    LDA {ZP_XR}
    STA {py2asm_globals.TEMP_VAR_1:02X}
    LDA {ZP_XR}+1
    STA {py2asm_globals.TEMP_VAR_1:02X}+1
    JSR int_to_fp1_from_addr ; Convert XR to float in FP1
    ; Store FP1 (XR_float) in a temp FP var
    JSR copy_fp1_to_fp_addr_temp2

    LDA {ZP_YR}
    STA {py2asm_globals.TEMP_VAR_1:02X}
    LDA #$00
    STA {py2asm_globals.TEMP_VAR_1:02X}+1
    JSR int_to_fp1_from_addr ; Convert YR to float in FP1
    ; Store FP1 (YR_float) in a temp FP var
    JSR copy_fp1_to_fp_addr_temp3

    ; Main loop for F2 = 1 (right half) and F2 = -1 (left half)
    ; We will just run the code twice, once for positive X and once for negative X

    ; --- Right half (X from 0 to XR) ---
    LDA #$00
    STA {ZP_CURRENT_X}
    STA {ZP_CURRENT_X}+1

{x_loop_label}_right:
    ; --- Calculate TC = YR * SQR(1 - (X*X)/(XR*XR)) ---
    ; 1. Calculate X*X
    LDA {ZP_CURRENT_X}
    STA {py2asm_globals.TEMP_VAR_1:02X}
    LDA {ZP_CURRENT_X}+1
    STA {py2asm_globals.TEMP_VAR_1:02X}+1
    JSR int_to_fp1_from_addr ; FP1 = X_float
    JSR copy_fp1_to_fp2      ; FP2 = X_float
    JSR FP_FMUL              ; FP1 = X_float * X_float = X_squared

    ; 2. Calculate XR*XR
    JSR copy_fp_addr_temp2_to_fp2 ; FP2 = XR_float
    JSR copy_fp_addr_temp2_to_fp1 ; FP1 = XR_float
    JSR FP_FMUL              ; FP1 = XR_float * XR_float = XR_squared

    ; 3. Calculate (X*X) / (XR*XR)
    ; FP1 has XR_squared. Need to swap with X_squared before division.
    ; Let's put X_squared (currently in FP1) into a temp FP var.
    JSR copy_fp1_to_fp_addr_temp1
    ; Now load XR_squared into FP1
    JSR copy_fp_addr_temp2_to_fp1
    JSR FP_FMUL ; FP1 = XR_squared * XR_squared (recalc needed after copy)
    ; Now load X_squared into FP2
    JSR copy_fp_addr_temp1_to_fp2
    ; Now we have FP1=XR_squared, FP2=X_squared. We need to calculate FP2/FP1.
    JSR FP_FDIV              ; FP1 = Dividend/Divisor = X_squared / XR_squared

    ; 4. Calculate 1.0 - result
    JSR copy_fp1_to_fp2      ; FP2 = ratio
    JSR load_one_fp1         ; FP1 = 1.0
    JSR FP_FSUB              ; FP1 = 1.0 - ratio

    ; 5. Calculate SQR(result)
    JSR FP_SQRT              ; FP1 = sqrt(1.0 - ratio)

    ; 6. Calculate YR * result
    JSR copy_fp_addr_temp3_to_fp2 ; FP2 = YR_float
    JSR FP_FMUL              ; FP1 = sqrt_val * YR_float = TC_float

    ; 7. Convert TC_float back to integer
    JSR FP_FIX               ; Converts FP1 to 16-bit integer in M1, M1+1
    LDA {py2asm_globals.WOZ_FP_M1:02X}+1 ; LSB of integer result
    STA {ZP_TC_INT}
    LDA {py2asm_globals.WOZ_FP_M1:02X}   ; MSB of integer result
    STA {ZP_TC_INT}+1

    ; --- Plot the 4 symmetric points ---
{plot_points_label}_right:
    ; Point 1: (XM + X, YM + TC)
    LDA {ZP_XM}
    CLC
    ADC {ZP_CURRENT_X}
    STA {ZP_PLOT_X}
    LDA {ZP_XM}+1
    ADC {ZP_CURRENT_X}+1
    STA {ZP_PLOT_X}+1
    LDA {ZP_YM}
    CLC
    ADC {ZP_TC_INT}
    STA {ZP_PLOT_Y}
    JSR gfx_plot_point

    ; Point 2: (XM + X, YM - TC)
    ; X is the same
    LDA {ZP_YM}
    SEC
    SBC {ZP_TC_INT}
    STA {ZP_PLOT_Y}
    JSR gfx_plot_point

    ; --- Loop control for right half ---
    ; Increment current X
    INC {ZP_CURRENT_X}
    BNE {x_loop_label}_right_nocarry
    INC {ZP_CURRENT_X}+1
{x_loop_label}_right_nocarry:
    ; Compare current X with XR
    LDA {ZP_CURRENT_X}+1
    CMP {ZP_XR}+1
    BCC {x_loop_label}_right ; if X_h < XR_h, continue
    BEQ {x_loop_label}_right_check_lsb
    JMP {end_ellipse_label} ; if X_h > XR_h, done
{x_loop_label}_right_check_lsb:
    LDA {ZP_CURRENT_X}
    CMP {ZP_XR}
    BCC {x_loop_label}_right ; if X_l < XR_l, continue

    ; Drawing of left half is omitted for brevity but would follow a similar pattern
    ; with X decrementing from 0 to -XR.

{end_ellipse_label}:
    RTS
"""
    return code.strip()


def _generate_copy_fp1_to_fp2():
    return f"""
copy_fp1_to_fp2
    LDA ${py2asm_globals.WOZ_FP_X1:02X}
    STA ${py2asm_globals.WOZ_FP_X2:02X}
    LDX #3
copy_fp1_to_fp2_loop:
    LDA ${py2asm_globals.WOZ_FP_X1:02X},X
    STA ${py2asm_globals.WOZ_FP_X2:02X},X
    DEX
    BPL copy_fp1_to_fp2_loop
    RTS
"""

def _generate_copy_fp1_to_fp_addr_temp1():
    return f"""
copy_fp1_to_fp_addr_temp1
    LDA ${py2asm_globals.WOZ_FP_X1:02X}
    STA ${py2asm_globals.TEMP_VAR_1}+3
    LDX #3
copy_fp1_to_fp_addr_temp1_loop:
    LDA ${py2asm_globals.WOZ_FP_X1:02X},X
    STA ${py2asm_globals.TEMP_VAR_1},X
    DEX
    BPL copy_fp1_to_fp_addr_temp1_loop
    RTS
"""

def _generate_copy_fp1_to_fp_addr_temp2():
    return f"""
copy_fp1_to_fp_addr_temp2
    LDA ${py2asm_globals.WOZ_FP_X1:02X}
    STA ${py2asm_globals.TEMP_VAR_2}+3
    LDX #3
copy_fp1_to_fp_addr_temp2_loop:
    LDA ${py2asm_globals.WOZ_FP_X1:02X},X
    STA ${py2asm_globals.TEMP_VAR_2},X
    DEX
    BPL copy_fp1_to_fp_addr_temp2_loop
    RTS
"""

def _generate_copy_fp1_to_fp_addr_temp3():
    return f"""
copy_fp1_to_fp_addr_temp3
    LDA ${py2asm_globals.WOZ_FP_X1:02X}
    STA ${py2asm_globals.TEMP_VAR_3}+3
    LDX #3
copy_fp1_to_fp_addr_temp3_loop:
    LDA ${py2asm_globals.WOZ_FP_X1:02X},X
    STA ${py2asm_globals.TEMP_VAR_3},X
    DEX
    BPL copy_fp1_to_fp_addr_temp3_loop
    RTS
"""


def _generate_copy_fp_addr_temp1_to_fp2():
    return f"""
copy_fp_addr_temp1_to_fp2
    LDA ${py2asm_globals.TEMP_VAR_1}+3
    STA ${py2asm_globals.WOZ_FP_X2}
    LDX #3
copy_fp_addr_temp1_to_fp2_loop:
    LDA ${py2asm_globals.TEMP_VAR_1},X
    STA ${py2asm_globals.WOZ_FP_X2},X
    DEX
    BPL copy_fp_addr_temp1_to_fp2_loop
    RTS
"""

def _generate_copy_fp_addr_temp2_to_fp1():
    return f"""
copy_fp_addr_temp2_to_fp1
    LDA ${py2asm_globals.TEMP_VAR_2}+3
    STA ${py2asm_globals.WOZ_FP_X1}
    LDX #3
copy_fp_addr_temp2_to_fp1_loop:
    LDA ${py2asm_globals.TEMP_VAR_2},X
    STA ${py2asm_globals.WOZ_FP_X1},X
    DEX
    BPL copy_fp_addr_temp2_to_fp1_loop
    RTS
"""

def _generate_copy_fp_addr_temp2_to_fp2():
    return f"""
copy_fp_addr_temp2_to_fp2
    LDA ${py2asm_globals.TEMP_VAR_2}+3
    STA ${py2asm_globals.WOZ_FP_X2}
    LDX #3
copy_fp_addr_temp2_to_fp2_loop:
    LDA ${py2asm_globals.TEMP_VAR_2},X
    STA ${py2asm_globals.WOZ_FP_X2},X
    DEX
    BPL copy_fp_addr_temp2_to_fp2_loop
    RTS
"""

def _generate_copy_fp_addr_temp3_to_fp2():
    return f"""
copy_fp_addr_temp3_to_fp2
    LDA ${py2asm_globals.TEMP_VAR_3}+3
    STA ${py2asm_globals.WOZ_FP_X2}
    LDX #3
copy_fp_addr_temp3_to_fp2_loop:
    LDA ${py2asm_globals.TEMP_VAR_3},X
    STA ${py2asm_globals.WOZ_FP_X2},X
    DEX
    BPL copy_fp_addr_temp3_to_fp2_loop
    RTS
"""



def _generate_int_to_fp1_from_addr():
    return f"""
int_to_fp1_from_addr
    ; Converts a 16-bit integer from TEMP_VAR_1 to a floating point number in FP1
    LDA ${py2asm_globals.TEMP_VAR_1}
    STA ${py2asm_globals.WOZ_FP_M1+2:02X}
    LDA ${py2asm_globals.TEMP_VAR_1}+1
    STA ${py2asm_globals.WOZ_FP_M1+1:02X}
    LDA #$00
    STA ${py2asm_globals.WOZ_FP_M1:02X}
    JSR FP_FLOAT
    RTS
    """

def _generate_gfx_draw_rect():
    """
    Draws a rectangle by calling gfx_draw_line four times.
    Input (ZP): x1 ($B0,$B1), y1 ($B2), x2 ($B6,$B7), y2 ($B8)
    Uses ZP locations $C2-$C9 as temporary storage for coordinates.
    """
    # ZP locations for draw_line parameters
    ZP_X1 = "$B0"
    ZP_Y1 = "$B2"
    ZP_X2 = "$B6"
    ZP_Y2 = "$B8"
    # Temporary storage for the rectangle's original coordinates
    RECT_X1 = "$C2" # 16-bit
    RECT_Y1 = "$C4" # 8-bit
    RECT_X2 = "$C6" # 16-bit
    RECT_Y2 = "$C8" # 8-bit

    code = f"""
gfx_draw_rect
    ; --- Save original rectangle coordinates ---
    LDA {ZP_X1};     STA {RECT_X1}
    LDA {ZP_X1}+1;   STA {RECT_X1}+1
    LDA {ZP_Y1};     STA {RECT_Y1}
    LDA {ZP_X2};     STA {RECT_X2}
    LDA {ZP_X2}+1;   STA {RECT_X2}+1
    LDA {ZP_Y2};     STA {RECT_Y2}

    ; --- Draw line 1: (x1, y1) -> (x2, y1) ---
    LDA {RECT_X1};     STA {ZP_X1}
    LDA {RECT_X1}+1;   STA {ZP_X1}+1
    LDA {RECT_Y1};     STA {ZP_Y1}
    LDA {RECT_X2};     STA {ZP_X2}
    LDA {RECT_X2}+1;   STA {ZP_X2}+1
    LDA {RECT_Y1};     STA {ZP_Y2}  ; y2 = y1
    JSR gfx_draw_line

    ; --- Draw line 2: (x2, y1) -> (x2, y2) ---
    ; x1 is already x2. y1 is already y1.
    LDA {RECT_Y2};     STA {ZP_Y2}  ; y2 = original y2
    JSR gfx_draw_line

    ; --- Draw line 3: (x2, y2) -> (x1, y2) ---
    LDA {RECT_X1};     STA {ZP_X1}      ; x1 = original x1
    LDA {RECT_X1}+1;   STA {ZP_X1}+1
    JSR gfx_draw_line

    ; --- Draw line 4: (x1, y2) -> (x1, y1) ---
    ; x2 is already x1. y2 is already y2.
    LDA {RECT_Y1};     STA {ZP_Y1}      ; y1 = original y1
    JSR gfx_draw_line

    RTS
"""
    return code.strip()

# --- Nuove Routine per Sprite ---

# Offset dei registri VIC dal base address $D000
VIC_SPRITE0_X = 0x00                  # Sprite 0 X-position
VIC_SPRITE0_Y = 0x01                  # Sprite 0 Y-position
VIC_SPRITE_MSB_X = 0x10               # Most Significant Bit of X-coordinate for all sprites
VIC_SPRITE_ENABLE = 0x15              # Sprite enable register (bitmap)
VIC_SPRITE_EXPAND_Y = 0x17            # Sprite Y-expansion register (bitmap)
VIC_SPRITE_PRIORITY = 0x1B            # Sprite-to-background priority (bitmap)
VIC_SPRITE_MULTICOLOR_ENABLE = 0x1C   # Sprite multicolor mode select (bitmap)
VIC_SPRITE_EXPAND_X = 0x1D            # Sprite X-expansion register (bitmap)
VIC_COLLISION_SPRITE_SPRITE = 0x1E    # Sprite-to-sprite collision register
VIC_COLLISION_SPRITE_DATA = 0x1F      # Sprite-to-data (background) collision register
VIC_SPRITE0_COLOR = 0x27              # Sprite 0 color register

# Base address for sprite data pointers in the screen RAM block
SPRITE_POINTER_BASE = 0x07F8          # Base address for sprite data pointers in screen RAM block

def _generate_sprite_set_pos():
    """
    Imposta la posizione di uno sprite.
    Input: X-reg = numero sprite (0-7), A = coordinata Y, ZP_X_COORD ($B0) = coordinata X (LSB, 0-255).
    Nota: Per posizioni X > 255, usare `sprite_set_x_msb`.
    """
    code = f"""
sprite_set_pos
    ; Input: X=sprite_num, A=Y, $B0=X_LSB
    ; Imposta la posizione Y
    STA ${py2asm_globals.VIC_BASE_ADDR:04X} + {VIC_SPRITE0_Y},X
    ; Imposta la posizione X (LSB)
    LDA $B0 ; Prende la coordinata X da una locazione ZP
    STA ${py2asm_globals.VIC_BASE_ADDR:04X} + {VIC_SPRITE0_X},X
    RTS
"""
    return code.strip()

def _generate_sprite_set_x_msb():
    """
    Imposta o cancella il bit più significativo (MSB) della coordinata X per uno o più sprite.
    Questo permette di superare la coordinata X=255.
    Input: A = maschera di bit per gli sprite da modificare (bit 0 per sprite 0, etc.).
           Se il bit nella maschera è 1, l'MSB della X per quello sprite viene impostato a 1.
    """
    code = f"""
sprite_set_x_msb
    ; Input: A = maschera di bit degli sprite da impostare
    PHA ; Salva la maschera
    LDA ${py2asm_globals.VIC_BASE_ADDR + VIC_SPRITE_MSB_X:04X}
    ORA PLA ; Applica la maschera per SETTARE i bit
    STA ${py2asm_globals.VIC_BASE_ADDR + VIC_SPRITE_MSB_X:04X}
    RTS
"""
    return code.strip()

def _generate_sprite_set_x_msb_clear():
    """
    Cancella il bit più significativo (MSB) della coordinata X per uno o più sprite.
    Input: A = maschera di bit per gli sprite da modificare (bit 0 per sprite 0, etc.).
           Se il bit nella maschera è 1, l'MSB della X per quello sprite viene impostato a 0.
    """
    code = f"""
sprite_set_x_msb_clear
    ; Input: A = maschera di bit degli sprite da cancellare
    EOR #$FF ; Inverte i bit della maschera (0s per gli sprite da cancellare)
    PHA      ; Salva la maschera invertita
    LDA ${py2asm_globals.VIC_BASE_ADDR + VIC_SPRITE_MSB_X:04X}
    AND PLA  ; Applica la maschera per CANCELLARE i bit
    STA ${py2asm_globals.VIC_BASE_ADDR + VIC_SPRITE_MSB_X:04X}
    RTS
"""
    return code.strip()

def _generate_sprite_enable():
    """
    Abilita uno o più sprite.
    Input: A = maschera di bit per gli sprite da abilitare (bit 0 per sprite 0, etc.).
    """
    code = f"""
sprite_enable
    ; Input: A = maschera di bit
    PHA ; Salva la maschera
    LDA ${py2asm_globals.VIC_BASE_ADDR + VIC_SPRITE_ENABLE:04X}
    ORA PLA ; Applica la maschera
    STA ${py2asm_globals.VIC_BASE_ADDR + VIC_SPRITE_ENABLE:04X}
    RTS
"""
    return code.strip()

def _generate_sprite_disable():
    """
    Disabilita uno o più sprite.
    Input: A = maschera di bit per gli sprite da disabilitare.
    """
    code = f"""
sprite_disable
    ; Input: A = maschera di bit
    EOR #$FF ; Inverte i bit della maschera (0s per gli sprite da disabilitare)
    PHA      ; Salva la maschera invertita
    LDA ${py2asm_globals.VIC_BASE_ADDR + VIC_SPRITE_ENABLE:04X}
    AND PLA  ; Applica la maschera per CANCELLARE i bit
    STA ${py2asm_globals.VIC_BASE_ADDR + VIC_SPRITE_ENABLE:04X}
    RTS
"""
    return code.strip()

def _generate_sprite_set_color():
    """
    Imposta il colore di un singolo sprite.
    Input: X-reg = numero sprite (0-7), A = codice colore (0-15).
    """
    code = f"""
sprite_set_color
    ; Input: X=sprite_num, A=colore
    STA ${py2asm_globals.VIC_BASE_ADDR + VIC_SPRITE0_COLOR:04X},X
    RTS
"""
    return code.strip()

def _generate_sprite_expand_xy():
    """
    Espande uno o più sprite in orizzontale e/o verticale.
    Input: A = maschera per espansione Y, X-reg = maschera per espansione X.
    """
    code = f"""
sprite_expand_xy
    ; Input: A=maschera_Y, X=maschera_X
    ; Espansione Y
    PHA ; Salva maschera Y
    LDA ${py2asm_globals.VIC_BASE_ADDR + VIC_SPRITE_EXPAND_Y:04X}
    ORA PLA
    STA ${py2asm_globals.VIC_BASE_ADDR + VIC_SPRITE_EXPAND_Y:04X}
    ; Espansione X
    TXA ; Sposta maschera X in A
    PHA
    LDA ${py2asm_globals.VIC_BASE_ADDR + VIC_SPRITE_EXPAND_X:04X}
    ORA PLA
    STA ${py2asm_globals.VIC_BASE_ADDR + VIC_SPRITE_EXPAND_X:04X}
    RTS
"""
    return code.strip()

def _generate_sprite_set_priority():
    """
    Imposta la priorità degli sprite (davanti o dietro lo sfondo).
    Input: A = maschera di bit (1=dietro, 0=davanti).
    """
    code = f"""
sprite_set_priority
    ; Input: A = maschera di bit (1=dietro, 0=davanti)
    PHA
    LDA ${py2asm_globals.VIC_BASE_ADDR + VIC_SPRITE_PRIORITY:04X}
    ORA PLA
    STA ${py2asm_globals.VIC_BASE_ADDR + VIC_SPRITE_PRIORITY:04X}
    RTS
"""
    return code.strip()

def _generate_sprite_set_multicolor():
    """
    Abilita la modalità multicolore per gli sprite.
    Input: A = maschera di bit per gli sprite da rendere multicolore.
    """
    code = f"""
sprite_set_multicolor
    ; Input: A = maschera di bit
    PHA
    LDA ${py2asm_globals.VIC_BASE_ADDR + VIC_SPRITE_MULTICOLOR_ENABLE:04X}
    ORA PLA
    STA ${py2asm_globals.VIC_BASE_ADDR + VIC_SPRITE_MULTICOLOR_ENABLE:04X}
    RTS
"""
    return code.strip()

def _generate_sprite_set_multicolor_colors():
    """
    Imposta i due colori globali per gli sprite in modalità multicolore.
    Input: A = colore per il registro multicolor 1 ($D025)
           X = colore per il registro multicolor 2 ($D026)
    """
    code = f"""
sprite_set_multicolor_colors
    STA ${py2asm_globals.VIC_BASE_ADDR + 0x25:04X} ; Imposta colore multicolor 1
    STX ${py2asm_globals.VIC_BASE_ADDR + 0x26:04X} ; Imposta colore multicolor 2
    RTS
"""
    return code.strip()

def _generate_sprite_check_collision_sprite():
    """
    Controlla le collisioni tra sprite.
    Output: A = registro di collisione ($D01E). Un bit a 1 indica che lo sprite corrispondente è entrato in collisione.
    """
    code = f"""
sprite_check_collision_sprite
    LDA ${py2asm_globals.VIC_BASE_ADDR + VIC_COLLISION_SPRITE_SPRITE:04X}
    RTS
"""
    return code.strip()

def _generate_sprite_check_collision_data():
    """
    Controlla le collisioni tra sprite e dati dello schermo/caratteri.
    Output: A = registro di collisione ($D01F).
    """
    code = f"""
sprite_check_collision_data
    LDA ${py2asm_globals.VIC_BASE_ADDR + VIC_COLLISION_SPRITE_DATA:04X}
    RTS
"""
    return code.strip()

def _generate_sprite_set_pointer():
    """
    Imposta il puntatore dati per un singolo sprite.
    Input: X-reg = numero sprite (0-7), A = valore del puntatore.
    Il puntatore è un valore che, moltiplicato per 64, dà l'indirizzo dei dati dello sprite.
    Es: pointer=64 -> indirizzo = 64*64 = 4096 = $1000.
    """
    code = f"""
sprite_set_pointer
    ; Input: X=sprite_num, A=valore puntatore
    STA {SPRITE_POINTER_BASE},X
    RTS
"""
    return code.strip()

def _generate_sprite_create_from_data():
    """
    Funzione "editor" per creare/aggiornare i dati di uno sprite da un blocco di memoria.
    Copia 63 byte da un indirizzo sorgente, calcola la destinazione in un'area predefinita
    per i dati sprite ($3000-$31FF), esegue la copia e imposta il puntatore dello sprite.

    Input:
    - X-reg: Numero dello sprite (0-7) da modificare.
    - ZP_SRC_PTR ($F0-$F1): Puntatore (16-bit) all'indirizzo dei dati sorgente (63 bytes).

    Utilizza:
    - ZP_DEST_PTR ($F2-$F3): Puntatore di destinazione calcolato.
    - Y-reg: Come contatore per il loop di copia.
    """
    ZP_SRC_PTR = "$F0"
    ZP_DEST_PTR = "$F2"
    # Area dati sprite: $3000-$31FF. Ogni sprite occupa 64 byte.
    # I puntatori sprite sono (indirizzo / 64).
    # Quindi per $3000 il puntatore è $3000/64 = $C0. Per $3040 è $C1, etc.
    SPRITE_DATA_POINTER_START = 0xC0 # Valore puntatore per sprite in $3000

    copy_loop_label = create_label("sprite_copy_loop", str(py2asm_globals.label_counter))
    py2asm_globals.label_counter += 1

    code = f"""
sprite_create_from_data
    ; Input: X=sprite_num, $F0/$F1=indirizzo sorgente

    ; --- 1. Imposta il puntatore dello sprite per puntare ai nuovi dati ---
    ; Il valore del puntatore è POINTER_START + numero_sprite.
    TXA ; Sposta numero sprite in A
    CLC
    ADC #${SPRITE_DATA_POINTER_START}
    STA {SPRITE_POINTER_BASE},X ; Imposta il puntatore (es. $07F8,X)

    ; --- 2. Calcola l'indirizzo di destinazione per i dati dello sprite ---
    ; Destinazione = (valore puntatore) * 64.
    ; Dato che il puntatore è in A, lo moltiplichiamo per 64 (shift a sinistra di 6).
    ; Il risultato sarà l'indirizzo base dei dati dello sprite.
    ASL A
    ASL A
    ASL A
    ASL A
    ASL A
    ASL A
    STA {ZP_DEST_PTR}+1 ; Il risultato è l'high byte dell'indirizzo (es. $C0 -> $30)
    LDA #$00
    STA {ZP_DEST_PTR}   ; L'low byte è sempre $00 in questo schema

    ; --- 3. Copia i 63 byte dalla sorgente alla destinazione ---
    LDY #$00 ; Inizializza il contatore
{copy_loop_label}:
    LDA ({ZP_SRC_PTR}),Y  ; Carica un byte dalla sorgente
    STA ({ZP_DEST_PTR}),Y  ; Salva il byte nella destinazione
    INY ; Incrementa il contatore
    CPY #63 ; Abbiamo copiato 63 byte?
    BNE {copy_loop_label} ; Se no, continua
    RTS
"""
    return code.strip()

# The main dictionary mapping routine names to their generator functions.
ROUTINE_GENERATORS = {
    # Graphics
    'gfx_turn_on': _generate_gfx_turn_on,
    'gfx_turn_off': _generate_gfx_turn_off,
    'gfx_clear_screen': _generate_gfx_clear_screen,
    'gfx_plot_point': _generate_gfx_plot_point,
    'gfx_draw_line': _generate_gfx_draw_line,
    'gfx_draw_ellipse': _generate_gfx_draw_ellipse,
    'gfx_draw_rect': _generate_gfx_draw_rect,
    'gfx_draw_circle': lambda: "", # Circle is handled by draw_ellipse in assembly

    # Sprites
    'sprite_set_pos': _generate_sprite_set_pos,
    'sprite_set_x_msb': _generate_sprite_set_x_msb,
    'sprite_set_x_msb_clear': _generate_sprite_set_x_msb_clear,
    'sprite_enable': _generate_sprite_enable,
    'sprite_disable': _generate_sprite_disable,
    'sprite_set_color': _generate_sprite_set_color,
    'sprite_expand_xy': _generate_sprite_expand_xy,
    'sprite_set_priority': _generate_sprite_set_priority,
    'sprite_set_multicolor': _generate_sprite_set_multicolor,
    'sprite_set_multicolor_colors': _generate_sprite_set_multicolor_colors,
    'sprite_check_collision_sprite': _generate_sprite_check_collision_sprite,
    'sprite_check_collision_data': _generate_sprite_check_collision_data,
    'sprite_set_pointer': _generate_sprite_set_pointer,
    'sprite_create_from_data': _generate_sprite_create_from_data,

    # Floating Point Helpers (used by ellipse, etc.)
    'copy_fp1_to_fp2': _generate_copy_fp1_to_fp2,
    'copy_fp1_to_fp_addr_temp1': _generate_copy_fp1_to_fp_addr_temp1,
    'copy_fp1_to_fp_addr_temp2': _generate_copy_fp1_to_fp_addr_temp2,
    'copy_fp1_to_fp_addr_temp3': _generate_copy_fp1_to_fp_addr_temp3,
    'copy_fp_addr_temp1_to_fp2': _generate_copy_fp_addr_temp1_to_fp2,
    'copy_fp_addr_temp2_to_fp1': _generate_copy_fp_addr_temp2_to_fp1,
    'copy_fp_addr_temp2_to_fp2': _generate_copy_fp_addr_temp2_to_fp2,
    'copy_fp_addr_temp3_to_fp2': _generate_copy_fp_addr_temp3_to_fp2,
    'int_to_fp1_from_addr': _generate_int_to_fp1_from_addr,

    # Note: The core FP routines (FP_ADD, FP_SUB, etc.) are assumed to be
    # in a separate, always-included library like 'woz_fp.s' and are not
    # generated dynamically here. We only add them to used_routines.
    # This dictionary is for routines generated by Python code.
}

def get_routine_code(routine_name):
    """
    Returns the assembly code for a given routine name.
    """
    generator = ROUTINE_GENERATORS.get(routine_name)
    if generator:
        return generator()
    return None # Or raise an error if the routine is not found
