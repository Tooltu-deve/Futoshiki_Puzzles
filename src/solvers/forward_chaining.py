from __future__ import annotations

from core.types import Puzzle


Cell = tuple[int, int]


def solve_forward_chaining(puzzle: Puzzle) -> list[list[int]] | None:
    n = puzzle.size
    domains: dict[Cell, set[int]] = {}

    for r in range(n):
        for c in range(n):
            given = puzzle.grid[r][c]
            if given == 0:
                domains[(r, c)] = set(range(1, n + 1))
            else:
                domains[(r, c)] = {given}

    def prune(cell: Cell, values_to_remove: set[int]) -> bool:
        current = domains[cell]
        new_domain = current - values_to_remove
        if new_domain == current:
            return False
        domains[cell] = new_domain
        return True

    def assign(cell: Cell, value: int) -> bool:
        if value not in domains[cell]:
            domains[cell] = set()
            return True
        if domains[cell] == {value}:
            return False
        domains[cell] = {value}
        return True

    def has_empty_domain() -> bool:
        return any(len(domain) == 0 for domain in domains.values())

    def enforce_lt(left: Cell, right: Cell) -> bool:
        left_domain = domains[left]
        right_domain = domains[right]
        changed = False

        new_left = {x for x in left_domain if any(x < y for y in right_domain)}
        if new_left != left_domain:
            domains[left] = new_left
            changed = True

        left_domain = domains[left]
        right_domain = domains[right]
        new_right = {y for y in right_domain if any(x < y for x in left_domain)}
        if new_right != right_domain:
            domains[right] = new_right
            changed = True

        return changed

    changed = True
    while changed:
        changed = False

        # Rule 1: row/column uniqueness propagation from singletons.
        for r in range(n):
            fixed_values = {next(iter(domains[(r, c)])) for c in range(n) if len(domains[(r, c)]) == 1}
            for c in range(n):
                if len(domains[(r, c)]) == 1:
                    continue
                if prune((r, c), fixed_values):
                    changed = True

        for c in range(n):
            fixed_values = {next(iter(domains[(r, c)])) for r in range(n) if len(domains[(r, c)]) == 1}
            for r in range(n):
                if len(domains[(r, c)]) == 1:
                    continue
                if prune((r, c), fixed_values):
                    changed = True

        if has_empty_domain():
            return None

        # Rule 2: inequality constraints propagation.
        for r in range(n):
            for c in range(n - 1):
                relation = puzzle.horizontal[r][c]
                if relation == 1 and enforce_lt((r, c), (r, c + 1)):
                    changed = True
                elif relation == -1 and enforce_lt((r, c + 1), (r, c)):
                    changed = True

        for r in range(n - 1):
            for c in range(n):
                relation = puzzle.vertical[r][c]
                if relation == 1 and enforce_lt((r, c), (r + 1, c)):
                    changed = True
                elif relation == -1 and enforce_lt((r + 1, c), (r, c)):
                    changed = True

        if has_empty_domain():
            return None

        # Rule 3: hidden singles in each row.
        for r in range(n):
            for value in range(1, n + 1):
                cells = [(r, c) for c in range(n) if value in domains[(r, c)]]
                if len(cells) == 0:
                    return None
                if len(cells) == 1 and assign(cells[0], value):
                    changed = True

        # Rule 4: hidden singles in each column.
        for c in range(n):
            for value in range(1, n + 1):
                cells = [(r, c) for r in range(n) if value in domains[(r, c)]]
                if len(cells) == 0:
                    return None
                if len(cells) == 1 and assign(cells[0], value):
                    changed = True

        if has_empty_domain():
            return None

    if any(len(domain) != 1 for domain in domains.values()):
        return None

    solved = [[0 for _ in range(n)] for _ in range(n)]
    for (r, c), domain in domains.items():
        solved[r][c] = next(iter(domain))
    return solved
