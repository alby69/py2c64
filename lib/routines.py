from typing import Dict, List, Set

class C64HardwareLibrary:
    """Library for C64 hardware functions."""

    @staticmethod
    def get_graphics_routines() -> Dict[str, List[str]]:
        """Returns the routines for graphics from the graphics package."""
        return {
            'GON': [
                'GON:',
                '  JMP C824',
            ],
            'GOFF': [
                'GOFF:',
                '  JMP C841',
            ],
            'GCLEAR': [
                'GCLEAR:',
                '  JMP C912',
            ],
            'SCOLOR': [
                'SCOLOR:',
                '  JMP C931',
            ],
            'PCOLOR': [
                'PCOLOR:',
                '  JMP C92A',
            ],
            'PLOT': [
                'PLOT:',
                '  JMP C858',
            ],
            'UNPLOT': [
                'UNPLOT:',
                '  JMP C855',
            ],
            'SLINE': [
                'SLINE:',
                '  JMP C86B',
            ],
            'CLLINE': [
                'CLLINE:',
                '  JMP C868',
            ],

            # Full routine implementation starting at C824
            'C824': [
                'C824: ; INIT routine',
                '  NOP',
                '  LDA V+17',
                '  STA CBIE',
                '  LDA V+24',
                '  STA CBIF',
                '  LDA #%00111011',
                '  STA V+17',
                '  LDA #%00011000',
                '  STA V+24',
                '  LDA #$60',
                '  STA C824',
                '  RTS',
                'C841: ; GOFF routine',
                '  LDA CBIE',
                '  STA V+17',
                '  LDA CBIF',
                '  STA V+24',
                '  LDA #$EA',
                '  STA C824',
                '  JMP $E544',
                'C855: ; UNPLOT routine',
                '  LDX #$00',
                '  JMP C85A',
                'C858: ; PLOT routine',
                '  LDX #$80',
                'C85A: ; PL1 routine',
                '  STX FLG',
                '  JSR CHKCOM',
                '  JSR C879',
                '  JSR C894',
                '  JMP C8E2',
                'C868: ; CLLINE routine',
                '  LDX #$00',
                '  JMP C86D',
                'C86B: ; SLINE routine',
                '  LDX #$80',
                'C86D:',
                '  JSR C85A',
                '  JSR CHKCOM',
                '  JSR C879',
                '  JMP C9BB',
                'C879: ; TESCOR routine',
                '  JSR GETCOR',
                '  TXA',
                '  TAY',
                '  LDX XC+1',
                '  CPY #200',
                '  BCS C891',
                '  LDA XC',
                '  CPX #>320',
                '  BCC C890',
                '  BNE C891',
                '  CMP #<320',
                '  BCS C891',
                'C890: RTS',
                'C891: JMP QERR',
                'C894: ; HPOSN routine',
                '  STY CBIC',
                '  STA CBIA',
                '  STX CBIB',
                '  STA XC',
                '  STX XC+1',
                '  TYA',
                '  LSR A',
                '  LSR A',
                '  LSR A',
                '  TAX',
                '  LDA CB2F,X',
                '  STA B',
                '  TXA',
                '  AND #$03',
                '  TAX',
                '  LDA CB49,X',
                '  STA A',
                '  TYA',
                '  AND #7',
                '  CLC',
                '  ADC A',
                '  STA A',
                '  LDA XC',
                '  AND #$F8',
                '  STA OFFX',
                '  LDA #>GRAPH',
                '  ORA B',
                '  STA B',
                '  CLC',
                '  LDA A',
                '  ADC OFFX',
                '  STA A',
                '  LDA B',
                '  ADC XC+1',
                '  STA B',
                '  LDA XC',
                '  AND #7',
                '  EOR #7',
                '  TAX',
                '  LDA CB4D,X',
                '  STA MSC',
                '  RTS',
                'C8E2: ; PLT routine',
                '  LDY #0',
                '  PHP',
                '  LDA MSC',
                '  BIT FLG',
                '  BMI C8F0',
                '  EOR #$FF',
                '  AND (A),Y',
                '  JMP C8F2',
                'C8F0: ORA (A),Y',
                'C8F2: STA (A),Y',
                '  LDA A',
                '  STA USE',
                '  LDA B',
                '  LSR A',
                '  ROR USE',
                '  LSR A',
                '  ROR USE',
                '  LSR A',
                '  ROR USE',
                '  AND #$03',
                '  ORA #$04',
                '  STA USE+1',
                '  LDA CBID',
                '  STA (USE),Y',
                '  PLP',
                '  LDY TEMP',
                '  RTS',
                'C912: ; GCLEAR routine',
                '  LDA #>GRAPH',
                '  STA USE+1',
                '  LDY #<GRAPH',
                '  STY USE',
                '  LDX #$20',
                'C91C: TYA',
                '  STA (USE),Y',
                '  INY',
                '  BNE C91C',
                '  INC USE+1',
                '  DEX',
                '  BNE C91C',
                '  JMP C937',
                'C92A: ; PCOLOR routine',
                '  JSR CHKGET',
                '  STX CBID',
                '  RTS',
                'C931: ; SCOLOR routine',
                '  JSR CHKGET',
                '  STX CBID',
                'C937: LDX #$03',
                '  LDA #>VIDEO',
                '  STA USE+1',
                '  LDY #<VIDEO',
                '  STY USE',
                '  STY FLG',
                'C943: LDA CBID',
                'C946: STA (USE),Y',
                '  INY',
                '  CPY FLG',
                '  BNE C946',
                '  INC USE+1',
                '  DEX',
                '  BEQ C955',
                '  BPL C946',
                '  RTS',
                'C955: LDX #$E8',
                '  STX FLG',
                '  BNE C946',
                'C9BB: ; HLINE routine',
                '  PHA',
                '  LDA XCH',
                '  LSR A',
                '  LDA XCL',
                '  ROR A',
                '  LSR A',
                '  LSR A',
                '  STA TEMP',
                '  PLA',
                '  PHA',
                '  SEC',
                '  SBC XCL',
                '  PHA',
                '  TXA',
                '  SBC XCH',
                '  STA DIF3',
                '  BCS C9E1',
                '  PLA',
                '  EOR #$FF',
                '  ADC #1',
                '  PHA',
                '  LDA #0',
                '  SBC DIF3',
                'C9E1: STA DIF1',
                '  STA DIF5',
                '  PLA',
                '  STA DIFO',
                '  STA DIF4',
                '  PLA',
                '  STA XCL',
                '  STX XCH',
                '  TYA',
                '  CLC',
                '  SBC YC',
                '  BCC CA06',
                '  EOR #$FF',
                '  ADC #$FE',
                'CA06: STA DIF2',
                '  STY YC',
                '  ROR DIF3',
                '  SEC',
                '  SBC DIFO',
                '  TAX',
                '  LDA #$FF',
                '  SBC DIF1',
                '  STA CTR',
                '  LDY TEMP',
                '  BCS CA16',
                'CA11: ASL A',
                '  JSR C9A6',
                '  SEC',
                'CA16: LDA DIF4',
                '  ADC DIF2',
                '  STA DIF4',
                '  LDA DIF5',
                '  SBC #0',
                'CA20: STA DIF5',
                '  STY TEMP',
                '  JSR C8E2',
                '  INX',
                '  BNE CA2F',
                '  INC CTR',
                '  BNE CA2F',
                '  RTS',
                'CA2F: LDA DIF3',
                '  BCS CA11',
                '  JSR C979',
                '  CLC',
                '  LDA DIF4',
                '  ADC DIFO',
                '  STA DIF4',
                '  LDA DIF5',
                '  ADC DIF1',
                '  BVC CA20'
            ]
        }

    @staticmethod
    def get_sprite_routines() -> Dict[str, List[str]]:
        """Returns the routines for sprites."""
        return {
            "sprite_enable": [
                "SPRITE_ENABLE:",
                "    LDA SPRITE_MASK",
                "    ORA $D015",
                "    STA $D015",
                "    RTS"
            ],
            "sprite_disable": [
                "SPRITE_DISABLE:",
                "    LDA SPRITE_MASK",
                "    EOR #$FF",
                "    AND $D015",
                "    STA $D015",
                "    RTS"
            ],
            "sprite_set_pos": [
                "SPRITE_SET_POS:",
                "    ; Input: SPRITE_NUM, SPRITE_X, SPRITE_Y",
                "    LDA SPRITE_NUM",
                "    ASL",
                "    TAX",
                "    LDA SPRITE_X",
                "    STA $D000,X",
                "    LDA SPRITE_Y",
                "    STA $D001,X",
                "    RTS"
            ]
        }

