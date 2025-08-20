from typing import Dict, List

def get_sprite_routines() -> Dict[str, List[str]]:
    """Returns a dictionary of all sprite-related assembly routines."""
    return {
        "sprite_enable": [
            "sprite_enable:",
            "    ; Input: A = sprite mask",
            "    ORA $D015",
            "    STA $D015",
            "    RTS"
        ],
        "sprite_disable": [
            "sprite_disable:",
            "    ; Input: A = sprite mask",
            "    EOR #$FF",
            "    AND $D015",
            "    STA $D015",
            "    RTS"
        ],
        "sprite_set_pos": [
            "sprite_set_pos:",
            "    ; Input: X = sprite number, A = x_pos, Y = y_pos",
            "    TXA",
            "    ASL",
            "    TAX",
            "    LDA X_POS_REG",
            "    STA $D000,X",
            "    LDA Y_POS_REG",
            "    STA $D001,X",
            "    RTS"
        ],
        "sprite_set_color": [
            "sprite_set_color:",
            "    ; Input: X = sprite number, A = color",
            "    STA $D027,X",
            "    RTS"
        ],
        "sprite_set_multicolor": [
            "sprite_set_multicolor:",
            "    ; Input: A = sprite mask",
            "    ORA $D01C",
            "    STA $D01C",
            "    RTS"
        ],
        "sprite_set_priority": [
            "sprite_set_priority:",
            "    ; Input: A = sprite mask",
            "    ORA $D01B",
            "    STA $D01B",
            "    RTS"
        ],
        "sprite_expand_y": [
            "sprite_expand_y:",
            "    ; Input: A = sprite mask",
            "    ORA $D017",
            "    STA $D017",
            "    RTS"
        ],
        "sprite_expand_x": [
            "sprite_expand_x:",
            "    ; Input: A = sprite mask",
            "    ORA $D01D",
            "    STA $D01D",
            "    RTS"
        ]
    }
