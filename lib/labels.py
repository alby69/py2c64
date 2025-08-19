from typing import Dict, Set

class LabelManager:
    """Gestisce la generazione di label univoche per assembly"""
    
    def __init__(self):
        self.counters: Dict[str, int] = {}
        self.used_labels: Set[str] = set()

    def generate_label(self, prefix: str = "L") -> str:
        """Genera una label univoca con il prefisso specificato"""
        if prefix not in self.counters:
            self.counters[prefix] = 0

        while True:
            label = f"{prefix}{self.counters[prefix]}"
            self.counters[prefix] += 1

            if label not in self.used_labels:
                self.used_labels.add(label)
                return label