class RoutineManager:
    """Manages library routines and their dependencies."""

    def __init__(self):
        self.available_routines: Dict[str, List[str]] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self.used_routines: Set[str] = set()

        # Load hardware routines
        self.available_routines.update(C64HardwareLibrary.get_graphics_routines())
        self.available_routines.update(C64HardwareLibrary.get_sprite_routines())

        # Load math routines
        self.available_routines.update(self._get_math_routines())

        # Load list routines
        self.available_routines.update(self._get_list_routines())

        # Load graphics package data tables
        self.available_routines.update(self._get_graphics_package_data())

        # Load scrolling routines
        self.available_routines.update(self._get_scrolling_routines())

        # Define dependencies
        self.dependencies = {
            "draw_line": ["multiply16x16"],
            "draw_ellipse": ["multiply16x16", "sqrt_int16"],
            "print_int16": ["divide16x16"],
            "SCROLL": ["CCOO", "CCBB", "CCE5", "CC86", "CCAB", "CC8D"]
        }

    def _get_math_routines(self) -> Dict[str, List[str]]:
        """Returns the math routines."""
        return {
            "multiply16x16": [
                "MULTIPLY16x16:",
                "    ; 16x16 -> 32 bit multiplication",
                "    ; Input: MULT_ARG1, MULT_ARG2",
                "    ; Output: MULT_RESULT (32 bit)",
                "    LDA #$00",
                "    STA MULT_RESULT",
                "    STA MULT_RESULT+1",
                "    STA MULT_RESULT+2",
                "    STA MULT_RESULT+3",
                "    LDX #$10",
                "MULT_LOOP:",
                "    LSR MULT_ARG1+1",
                "    ROR MULT_ARG1",
                "    BCC MULT_SKIP",
                "    CLC",
                "    LDA MULT_RESULT",
                "    ADC MULT_ARG2",
                "    STA MULT_RESULT",
                "    LDA MULT_RESULT+1",
                "    ADC MULT_ARG2+1",
                "    STA MULT_RESULT+1",
                "MULT_SKIP:",
                "    ASL MULT_ARG2",
                "    ROL MULT_ARG2+1",
                "    DEX",
                "    BNE MULT_LOOP",
                "    RTS"
            ],
            "divide16x16": [
                "DIVIDE16x16:",
                "    ; 16x16 -> 16 bit division",
                "    ; ... full implementation ...",
                "    RTS"
            ],
            "sqrt_int16": [
                "SQRT_INT16:",
                "    ; Approximate square root for integers",
                "    ; ... full implementation ...",
                "    RTS"
            ]
        }

    def mark_routine_used(self, routine_name: str):
        """Marks a routine as used and recursively adds its dependencies."""
        if routine_name in self.available_routines and routine_name not in self.used_routines:
            self.used_routines.add(routine_name)

            # Recursively add dependencies
            if routine_name in self.dependencies:
                for dep in self.dependencies[routine_name]:
                    self.mark_routine_used(dep)

    def _get_list_routines(self) -> Dict[str, List[str]]:
        """Returns the routines for list manipulation."""
        # ZP_PTR1 = $FB/$FC
        # ZP_PTR2 = $FD/$FE
        return {
            "get_list_element": [
                "; Routine to get an element from a list",
                "; Input:",
                ";   LIST_ROUTINE_ARG1: 16-bit pointer to the list",
                ";   LIST_ROUTINE_ARG2: 16-bit index",
                "; Output:",
                ";   LIST_ROUTINE_RET1: 16-bit value of the element",
                "GET_LIST_ELEMENT:",
                "; 1. Calculate offset = index * 2",
                "    LDA LIST_ROUTINE_ARG2",
                "    ASL A",
                "    STA $FB",
                "    LDA LIST_ROUTINE_ARG2+1",
                "    ROL A",
                "    STA $FC",
                "; 2. Add 1 to offset to get past the length byte",
                "    CLC",
                "    LDA $FB",
                "    ADC #1",
                "    STA $FB",
                "    BCC GET_ELEM_NO_CARRY",
                "    INC $FC",
                "GET_ELEM_NO_CARRY:",
                "; 3. Calculate final address = base_ptr + offset",
                "    CLC",
                "    LDA LIST_ROUTINE_ARG1",
                "    ADC $FB",
                "    STA $FD",
                "    LDA LIST_ROUTINE_ARG1+1",
                "    ADC $FC",
                "    STA $FE",
                "; 4. Dereference pointer to get the value",
                "    LDY #0",
                "    LDA ($FD),Y",
                "    STA LIST_ROUTINE_RET1",
                "    INY",
                "    LDA ($FD),Y",
                "    STA LIST_ROUTINE_RET1+1",
                "    RTS",
            ]
        }

    def get_used_routines_code(self) -> List[str]:
        """Returns the assembly code for all used routines."""
        code = []
        for routine_name in self.used_routines:
            if routine_name in self.available_routines:
                code.extend(self.available_routines[routine_name])
                code.append("")  # Blank line between routines

        return code

    def _get_graphics_package_data(self) -> Dict[str, List[str]]:
        """Returns the data tables for the graphics package."""
        return {
            'CB2F': [
                'CB2F: ; MULH table',
                '  .BYTE 0, 1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 15, 16',
                '  .BYTE 17, 18, 20, 21, 22, 23, 25, 26, 27, 28, 30, 31'
            ],
            'CB49': [
                'CB49: ; MULL table',
                '  .BYTE $00, $40, $80, $C0'
            ],
            'CB4D': [
                'CB4D: ; MSCTAB table',
                '  .BYTE %00000001, %00000010, %00000100, %00001000',
                '  .BYTE %00010000, %00100000, %01000000, %10000000'
            ]
        }

    def _get_scrolling_routines(self) -> Dict[str, List[str]]:
        """Returns the routines for scrolling."""
        return {
            'SCROLL': [
                'SCROLL:',
                '  JMP CCOO',
            ],
            'CCOO': [
                'CCOO: ; START',
                '  JSR CHKGET',
                '  TXA',
                '  LSR A',
                '  PHP',
                '  JSR CHKGET',
                '  CPX #25',
                '  BCC CC0D',
                '  LDX #24',
                'CC0D: STX 07F6',
                '  JSR CHKGET',
                '  CPX #25',
                '  BCC CC19',
                '  LDX #24',
                'CC19: STX 07F7',
                '  TXA',
                '  LDX 07F6',
                '  LDY 07F7',
                '  SEC',
                '  SBC 07F6',
                '  BCS CC33',
                '  EOR #$FF',
                '  LDX 07F7',
                '  LDY 07F6',
                'CC33: STA NUMBER',
                '  PLP',
                '  PHP',
                '  BCC CC3B',
                '  INY',
                'CC3A: TYA',
                '  TAX',
                'CC3B: LDA CCBB,X',
                '  STA ADDRESS+1',
                '  LDA CCE5,X',
                '  STA ADDRESS',
                '  PLP',
                '  PHP',
                '  BCC MOVE',
                '  SBC #1',
                '  STA ADDRESS',
                '  BCS MOVE',
                '  DEC ADDRESS+1',
                'MOVE:',
                '  LDA ADDRESS+1',
                '  AND #3',
                '  ORA #4',
                '  PLP',
                '  PHP',
                '  JSR CC86',
                '  PLP',
                '  PHP',
                '  LDA ADDRESS',
                '  BCC CC6D',
                '  ADC #39',
                '  STA ADDRESS',
                '  BCC CC6B',
                '  INC ADDRESS+1',
                '  BCS CC75',
                'CC6D: SBC #39',
                '  STA ADDRESS',
                '  BCS CC75',
                '  DEC ADDRESS+1',
                'CC75: LDA ADDRESS+1',
                '  AND #3',
                '  ORA #$D8',
                '  PLP',
                '  PHP',
                '  JSR CC86',
                '  DEC NUMBER',
                '  BPL MOVE',
                '  PLP',
                '  RTS',
                'CC86: ; MOVE1',
                '  STA ADDRESS+1',
                '  BCC CC8D',
                '  JMP CCAB',
                'CC8D: ; LEFT',
                '  LDY #0',
                '  LDA (ADDRESS),Y',
                '  TAX',
                '  LDY #39',
                'CC94: LDA (ADDRESS),Y',
                '  PHA',
                '  TXA',
                '  STA (ADDRESS),Y',
                '  PLA',
                '  TAX',
                '  DEY',
                '  BPL CC94',
                '  CLC',
                '  LDA ADDRESS',
                '  ADC #40',
                '  STA ADDRESS',
                '  BCC CCAA',
                '  INC ADDRESS+1',
                'CCAA: RTS',
                'CCAB: ; RIGHT',
                '  SEC',
                '  LDA ADDRESS',
                '  SBC #40',
                '  STA ADDRESS',
                '  BCS CCB6',
                '  DEC ADDRESS+1',
                'CCB6: LDY #40',
                '  LDA (ADDRESS),Y',
                '  TAX',
                '  LDY #1',
                'CCBD: LDA (ADDRESS),Y',
                '  PHA',
                '  TXA',
                '  STA (ADDRESS),Y',
                '  PLA',
                '  TAX',
                '  INY',
                '  CPY #41',
                '  BNE CCBD',
                '  RTS',
            ],
            'CCBB': [
                'CCBB: ; MULH table',
                '  .BYTE 4,4,4,4,4,4,4,5,5,5,5,5,5',
                '  .BYTE 6,6,6,6,6,6,6,7,7,7,7,7,7',
            ],
            'CCE5': [
                'CCE5: ; MULL table',
                '  .BYTE $00,$28,$50,$78,$A0,$C8,$F0,$18,$40,$68,$90,$B8,$E0',
                '  .BYTE $08,$30,$58,$80,$A8,$D0,$F8,$20,$48,$70,$98,$C0,$E8',
            ]
        }
