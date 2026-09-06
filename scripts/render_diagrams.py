#!/usr/bin/env python3
"""Render the two figures under generated/ as Mermaid: the layered
OG-CAIE figure (from the glossary graph) and the assemblage wiring (from
the SysML model converted to Turtle). Both land in slice S2; until then
this emits nothing and exits 0 so the gate's regeneration step is honest
about what exists."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated"


def main() -> int:
    OUT.mkdir(exist_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
