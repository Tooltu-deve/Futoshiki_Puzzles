from __future__ import annotations

from core.types import Puzzle


class KBGenerator:
    """
    Generates a Knowledge Base in CNF (Conjunctive Normal Form)
    using the DIMACS standard format (list of lists of integers).
    """

    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle
        self.n = puzzle.size
        self.clauses: list[list[int]] = []

    def var_id(self, r: int, c: int, v: int) -> int:
        """
        Maps a state Val(r, c, v) to a unique positive integer.
        r, c is 0-indexed. v is 1-indexed (1 to N).
        """
        return r * self.n * self.n + c * self.n + v

    def generate_cnf(self) -> list[list[int]]:
        self.clauses = []
        n = self.n

        # 1. Each cell has at least one value: Val(r, c, 1) V Val(r, c, 2) V ... V Val(r, c, N)
        for r in range(n):
            for c in range(n):
                clause = [self.var_id(r, c, v) for v in range(1, n + 1)]
                self.clauses.append(clause)

        # 2. Each cell has at most one value: ~Val(r, c, v1) V ~Val(r, c, v2)
        for r in range(n):
            for c in range(n):
                for v1 in range(1, n + 1):
                    for v2 in range(v1 + 1, n + 1):
                        self.clauses.append([-self.var_id(r, c, v1), -self.var_id(r, c, v2)])

                # 5. Given clues (Initial facts)
                if self.puzzle.grid[r][c] != 0:
                    v = self.puzzle.grid[r][c]
                    self.clauses.append([self.var_id(r, c, v)])

        # 3. Row Uniqueness: ~Val(r, c1, v) V ~Val(r, c2, v)
        for r in range(n):
            for v in range(1, n + 1):
                for c1 in range(n):
                    for c2 in range(c1 + 1, n):
                        self.clauses.append([-self.var_id(r, c1, v), -self.var_id(r, c2, v)])

        # 4. Column Uniqueness: ~Val(r1, c, v) V ~Val(r2, c, v)
        for c in range(n):
            for v in range(1, n + 1):
                for r1 in range(n):
                    for r2 in range(r1 + 1, n):
                        self.clauses.append([-self.var_id(r1, c, v), -self.var_id(r2, c, v)])

        # 6. Set Inequalities (Horizontal & Vertical)
        self._generate_inequalities()

        return self.clauses

    def _generate_inequalities(self) -> None:
        n = self.n
        # Horizontal constraints
        # 1 means left < right, -1 means left > right
        for r in range(n):
            for c in range(n - 1):
                sign = self.puzzle.horizontal[r][c]
                if sign == 1:  # Left < Right
                    for v1 in range(1, n + 1):
                        for v2 in range(1, n + 1):
                            if v1 >= v2:  # Invalid combination
                                self.clauses.append([-self.var_id(r, c, v1), -self.var_id(r, c + 1, v2)])
                elif sign == -1:  # Left > Right
                    for v1 in range(1, n + 1):
                        for v2 in range(1, n + 1):
                            if v1 <= v2:  # Invalid combination
                                self.clauses.append([-self.var_id(r, c, v1), -self.var_id(r, c + 1, v2)])

        # Vertical constraints
        # 1 means top < bottom, -1 means top > bottom
        for r in range(n - 1):
            for c in range(n):
                sign = self.puzzle.vertical[r][c]
                if sign == 1:  # Top < Bottom
                    for v1 in range(1, n + 1):
                        for v2 in range(1, n + 1):
                            if v1 >= v2:
                                self.clauses.append([-self.var_id(r, c, v1), -self.var_id(r + 1, c, v2)])
                elif sign == -1:  # Top > Bottom
                    for v1 in range(1, n + 1):
                        for v2 in range(1, n + 1):
                            if v1 <= v2:
                                self.clauses.append([-self.var_id(r, c, v1), -self.var_id(r + 1, c, v2)])


def generate_puzzle_kb(puzzle: Puzzle) -> list[list[int]]:
    """Helper function to instantiate KBGenerator and get CNF clauses."""
    generator = KBGenerator(puzzle)
    return generator.generate_cnf()
