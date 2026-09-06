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


def main(argv):
    term, locator, date = argv[0], argv[1], argv[2]
    src = argv[argv.index("--source") + 1] if "--source" in argv else "iso-9000-2026"
    path = VOCAB
    head = f"term:{term} a skos:Concept"
    if ":" in term:  # a step in vocabulary/epo.ttl, e.g. epo:agree
        path = ROOT / "vocabulary" / "epo.ttl"
        head = f"{term} a epo:EpoStep"
    t = path.read_text()
    start = t.index(head)
    end = t.find("\nterm:" if ":" not in term else "\nepo:", start + 1)
    block = t[start:end if end > 0 else len(t)]
    pat = re.compile(r'(ogc:cites src:' + re.escape(src) + r' ; ogc:locator "' + re.escape(locator) + r'"[^\]]*?ogc:quoteStatus ")pending(")')
    new, n = pat.subn(r'\1human" ; ogc:verifiedBy rul:Z ; ogc:verifiedOn "' + date + r'"^^xsd:date' + "", block)
    # the replacement above leaves a stray closing quote from group 2; fix it
    new = new.replace('^^xsd:date"', '^^xsd:date')
    assert n == 1, f"{n} pending citations matched for {term} / {locator}"
    path.write_text(t[:start] + new + t[start + len(block):])
    # tick the first matching untouched row on any rulings sheet; warn if none
    ticked = False
    for sheet in sorted((ROOT / "rulings" / "sheets").glob("*.md")):
        s = sheet.read_text()
        row = re.compile(r"^(\|[^\n]*\| " + re.escape(locator) + r" \|[^\n]*\| )\[ \] \|$", re.M)
        s2, m = row.subn(r"\1[x] " + date + " |", s, count=1)
        if m:
            sheet.write_text(s2); ticked = True; break
    if not ticked:
        print(f"warning: no sheet row for {term} / {locator}; vocabulary ticked only")
    print(f"ticked {term} {locator} ({src}) on {date}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
