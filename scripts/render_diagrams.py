#!/usr/bin/env python3
"""Render model-derived fragments under generated/: the figures (views from
the registry in ogc/views.py, each captioned with the perspective it
encodes, ruling R-38), the wiring tables, the SCI tables, the crosswalk and
the receipts. Everything is read from the canonical model graph
(model/og-caie.model.ttl, ruling R-22) and model/trace.ttl, never
hand-drawn, so the figures cannot drift from the model. Deterministic:
same graph, same bytes."""
import json
import subprocess
import sys
from pathlib import Path

from rdflib import RDF, RDFS, Graph, Namespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from prune_model import OGM, SYS  # noqa: E402
from ogc import views  # noqa: E402

GRAPH = ROOT / "model" / "og-caie.model.ttl"
MANIFEST = ROOT / "model" / "model_manifest.json"
MODEL = ROOT / "model" / "og-caie.sysml"
SYSML = ROOT / "toolchain" / "bin" / "sysml"
OUT = ROOT / "generated"
OGC = Namespace("https://w3id.org/og-caie/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")


def graph() -> Graph:
    g = Graph(); g.parse(GRAPH); return g


def name(g, n) -> str:
    return views.name(g, n)


def figure(view_name: str, g: Graph) -> str:
    """One view from the registry, captioned with the perspective it encodes (R-38)."""
    v = views.VIEWS[view_name]
    legend = ("" if view_name == "nesting" else
              " Legend: rounded green, a person; double-boxed pink, a machine; dashed amber, an affected population; "
              "a plain box, an organization; a solid arrow bundles the items that flow from one part to another; "
              "a dotted arrow is a relation that carries no item.")
    return views.mermaid(v.render(g)) + f"\n**View `{v.name}`: {v.title.lower()}.** {v.perspective()}{legend}\n"


def render_nesting() -> str:
    return figure("nesting", graph())


def render_wiring() -> str:
    return ("## The assemblage\n\nOrganizations are boxes containing their parts; people are rounded (green), machines are double-boxed (red), "
            "affected populations are dashed (amber); each solid edge bundles the seams from one part to another, labelled by the item kinds that flow; "
            "the dotted edge is a relation that carries no item.\n\n" + figure("assemblage", graph()))


def render_wiring_table() -> str:
    g = graph()
    rows = list(g.query((ROOT / "queries" / "wiring.rq").read_text()))
    lines = ["## Every wire, explained locally\n",
             "For each kind of part, each port: its direction, the item kind it carries, and the wire to the part and port at the other end "
             "(`queries/wiring.rq` over the model graph, ruling R-26). An input has one row; an output has one row per reader.\n",
             "| Part | Port | Direction | Carries | Wire | Other end |", "|---|---|---|---|---|---|"]
    for r in rows:
        arrow = "from" if str(r.direction) == "in" else "to"
        lines.append(f"| {r.part} | {r.port} | {r.direction} | {r.carries} | {r.wire} | {arrow} {r.otherPart}.{r.otherPort} |")
    return "\n".join(lines) + "\n"


def seam_chapter(g, s) -> str:
    return views.seam_slice(g, s)


def render_wiring_chapter(chapter: str) -> str:
    return figure(chapter, graph())


def render_wiring_table_chapter(chapter: str) -> str:
    g = graph()
    rows = list(g.query((ROOT / "queries" / "wiring.rq").read_text()))
    seams = {name(g, s) for s in g.subjects(RDF.type, SYS.InterfaceUsage) if seam_chapter(g, s) == chapter}
    lines = ["| Part | Port | Direction | Carries | Wire | Other end |", "|---|---|---|---|---|---|"]
    for r in rows:
        if str(r.wire) not in seams:
            continue
        arrow = "from" if str(r.direction) == "in" else "to"
        lines.append(f"| {r.part} | {r.port} | {r.direction} | {r.carries} | {r.wire} | {arrow} {r.otherPart}.{r.otherPort} |")
    return "\n".join(lines) + "\n"


def render_sci_chapter(chapter: str) -> str:
    g = trace_graph()
    lines = ["| ID | Statement | Checked by |", "|---|---|---|"]
    for t in sorted(g.subjects(RDF.type, OGC.Trace), key=str):
        if str(g.value(t, OGC.page)) != chapter:
            continue
        sid = str(t).rsplit("#", 1)[-1]
        shapes = ", ".join(sorted(str(s).rsplit("/", 1)[-1] for s in g.objects(t, OGC.checkedBy)))
        lines.append(f"| {sid} | {g.value(t, RDFS.comment)} | {shapes} |")
    return "\n".join(lines) + "\n"


