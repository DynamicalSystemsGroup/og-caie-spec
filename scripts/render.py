#!/usr/bin/env python3
"""Render committed Markdown fragments under generated/ from the RDF graphs.
Deterministic: same graphs, same bytes. The gate diffs generated/ after
running this; the site includes the fragments."""
from pathlib import Path

from rdflib import RDF, Graph, Namespace

ROOT = Path(__file__).resolve().parents[1]
OGC = Namespace("https://w3id.org/og-caie/")
PROV = Namespace("http://www.w3.org/ns/prov#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
OUT = ROOT / "generated"


def cell(s: object) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def render_rulings() -> str:
    g = Graph().parse(ROOT / "rulings" / "adjudications.ttl")
    lines = ["| # | Concern | Severity | Status | Ruling (verbatim) | Adjudicator | Date | Change |",
             "|---|---|---|---|---|---|---|---|"]
    rulings = sorted(g.subjects(RDF.type, OGC.Ruling), key=lambda r: int(g.value(r, OGC.order)))
    for r in rulings:
        c = g.value(r, OGC.resolves)
        who = g.value(g.value(r, PROV.wasAttributedTo), RDFS.label)
        lines.append("| {} | **{}**: {} | {} | {} | {} | {} | {} | {} |".format(
            cell(g.value(r, OGC.order)),
            cell(str(c).rsplit("#", 1)[-1]), cell(g.value(c, RDFS.label)),
            cell(g.value(c, OGC.severity)), cell(g.value(c, OGC.status)),
            cell(g.value(r, OGC.rulingText)), cell(who),
            cell(g.value(r, PROV.generatedAtTime)), cell(g.value(r, OGC.changeNote))))
    open_ = [c for c in g.subjects(RDF.type, OGC.Concern) if str(g.value(c, OGC.status)) == "open"]
    lines.append("")
    lines.append(f"Open concerns: {len(open_)}.")
    return "\n".join(lines) + "\n"


def main() -> int:
    OUT.mkdir(exist_ok=True)
    (OUT / "rulings.md").write_text(render_rulings())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
