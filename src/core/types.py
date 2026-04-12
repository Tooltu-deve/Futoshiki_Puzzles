from dataclasses import dataclass


@dataclass
class Puzzle:
    size: int
    grid: list[list[int]]
    horizontal: list[list[int]]
    vertical: list[list[int]]
