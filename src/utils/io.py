from __future__ import annotations

from pathlib import Path

from core.types import Puzzle


def format_solution(puzzle: Puzzle, solved_grid: list[list[int]]) -> str:
    n = puzzle.size
    lines: list[str] = []

    for r in range(n):
        row_tokens: list[str] = []
        for c in range(n):
            row_tokens.append(str(solved_grid[r][c]))
            if c < n - 1:
                relation = puzzle.horizontal[r][c]
                if relation == 1:
                    row_tokens.append("<")
                elif relation == -1:
                    row_tokens.append(">")
                else:
                    row_tokens.append(" ")
        lines.append(" ".join(row_tokens).rstrip())

        if r < n - 1:
            vert_tokens: list[str] = []
            for c in range(n):
                relation = puzzle.vertical[r][c]
                if relation == 1:
                    vert_tokens.append("v")
                elif relation == -1:
                    vert_tokens.append("^")
                else:
                    vert_tokens.append(" ")
                if c < n - 1:
                    # Placeholder token for horizontal relation columns.
                    vert_tokens.append(" ")
            lines.append(" ".join(vert_tokens).rstrip())

    return "\n".join(lines)


def save_text_output(path: str | Path, content: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content + "\n", encoding="utf-8")
