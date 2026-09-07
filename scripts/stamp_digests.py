#!/usr/bin/env python3
"""Write the current digests of the shapes, the ontology and the coverage
query into the record (sheet 10-18, R-50): the conformance verdict and the
coverage computation of track/measles-evaluation.ttl name by sha256 what
they ran. `ogc doctor` reports BAD when the record's digests drift from the
files; run this after editing any of the three, then regenerate the
counterexamples (scripts/render_counterexamples.py), which copy the record.
Textual: the file's comments and layout survive."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ogc.graph import RECORD_FILE, digests, find_root  # noqa: E402


def stamp(root: Path) -> int:
    path = root / RECORD_FILE
    text = path.read_text()
    changed = 0
    for key, value in digests(root).items():
        new, n = re.subn(rf'(epo:{key} ")[^"]*(")', rf"\g<1>{value}\g<2>", text)
        if n == 0:
            raise SystemExit(f"{RECORD_FILE}: no epo:{key} to stamp")
        changed += int(new != text)
        text = new
    path.write_text(text)
    return changed


if __name__ == "__main__":
    root = find_root()
    print(f"{RECORD_FILE}: digests {'updated' if stamp(root) else 'current'}")
