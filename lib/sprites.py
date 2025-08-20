from typing import Dict, List

def get_sprite_routines() -> Dict[str, List[str]]:
    """Returns the routines for sprites."""
    return {
        "sprite_enable": [
            "sprite_enable:",
            "    LDA SPRITE_MASK",
            "    ORA $D015",
            "    STA $D015",
            "    RTS"
        ],
        "sprite_disable": [
            "sprite_disable:",
            "    LDA SPRITE_MASK",
            "    EOR #$FF",
            "    AND $D015",
            "    STA $D015",
            "    RTS"
        ],
        "sprite_set_pos": [
            "sprite_set_pos:",
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
