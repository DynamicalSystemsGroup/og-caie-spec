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
    (OUT / "record.md").write_text(render_record())
    return 0



def render_record() -> str:
    from pyshacl import validate
    EPO = Namespace("https://w3id.org/og-caie/epo#")
    g = Graph()
    for f in ("vocabulary/epo.ttl", "track/measles-run.ttl"):
        g.parse(ROOT / f)
    out = []
    # the chain
    out.append("### The chain\n")
    out.append("| Step | Node | Who | When |\n|---|---|---|---|")
    PROV = Namespace("http://www.w3.org/ns/prov#")
    EARL = Namespace("http://www.w3.org/ns/earl#")
    order = [EPO.DsoRelease, EPO.RequirementSet, EPO.Requirement, EPO.AcceptanceCriterion, EPO.TestPlan, EPO.Strategy, EPO.Probe,
             EPO.ConsistencyCheck, EPO.TestSuite, EPO.Session, EPO.Turn, EPO.Trajectory, EPO.Response, EPO.Evidence, EPO.Determination, EPO.Attestation, EPO.CoverageComputation, EPO.Report, EPO.Recommendation]
    for cls in order:
        for n in sorted(g.subjects(RDF.type, cls), key=str):
            who = [g.value(a, RDFS.label) or str(a).rsplit("#", 1)[-1] for p in (EARL.assertedBy, EPO.approvedBy, PROV.wasAttributedTo, PROV.wasAssociatedWith) for a in g.objects(n, p)]
            when = g.value(n, PROV.generatedAtTime) or g.value(n, PROV.startedAtTime) or g.value(n, PROV.endedAtTime) or ""
            step = g.value(n, EPO.step)
            step = cell(g.value(step, RDFS.label)).split(":")[0] if step else ""
            out.append(f"| {step} | `{str(n).rsplit('#', 1)[-1]}` ({cell(str(cls).rsplit('#', 1)[-1])}) | {cell('; '.join(dict.fromkeys(str(w) for w in who)))} | {cell(when)} |")
    # coverage
    (row,) = list(g.query((ROOT / "queries" / "coverage.rq").read_text()))
    report = next(g.subjects(RDF.type, EPO.Report))
    out.append("\n### Coverage and performance, recomputed\n")
    out.append("| Quantity | Stored in the report | Recomputed by queries/coverage.rq |\n|---|---|---|")
    for k, v in (("coverage", row.coverage), ("passRate", row.passRate), ("failRate", row.failRate), ("cantTellRate", row.cantTellRate)):
        out.append(f"| {k} | {cell(g.value(report, EPO[k]))} | {cell(v)} |")
    out.append(f"\nCovered criteria: {row.coveredCount} of 3; the third criterion is untested and counts for nothing.")
    # traceback
    rows = list(g.query((ROOT / "queries" / "traceback.rq").read_text()))
    out.append("\n### The recommendation, traced back\n")
    out.append("| Attestation (who) | Criterion | Expected result | Evidence | Determination (who; outcome) | Attested outcome | Experiment (turn, session, probe under plan; operator; system) | DSO release (approver) | EPO step |\n|---|---|---|---|---|---|---|---|")
    for r in rows:
        out.append(f"| `{str(r.attestation).rsplit('#', 1)[-1]}` ({cell(r.assertor)}) | {cell(r.criterion)} | {cell(r.expected)} | `{str(r.evidence).rsplit('#', 1)[-1]}` | `{str(r.determination).rsplit('#', 1)[-1]}` ({cell(r.determiner)}; {cell(r.determined)}) | {cell(r.outcome)} | turn {cell(r.turnIndex)} of `{str(r.run).rsplit('#', 1)[-1]}`, `{str(r.probe).rsplit('#', 1)[-1]}` under `{str(r.plan).rsplit('#', 1)[-1]}`; {cell(r.operator)}; {cell(r.sut)} | `{str(r.dso).rsplit('#', 1)[-1]}` ({cell(r.dsoApprover)}) | {cell(r.step)} |")
    # conformity and counterexamples
    shapes = Graph().parse(ROOT / "shapes" / "epo.shapes.ttl")
    SH = Namespace("http://www.w3.org/ns/shacl#")
    out.append("\n### Conformity\n")
    out.append("| Graph | Conforms | Shapes violated | Message |\n|---|---|---|---|")
    ok, results, _ = validate(g, shacl_graph=shapes, advanced=True)
    out.append(f"| `track/measles-run.ttl` | {ok} | | |")
    for cx in sorted((ROOT / "counterexamples").glob("*.ttl")):
        d = Graph().parse(ROOT / "vocabulary" / "epo.ttl"); d.parse(cx)
        ok, results, _ = validate(d, shacl_graph=shapes, advanced=True)
        shapes_hit = sorted({str(s).rsplit("/", 1)[-1] for s in results.objects(None, SH.sourceShape)})
        msgs = sorted({str(m) for m in results.objects(None, SH.resultMessage)})
        out.append(f"| `counterexamples/{cx.name}` | {ok} | {cell(', '.join(shapes_hit))} | {cell(' / '.join(msgs))} |")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    raise SystemExit(main_all())
