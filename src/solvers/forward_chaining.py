from __future__ import annotations

from core.types import Puzzle
from utils.tracer import Tracer


Cell = tuple[int, int]


def solve_forward_chaining(puzzle: Puzzle, tracer: Tracer | None = None) -> list[list[int]] | None:
    t = tracer or Tracer(enabled=False)
    n = puzzle.size
    domains: dict[Cell, set[int]] = {}

    given_count = 0
    for r in range(n):
        for c in range(n):
            given = puzzle.grid[r][c]
            if given == 0:
                domains[(r, c)] = set(range(1, n + 1))
            else:
                domains[(r, c)] = {given}
                given_count += 1
    t.header("Forward Chaining", f"N={n}")
    t.log(f"[init] given clues = {given_count}, empty cells = {n*n - given_count}")
    iter_no = 0

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
        iter_no += 1
        t.section(f"iter {iter_no}")
        r1 = r2 = r3 = r4 = 0

        # Rule 1: row/column uniqueness propagation from singletons.
        for r in range(n):
            fixed_values = {next(iter(domains[(r, c)])) for c in range(n) if len(domains[(r, c)]) == 1}
            for c in range(n):
                if len(domains[(r, c)]) == 1:
                    continue
                if prune((r, c), fixed_values):
                    changed = True
                    r1 += 1

        for c in range(n):
            fixed_values = {next(iter(domains[(r, c)])) for r in range(n) if len(domains[(r, c)]) == 1}
            for r in range(n):
                if len(domains[(r, c)]) == 1:
                    continue
                if prune((r, c), fixed_values):
                    changed = True
                    r1 += 1

        if has_empty_domain():
            t.log("  [FAIL] empty domain after singleton elim")
            return None

        # Rule 2: inequality constraints propagation.
        for r in range(n):
            for c in range(n - 1):
                relation = puzzle.horizontal[r][c]
                if relation == 1 and enforce_lt((r, c), (r, c + 1)):
                    changed = True
                    r2 += 1
                elif relation == -1 and enforce_lt((r, c + 1), (r, c)):
                    changed = True
                    r2 += 1

        for r in range(n - 1):
            for c in range(n):
                relation = puzzle.vertical[r][c]
                if relation == 1 and enforce_lt((r, c), (r + 1, c)):
                    changed = True
                    r2 += 1
                elif relation == -1 and enforce_lt((r + 1, c), (r, c)):
                    changed = True
                    r2 += 1

        if has_empty_domain():
            t.log("  [FAIL] empty domain after inequality AC")
            return None

        # Rule 3: hidden singles in each row.
        for r in range(n):
            for value in range(1, n + 1):
                cells = [(r, c) for c in range(n) if value in domains[(r, c)]]
                if len(cells) == 0:
                    t.log(f"  [FAIL] value {value} has no home in row {r}")
                    return None
                if len(cells) == 1 and assign(cells[0], value):
                    changed = True
                    r3 += 1
                    t.log(f"  hidden single  row {r}  ->  {cells[0]} = {value}")

        # Rule 4: hidden singles in each column.
        for c in range(n):
            for value in range(1, n + 1):
                cells = [(r, c) for r in range(n) if value in domains[(r, c)]]
                if len(cells) == 0:
                    t.log(f"  [FAIL] value {value} has no home in col {c}")
                    return None
                if len(cells) == 1 and assign(cells[0], value):
                    changed = True
                    r4 += 1
                    t.log(f"  hidden single  col {c}  ->  {cells[0]} = {value}")

        if has_empty_domain():
            t.log("  [FAIL] empty domain after hidden singles")
            return None

        solved_cells = sum(1 for d in domains.values() if len(d) == 1)
        t.log(f"  singleton elim   : pruned {r1}")
        t.log(f"  inequality AC    : pruned {r2}")
        t.log(f"  hidden single row: found  {r3}")
        t.log(f"  hidden single col: found  {r4}")
        t.log(f"  state            : {solved_cells}/{n*n} cells fixed")

    t.blank()
    if any(len(domain) != 1 for domain in domains.values()):
        t.log("[done] FAIL — fixpoint without full assignment, search required")
        return None
    t.log("[done] SUCCESS — all cells reduced to singletons")

    solved = [[0 for _ in range(n)] for _ in range(n)]
    for (r, c), domain in domains.items():
        solved[r][c] = next(iter(domain))
    return solved
