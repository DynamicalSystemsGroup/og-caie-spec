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




SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")


def render_glossary() -> str:
    g = Graph()
    for f in ("vocabulary/og-caie.ttl", "sources/sources.ttl"):
        g.parse(ROOT / f)
    order = {"adopted": 0, "refined": 1, "coined": 2}
    terms = sorted(g.subjects(RDF.type, SKOS.Concept),
                   key=lambda t: (order[str(g.value(t, OGC["class"]))], str(g.value(t, SKOS.prefLabel)).lower()))
    lines = ["| Term | Class | Narrative definition | Canonical source (locator; quote) | Status | Binding |",
             "|---|---|---|---|---|---|"]
    for t in terms:
        c = g.value(t, OGC.canonical)
        src = g.value(c, OGC.cites)
        label = str(g.value(src, RDFS.label)).split(" (")[0].split(", ")[0]
        alts = sorted(str(a) for a in g.objects(t, SKOS.altLabel))
        name = cell(g.value(t, SKOS.prefLabel)) + (f" *(also: {', '.join(alts)})*" if alts else "")
        rel = g.value(t, OGC.anchorRelation)
        klass = cell(g.value(t, OGC["class"])) + (f" ({rel})" if rel else "")
        quote = g.value(c, OGC.quote)
        cite = f"{label}, {cell(g.value(c, OGC.locator))}" + (f': "{cell(quote)}"' if quote else "")
        status = cell(g.value(c, OGC.quoteStatus) or "n/a")
        note = g.value(t, OGC.scopeNote)
        definition = cell(g.value(t, SKOS.definition)) + (f" *Note: {cell(note)}*" if note else "")
        lines.append(f"| **{name}** | {klass} | {definition} | {cite} | {status} | {cell(g.value(t, OGC.binding))} |")
    counts = {k: sum(1 for t in terms if str(g.value(t, OGC["class"])) == k) for k in order}
    lines.append("")
    lines.append(f"{len(terms)} terms: {counts['adopted']} adopted, {counts['refined']} refined, {counts['coined']} coined.")
    return "\n".join(lines) + "\n"


def render_sources() -> str:
    g = Graph().parse(ROOT / "sources" / "sources.ttl")
    rank_order = {"1": 0, "2": 1, "3": 2, "4": 3, "reserve": 4, "internal": 5}
    srcs = sorted(g.subjects(RDF.type, OGC.Source), key=lambda s: (rank_order[str(g.value(s, OGC.rank))], str(s)))
    lines = ["| Rank | Source | Posture | Snapshots | Licence note |", "|---|---|---|---|---|"]
    for s in srcs:
        n = sum(1 for _ in g.objects(s, OGC.snapshot))
        lines.append(f"| {cell(g.value(s, OGC.rank))} | {cell(g.value(s, RDFS.label))} | {cell(g.value(s, OGC.posture))} | {n} | {cell(g.value(s, OGC.licenceNote))} |")
    return "\n".join(lines) + "\n"


def main_all() -> int:
    OUT.mkdir(exist_ok=True)
    (OUT / "rulings.md").write_text(render_rulings())
    (OUT / "glossary.md").write_text(render_glossary())
    (OUT / "sources.md").write_text(render_sources())
    return 0


if __name__ == "__main__":
    raise SystemExit(main_all())
