# lib/labels.py
"""Manages the generation of unique labels for assembly code."""

class LabelManager:
    """Generates unique labels for assembly code."""
    def __init__(self):
        self.counters = {}

    def generate_label(self, prefix: str = "L") -> str:
        """Generates a new unique label with the given prefix."""
        count = self.counters.get(prefix, 0)
        self.counters[prefix] = count + 1
        return f"{prefix}_{count}"
