#!/usr/bin/env python3
"""Write the current digests into the record (sheet 10-18, R-50): the
conformance verdict of track/measles-evaluation.ttl names by sha256 the
shapes and the ontology it ran and the record it judged (epo:recordDigest,
the canonical member triples dated no later than the verdict, the verdict
itself excluded; round four, KG 8), and the two coverage computations name
the shapes, the ontology and the coverage query. The file digests are
stamped first, since the draft's coverage computation is part of what the
record digest covers. `ogc doctor` reports BAD when the record's digests
drift; run this after editing the shapes, the ontology, the query or the
record, then regenerate the counterexamples
(scripts/render_counterexamples.py), which copy the record. Textual: the
file's comments and layout survive."""
import re
import sys
from pathlib import Path

from rdflib import Graph

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ogc.graph import RECORD_FILE, digests, find_root, verdict_digest  # noqa: E402


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
    g = Graph().parse(data=text, format="turtle")
    for verdict, value in verdict_digest(g).items():
        new, n = re.subn(rf'(epo:recordDigest ")[^"]*(")', rf"\g<1>{value}\g<2>", text)
        if n != 1:
            raise SystemExit(f"{RECORD_FILE}: expected one epo:recordDigest to stamp, found {n}")
        changed += int(new != text)
        text = new
    path.write_text(text)
    return changed


if __name__ == "__main__":
    root = find_root()
    print(f"{RECORD_FILE}: digests {'updated' if stamp(root) else 'current'}")
