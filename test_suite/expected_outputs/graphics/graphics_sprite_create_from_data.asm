;--------- Start python code ---------
; 
; # Create sprite 0 from data located at address $4000
; sprite_create_from_data(0, 0x4000)
; 
; # Create sprite 1 using variables
; sprite_to_create = 1
; data_address = 0x4040
; sprite_create_from_data(sprite_to_create, data_address)
; 
; while True: # pragma: no cover
;     pass # pragma: no cover

    * = $C100
    JMP main_program_entry_point
; --- Data Section ---
sprite_to_create * = * + 2
data_address * = * + 2
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
    LDA #0
    STA temp_0
    LDA #0
    STA temp_0+1
    LDA #0
    STA temp_1
    LDA #64
    STA temp_1+1
    LDA #1
    STA sprite_to_create
    LDA #0
    STA sprite_to_create+1
    LDA #64
    STA data_address
    LDA #64
    STA data_address+1
    LDA sprite_to_create
    STA temp_1
    LDA sprite_to_create+1
    STA temp_1+1
    LDA data_address
    STA temp_0
    LDA data_address+1
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
sprite_create_from_data
    ; Input: X=sprite_num, $F0/$F1=indirizzo sorgente

    ; --- 1. Imposta il puntatore dello sprite per puntare ai nuovi dati ---
    ; Il valore del puntatore è POINTER_START + numero_sprite.
    TXA ; Sposta numero sprite in A
    CLC
    ADC #$192
    STA 2040,X ; Imposta il puntatore (es. $07F8,X)

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
    STA $F2+1 ; Il risultato è l'high byte dell'indirizzo (es. $C0 -> $30)
    LDA #$00
    STA $F2   ; L'low byte è sempre $00 in questo schema

    ; --- 3. Copia i 63 byte dalla sorgente alla destinazione ---
    LDY #$00 ; Inizializza il contatore
sprite_copy_loop_1:
    LDA ($F0),Y  ; Carica un byte dalla sorgente
    STA ($F2),Y  ; Salva il byte nella destinazione
    INY ; Incrementa il contatore
    CPY #63 ; Abbiamo copiato 63 byte?
    BNE sprite_copy_loop_1 ; Se no, continua
    RTS
