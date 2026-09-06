#!/usr/bin/env python3
"""Mark one pending quote as human-verified by Z on a date, in place, and
tick the matching row of the rulings sheet. Usage:
  tick.py <term-slug> <locator> <YYYY-MM-DD> [--source <slug>]
The Turtle is edited textually so blank-node citations keep their layout."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOCAB = ROOT / "vocabulary" / "og-caie.ttl"
SHEET = ROOT / "rulings" / "sheets" / "01-pending-verification.md"


def main(argv):
    term, locator, date = argv[0], argv[1], argv[2]
    src = argv[argv.index("--source") + 1] if "--source" in argv else "iso-9000-2026"
    t = VOCAB.read_text()
    start = t.index(f"term:{term} a skos:Concept")
    end = t.find("\nterm:", start + 1)
    block = t[start:end if end > 0 else len(t)]
    pat = re.compile(r'(ogc:cites src:' + re.escape(src) + r' ; ogc:locator "' + re.escape(locator) + r'"[^\]]*?ogc:quoteStatus ")pending(")')
    new, n = pat.subn(r'\1human" ; ogc:verifiedBy rul:Z ; ogc:verifiedOn "' + date + r'"^^xsd:date' + "", block)
    # the replacement above leaves a stray closing quote from group 2; fix it
    new = new.replace('^^xsd:date"', '^^xsd:date')
    assert n == 1, f"{n} pending citations matched for {term} / {locator}"
    VOCAB.write_text(t[:start] + new + t[start + len(block):])
    s = SHEET.read_text()
    row = re.compile(r"^(\| \d+ \| " + re.escape(term.replace("-", " ")) + r" \| " + re.escape(src) + r" \| " + re.escape(locator) + r" \|.*\| )\[ \] \|$", re.M)
    s, m = row.subn(r"\1[x] " + date + " |", s)
    assert m == 1, f"{m} sheet rows matched for {term}"
    SHEET.write_text(s)
    print(f"ticked {term} {locator} ({src}) on {date}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
