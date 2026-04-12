from __future__ import annotations

from pathlib import Path

from core.types import Puzzle


def _clean_lines(raw_text: str) -> list[str]:
    lines: list[str] = []
    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped)
    return lines


def _parse_row(line: str, expected_len: int) -> list[int]:
    parts = [part.strip() for part in line.split(",")]
    if len(parts) != expected_len:
        raise ValueError(f"Expected {expected_len} columns, got {len(parts)} in line: {line}")

    values: list[int] = []
    for part in parts:
        try:
            values.append(int(part))
        except ValueError as exc:
            raise ValueError(f"Invalid integer value: {part}") from exc
    return values


def parse_input_text(content: str) -> Puzzle:
    lines = _clean_lines(content)

    if not lines:
        raise ValueError("Input file is empty.")

    n = int(lines[0])
    cursor = 1

    if len(lines) < 1 + n + n + (n - 1):
        raise ValueError("Input file does not have enough rows for grid and constraints.")

    grid = [_parse_row(lines[cursor + i], n) for i in range(n)]
    cursor += n

    horizontal = [_parse_row(lines[cursor + i], n - 1) for i in range(n)]
    cursor += n

    vertical = [_parse_row(lines[cursor + i], n) for i in range(n - 1)]

    return Puzzle(size=n, grid=grid, horizontal=horizontal, vertical=vertical)


def parse_input_file(path: str | Path) -> Puzzle:
    file_path = Path(path)
    content = file_path.read_text(encoding="utf-8")
    return parse_input_text(content)
