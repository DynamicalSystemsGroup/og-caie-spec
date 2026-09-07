#!/usr/bin/env python3
"""Render generated/cli/<name>.md: what an `ogc` command prints, for the code
blocks on the chapter pages (ruling R-47, sheet 06, items 06-03 and 06-15:
what a page says a command prints must be what it prints).

Each fragment is the command as its first line and the output beneath, byte
for byte, with two exceptions the fragment states: the commit stamp on the
header line (`@ <sha>`) is replaced by the fixed token `<sha>`, because
the gate regenerates every fragment and diffs it byte for byte across
commits; and a trimmed fragment says how many lines it left out. The last
line is the exit code, as the receipts print it. Deterministic: same
graphs, same bytes."""
import re
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated" / "cli"
HEADER = re.compile(r"^(# ogc .*) @ \S+$")
SHA_TOKEN = "<sha>"

# name -> (arguments after `ogc`, trim): trim is None for the whole output, or
# (start, stop): keep the header line, then the lines from the first line
# that starts with `start` (None: the first) up to the first line that starts
# with `stop` (None: the end), and say how many lines were left out.
COMMANDS: dict[str, tuple[list[str], tuple[str | None, str | None] | None]] = {
    "check-word-system-under-test": (["check-word", "system under test"], None),
    "sci-10": (["sci", "SCI-10"], None),
    "term-statement-of-work": (["term", "statement of work"], None),
    "steps-determine-and-attest": (["steps"], ("## 5 determine", "## 6 report")),
    "sci-06": (["sci", "SCI-06"], None),
    "view-nesting": (["view", "nesting"], (None, "```mermaid")),
    "shape-s0-layers": (["shape", "S0-Layers"], None),
    "execute": (["execute"], None),
    "execute-mutate-skip-access": (["execute", "--mutate", "skip-access"], None),
}


def run(args: list[str]) -> tuple[list[str], int]:
    p = subprocess.run([sys.executable, "-m", "ogc", *args], cwd=ROOT, capture_output=True, text=True)
    return p.stdout.rstrip("\n").split("\n"), p.returncode


def normalise(lines: list[str]) -> list[str]:
    return [HEADER.sub(rf"\1 @ {SHA_TOKEN}", l) for l in lines]


def trim(lines: list[str], spec: tuple[str | None, str | None] | None) -> list[str]:
    if spec is None:
        return lines
    start, stop = spec
    head, body = lines[:1], lines[1:]
    i = next((k for k, l in enumerate(body) if l.startswith(start)), 0) if start else 0
    j = next((k for k, l in enumerate(body) if l.startswith(stop)), len(body)) if stop else len(body)
    kept = body[i:j]
    while kept and not kept[-1].strip():
        kept.pop()
    out = head
    if i:
        out.append(f"({i} lines omitted)")
    out += kept
    if len(body) - j:
        out.append(f"({len(body) - j} lines omitted)")
    return out


def fragment(name: str) -> str:
    args, spec = COMMANDS[name]
    lines, code = run(args)
    lines = trim(normalise(lines), spec)
    command = "$ uv run -q ogc " + shlex.join(args)
    return "\n".join([command, *lines, f"(exit {code})"]) + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in COMMANDS:
        (OUT / f"{name}.md").write_text(fragment(name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
