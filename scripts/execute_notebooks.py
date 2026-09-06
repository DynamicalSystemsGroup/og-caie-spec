"""Execute the "Checked" notebooks with nbclient and keep them fresh.

The site renders the committed outputs (MyST does not execute at build
time), so the committed outputs must equal a fresh execution, cell for
cell, and the last output must be the verdict line. Two modes:

    uv run python scripts/execute_notebooks.py            # execute in place (authoring)
    uv run python scripts/execute_notebooks.py --check    # gate: exit 1 if any notebook is stale

The gate and tests/test_notebooks.py both use check(); the functions here
are the one definition of "fresh".
"""
from __future__ import annotations

import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted((ROOT / "notebooks").glob("checked-*.ipynb"))
VERDICT = "NOTEBOOK: PASS"


def execute(path: Path) -> nbformat.NotebookNode:
    """A fresh execution of one notebook, run from notebooks/ (where the
    shared module lives), without execution timestamps in the metadata."""
    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(nb, timeout=600, kernel_name="python3", record_timing=False,
                            resources={"metadata": {"path": str(path.parent)}})
    client.execute()  # raises CellExecutionError on the first failing cell
    return nb


def cell_text(cell) -> str:
    """The text a reader sees under one code cell (streams and text/plain)."""
    chunks = []
    for out in cell.get("outputs", []):
        if out.get("output_type") == "stream":
            chunks.append(out.get("text", ""))
        elif out.get("output_type") == "error":
            chunks.append("\n".join(out.get("traceback", [])))
        else:
            data = out.get("data", {})
            for mime in ("text/markdown", "text/html", "text/plain"):
                if mime in data:
                    chunks.append(data[mime])
                    break
    return "".join(chunks)


def outputs(nb) -> list[str]:
    return [cell_text(c) for c in nb.cells if c.cell_type == "code"]


def stale(path: Path, fresh=None) -> list[str]:
    """Reasons the committed notebook is not fresh; empty when it is."""
    committed = nbformat.read(path, as_version=4)
    fresh = fresh if fresh is not None else execute(path)
    reasons = []
    a, b = outputs(committed), outputs(fresh)
    if len(a) != len(b):
        reasons.append(f"{path.name}: {len(a)} committed code cells, {len(b)} executed")
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            reasons.append(f"{path.name}: code cell {i} output differs from a fresh execution")
    last = b[-1].rstrip().splitlines()[-1] if b and b[-1].strip() else ""
    if last != VERDICT:
        reasons.append(f"{path.name}: last output line is {last!r}, not {VERDICT!r}")
    return reasons


def check() -> int:
    problems = []
    for path in NOTEBOOKS:
        reasons = stale(path)
        print(f"{path.relative_to(ROOT)}: {'fresh' if not reasons else 'STALE'}")
        problems += reasons
    for r in problems:
        print("  " + r)
    if not NOTEBOOKS:
        print("no notebooks/checked-*.ipynb found")
        return 1
    return 1 if problems else 0


def write_in_place() -> int:
    for path in NOTEBOOKS:
        nbformat.write(execute(path), path)
        print(f"{path.relative_to(ROOT)}: executed and written")
    return 0


if __name__ == "__main__":
    raise SystemExit(check() if "--check" in sys.argv[1:] else write_in_place())