def trace_graph() -> Graph:
    g = Graph()
    for f in ("model/trace.ttl", "vocabulary/og-caie.ttl", "sources/sources.ttl", "rulings/adjudications.ttl"):
        g.parse(ROOT / f)
    return g


def render_sci() -> str:
    g = trace_graph()
    rows = []
    for t in sorted(g.subjects(RDF.type, OGC.Trace), key=str):
        sid = str(t).rsplit("#", 1)[-1]
        label = str(g.value(t, RDFS.label)).split(" ", 1)[1]
        rows.append((sid, label, str(g.value(t, OGC.tag)), str(g.value(t, RDFS.comment))))
    n = len(rows)
    human = sum(1 for r in rows if "human" in r[2])
    lines = ["| ID | Name | Checked by | Statement |", "|---|---|---|---|"] + [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows]
    return (f"## The essentials\n\n{n} requirements: {n - human} verified by machine alone; {human} checked by machine for form, "
            "with the judgment itself made by a named person. They live in `model/trace.ttl`; SysML holds structure only (ruling R-22).\n\n"
            + "\n".join(lines) + "\n")


def render_trace() -> str:
    g = trace_graph()
    lines = ["## The crosswalk\n", "Each requirement, the shapes that check it (M over the model graph, S over the record), the glossary terms it is stated in, and what it rests on.\n",
             "| SCI | Checked by | Terms | Rests on |", "|---|---|---|---|"]
    for t in sorted(g.subjects(RDF.type, OGC.Trace), key=str):
        sid = str(t).rsplit("#", 1)[-1]
        shapes = ", ".join(sorted(str(s).rsplit("/", 1)[-1] for s in g.objects(t, OGC.checkedBy)))
        terms = ", ".join(sorted(str(g.value(x, SKOS.prefLabel)) for x in g.objects(t, OGC.usesTerm)))
        rests = ", ".join(sorted(str(x).rsplit("#", 1)[-1] for x in g.objects(t, OGC.restsOn)))
        lines.append(f"| {sid} ({g.value(t, OGC.tag)}) | {shapes} | {terms} | {rests} |")
    return "\n".join(lines) + "\n"


def receipt_validate() -> str:
    r = subprocess.run([str(SYSML), "model/og-caie.sysml", "-validate", "-strict"], cwd=ROOT, capture_output=True, text=True)
    body = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if l.strip())
    return f"### Strict validation of the authoring view\n\n```text\n$ sysml model/og-caie.sysml -validate -strict\n{body}\n(exit {r.returncode})\n```\n"


def receipt_graph() -> str:
    m = json.loads(MANIFEST.read_text())
    from pyshacl import validate
    g = graph(); shapes = Graph(); shapes.parse(ROOT / "shapes" / "model.shapes.ttl")
    ok, _, _ = validate(g, shacl_graph=shapes, advanced=True)
    n_shapes = len(set(shapes.subjects(RDF.type, Namespace("http://www.w3.org/ns/shacl#").NodeShape)))
    return ("### The canonical model graph\n\n"
            f"`sysml -convert ttl` renders {m['raw']['triples']} triples; the term map keeps {m['artifact']['triples']} "
            f"({m['artifact']['derived_triples']} of them resolved ends computed by `scripts/prune_model.py`), "
            f"within a budget of {m['triple_budget']['value']}. "
            f"Conformance of the graph to the {n_shapes} wiring shapes M1 to M5: **{'conforms' if ok else 'does not conform'}**.\n")


def render_receipts() -> str:
    return "## Receipts\n\n" + receipt_validate() + receipt_graph()


def main() -> int:
    OUT.mkdir(exist_ok=True)
    (OUT / "nesting.md").write_text(render_nesting())
    (OUT / "wiring.md").write_text(render_wiring())
    (OUT / "wiring-table.md").write_text(render_wiring_table())
    for ch in ("contracting", "evaluation"):
        (OUT / f"wiring-{ch}.md").write_text(render_wiring_chapter(ch))
        (OUT / f"wiring-table-{ch}.md").write_text(render_wiring_table_chapter(ch))
    for ch in ("contracting", "evaluation", "guarantees"):
        (OUT / f"sci-{ch}.md").write_text(render_sci_chapter(ch))
    (OUT / "sci.md").write_text(render_sci())
    (OUT / "receipts.md").write_text(render_receipts())
    (OUT / "trace.md").write_text(render_trace())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
