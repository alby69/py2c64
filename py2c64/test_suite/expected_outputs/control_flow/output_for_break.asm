;--------- Start python code ---------
; my_list = [1, 2, 3, 4, 5]
; res = 0
; for item in my_list:
;   if item == 4:
;     break
;   res = res + item
; # Expected: res = 1+2+3 = 6

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
my_list * = * + 2
res * = * + 2
item * = * + 2
exception_handler_active_flag * = * + 2
current_exception_target_label_ptr * = * + 2
last_exception_type_code * = * + 1

main_program_entry_point:
; --- Code Section ---
    LDA #<02FF
    STA $E0
    LDA #>02FF
    STA $E1
    LDA #0
    STA res
    LDA #0
    STA res+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
