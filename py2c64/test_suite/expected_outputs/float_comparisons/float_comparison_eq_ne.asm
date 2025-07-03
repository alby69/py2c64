;--------- Start python code ---------
; 
; a = 3.5
; b = 3.5
; c = -2.0
; 
; res_eq = (a == b)  # Expected: True (1)
; res_ne = (a != c)  # Expected: True (1)
; res_lt = (c < a)   # Expected: True (1)
; res_gt = (a > c)   # Expected: True (1)
; res_le1 = (a <= b) # Expected: True (1)
; res_le2 = (c <= a) # Expected: True (1)
; res_ge1 = (a >= b) # Expected: True (1)
; res_ge2 = (a >= c) # Expected: True (1)

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
a * = * + 2
b * = * + 2
c * = * + 2
res_eq * = * + 2
res_ne * = * + 2
res_lt * = * + 2
res_gt * = * + 2
res_le1 * = * + 2
res_le2 * = * + 2
res_ge1 * = * + 2
res_ge2 * = * + 2
exception_handler_active_flag * = * + 2
current_exception_target_label_ptr * = * + 2
last_exception_type_code * = * + 1

main_program_entry_point:
; --- Code Section ---
    LDA #<02FF
    STA $E0
    LDA #>02FF
    STA $E1
    LDA #$00
    STA a+0
    LDA #$00
    STA a+1
    LDA #$70
    STA a+2
    LDA #$82
    STA a+3
    LDA #$00
    STA b+0
    LDA #$00
    STA b+1
    LDA #$70
    STA b+2
    LDA #$82
    STA b+3
    LDA #0
    STA c
    LDA #0
    STA c+1
    LDA #0
    STA res_eq
    LDA #0
    STA res_eq+1
    LDA #0
    STA res_ne
    LDA #0
    STA res_ne+1
    LDA #0
    STA res_lt
    LDA #0
    STA res_lt+1
    LDA #0
    STA res_gt
    LDA #0
    STA res_gt+1
    LDA #0
    STA res_le1
    LDA #0
    STA res_le1+1
    LDA #0
    STA res_le2
    LDA #0
    STA res_le2+1
    LDA #0
    STA res_ge1
    LDA #0
    STA res_ge1+1
    LDA #0
    STA res_ge2
    LDA #0
    STA res_ge2+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
