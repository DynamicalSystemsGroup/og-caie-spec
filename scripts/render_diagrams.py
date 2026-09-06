#!/usr/bin/env python3
"""Render model-derived fragments under generated/: the layered OG-CAIE
figure, the assemblage wiring diagram, the SCI table, the crosswalk and
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
    return str(g.value(n, SYS.declaredName))


def definitions(g, kind):
    return {name(g, d): d for d in g.subjects(RDF.type, kind) if g.value(d, SYS.owner) is not None and name(g, g.value(d, SYS.owner)) == "OGCAIE"}


def kind_of(g, d) -> str:
    """person, organization, machine or party, by walking specializes."""
    seen = set()
    while d is not None and d not in seen:
        seen.add(d)
        n = name(g, d)
        if n in ("Person", "Organization", "Machine"):
            return n.lower()
        d = g.value(d, SYS.specializes)
    return "party"


def steps(g):
    proc = definitions(g, SYS.ActionDefinition)["EvaluationProcess"]
    succ = {name(g, g.value(s, OGM["first"])): name(g, g.value(s, OGM["then"]))
            for s in g.subjects(RDF.type, SYS.SuccessionAsUsage) if g.value(s, SYS.owner) == proc}
    first = (set(succ) - set(succ.values())).pop()
    order = [first]
    while order[-1] in succ:
        order.append(succ[order[-1]])
    return order


def part_tree(g, holder_def, prefix=""):
    """Yield (path, usage, definition) for every part usage under a definition, depth first."""
    for u in sorted(g.subjects(SYS.owner, holder_def), key=lambda x: name(g, x)):
        if (u, RDF.type, SYS.PartUsage) not in g:
            continue
        d = g.value(u, SYS.type)
        path = f"{prefix}{name(g, u)}"
        yield path, u, d
        yield from part_tree(g, d, path + ".")


def mermaid(block: str) -> str:
    return "```{mermaid}\n" + block.strip() + "\n```\n"


def render_layers() -> str:
    g = graph()
    defs = definitions(g, SYS.PartDefinition)
    people = sorted(n for n, d in defs.items() if kind_of(g, d) == "person")
    machines = sorted(n for n, d in defs.items() if kind_of(g, d) == "machine")
    orgs = sorted(n for n, d in defs.items() if kind_of(g, d) == "organization" and n != "Organization")
    chain = " --> ".join(f"s{i}[{s}]" for i, s in enumerate(steps(g)))
    m = f"""flowchart TB
  subgraph PARTIES["Parties: {', '.join(orgs)}; affected populations"]
    direction LR
    agree[service agreement] --> reqs[requirement set]
  end
  subgraph EPO["Evaluation Process Ontology: the standard operating procedure, fixed across domains"]
    direction LR
    {chain}
  end
  subgraph DSO["Domain-Specific Ontology: the expert-supplied parameter, one per domain"]
    direction LR
    de[DomainExpert] -- supplies or approves --> dso[(DsoRelease)]
  end
  subgraph EXEC["Execution: the human and machine assemblage performs EPO with DSO"]
    direction LR
    H["people: {', '.join(people)}"]
    M["machines: {', '.join(machines)}"]
    H --- rec[(evaluation record)]
    M --- rec
  end
  subgraph INTERP["Interpretation: named humans judge; every judgment traces back"]
    direction LR
    det[determinations on evidence: passed, failed, cantTell] --> att[attestations: outcome, appropriateness, sufficiency]
    att --> recmd[recommendation]
    recmd -. evidence collected .-> rec
    recmd -. experiments run: sessions, turns, probes under the test plan .-> rec
    recmd -. assessments and who made them .-> att
    recmd -. DSO release and who approved it .-> dso
    recmd -. EPO step .-> EPO
  end
  PARTIES ==> EPO
  EPO ==> EXEC
  DSO ==> EXEC
  EXEC ==> INTERP
"""
    return "## The layers\n\n" + mermaid(m)


def render_wiring() -> str:
    g = graph()
    assembly = definitions(g, SYS.PartDefinition)["OgCaieEvaluation"]
    lines = ["flowchart LR"]
    ids = {}
    classes = {"person": [], "machine": [], "organization": [], "party": []}

    def node(path, u, d):
        nid = path.replace(".", "_")
        ids[path] = nid
        k = kind_of(g, d)
        label = f"{name(g, u)} : {name(g, d)}"
        shape = {"person": f'{nid}(["{label}"])', "machine": f'{nid}[["{label}"]]', "party": f'{nid}{{{{"{label}"}}}}'}.get(k, f'{nid}["{label}"]')
        classes[k].append(nid)
        return shape

    tree = list(part_tree(g, assembly))
    top = [(p, u, d) for p, u, d in tree if "." not in p]
    for path, u, d in top:
        children = [(p, cu, cd) for p, cu, cd in tree if p.startswith(path + ".")]
        if children:
            lines.append(f'  subgraph {ids.setdefault(path, path)}["{name(g, u)} : {name(g, d)}"]')
            classes[kind_of(g, d)].append(path)
            for cp, cu, cd in children:
                grand = [(p2, u2, d2) for p2, u2, d2 in tree if p2.startswith(cp + ".")]
                if grand:
                    lines.append(f'    subgraph {cp.replace(".", "_")}["{name(g, cu)} : {name(g, cd)}"]')
                    for gp, gu, gd in grand:
                        lines.append("      " + node(gp, gu, gd))
                    lines.append("    end")
                elif cp.count(".") == 1:
                    lines.append("    " + node(cp, cu, cd))
            lines.append("  end")
        else:
            lines.append("  " + node(path, u, d))
    seams = sorted(g.subjects(RDF.type, SYS.InterfaceUsage), key=lambda s: name(g, s))
    for s in seams:
        sp, cp = g.value(s, OGM.supplierPort), g.value(s, OGM.consumerPort)
        src = next(p for p, u, d in tree if d == g.value(sp, SYS.owner))
        dst = next(p for p, u, d in tree if d == g.value(cp, SYS.owner))
        lines.append(f'  {ids[src]} -- "{name(g, s)}" --> {ids[dst]}')
    lines.append("  classDef person fill:#e8f5e9,stroke:#2e7d32;")
    lines.append("  classDef machine fill:#fce4ec,stroke:#ad1457;")
    lines.append("  classDef party fill:#fff8e1,stroke:#f9a825,stroke-dasharray: 4 4;")
    for k in ("person", "machine", "party"):
        if classes[k]:
            lines.append(f"  class {','.join(classes[k])} {k};")
    return ("## The assemblage\n\nOrganizations are boxes containing their parts; people are rounded (green), machines are double-boxed (red), "
            "affected populations are dashed (amber); every edge is one seam, named as in the model, from supplier port to conjugate consumer port.\n\n"
            + mermaid("\n".join(lines)))


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
    (OUT / "layers.md").write_text(render_layers())
    (OUT / "wiring.md").write_text(render_wiring())
    (OUT / "sci.md").write_text(render_sci())
    (OUT / "receipts.md").write_text(render_receipts())
    (OUT / "trace.md").write_text(render_trace())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
