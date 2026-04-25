from __future__ import annotations


class Tracer:
    DEFAULT_CAP = 5000
    INDENT = "  "

    def __init__(self, enabled: bool = False, cap: int = DEFAULT_CAP):
        self.enabled = enabled
        self.cap = cap
        self.steps: list[str] = []
        self.dropped = 0
        self.depth = 0

    def push(self) -> None:
        self.depth += 1

    def pop(self) -> None:
        if self.depth > 0:
            self.depth -= 1

    def _append(self, line: str) -> None:
        if len(self.steps) >= self.cap:
            self.dropped += 1
            return
        self.steps.append(line)

    def log(self, msg: str) -> None:
        if not self.enabled:
            return
        self._append(self.INDENT * self.depth + msg)

    def header(self, title: str, subtitle: str = "") -> None:
        if not self.enabled:
            return
        bar = "═" * 56
        self._append(bar)
        line = f"  {title}"
        if subtitle:
            line += f"   ({subtitle})"
        self._append(line)
        self._append(bar)

    def section(self, title: str) -> None:
        if not self.enabled:
            return
        self._append("")
        self._append(f"── {title} " + "─" * max(0, 52 - len(title)))

    def blank(self) -> None:
        if not self.enabled:
            return
        self._append("")

    def render(self) -> str:
        if not self.steps:
            return ""
        body = "\n".join(self.steps)
        if self.dropped:
            body += f"\n\n... ({self.dropped} more steps omitted, cap={self.cap})"
        return body
