from typing import List

class PeepholeOptimizer:
    """Peephole optimizer to remove redundant assembly code."""

    def __init__(self):
        self.optimizations = [
            self._remove_redundant_jumps,
            self._remove_dead_loads,
        ]

    def optimize(self, assembly_lines: List[str]) -> List[str]:
        """Applies all optimizations."""
        optimized = assembly_lines[:]

        for optimization in self.optimizations:
            optimized = optimization(optimized)

        return optimized

    def _remove_redundant_jumps(self, lines: List[str]) -> List[str]:
        """Removes redundant JMP instructions."""
        result = []
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Look for pattern: JMP LABEL followed by LABEL:
            if (line.startswith("JMP ") and
                i + 1 < len(lines) and
                lines[i + 1].strip() == line[4:] + ":"):
                # Skip the redundant JMP
                i += 1
                continue

            result.append(lines[i])
            i += 1

        return result

    def _remove_dead_loads(self, lines: List[str]) -> List[str]:
        """Removes redundant LDA/STA instructions."""
        result = []
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Look for pattern: LDA addr followed by STA addr (same address)
            if (line.startswith("LDA ") and
                i + 1 < len(lines) and
                lines[i + 1].strip() == f"STA {line[4:]}"):
                # Skip both instructions
                i += 2
                continue

            result.append(lines[i])
            i += 1

        return result
