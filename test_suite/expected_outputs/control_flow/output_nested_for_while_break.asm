;--------- Start python code ---------
; 
; outer_sum = 0
; my_list = [1, 2, 3]
; for x in my_list: # x = 1, 2, 3
;     outer_sum = outer_sum + x
;     y = 0
;     while y < 2: # y = 0, 1
;         y = y + 1 # In Python, this would be inside the loop
;         if x == 2:
;             break # Exits the inner while if x is 2
;     # Se x=1, y arriva a 2. outer_sum = 1
;     # Se x=2, y=1, break. outer_sum = 1+2=3
;     # Se x=3, y arriva a 2. outer_sum = 3+3=6
; # Expected: outer_sum = 6

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
outer_sum * = * + 2
my_list * = * + 2
x * = * + 2
y * = * + 2
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
    STA outer_sum
    LDA #0
    STA outer_sum+1
    LDA #0
    STA my_list
    LDA #0
    STA my_list+1
    JMP end_program

; --- Routines Section ---
    * = $8000
end_program
    RTS
