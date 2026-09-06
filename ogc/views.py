"""Reusable views of the canonical model graph (ruling R-38).

A view is a named perspective on model/og-caie.model.ttl: a title, what it
brings into focus, what it leaves out, and a renderer that reads only the
graph. Diagrams are views for humans, so each keeps its density to the
point it makes: wires between the same two parts in the same direction are
braided into one bundle, labelled by the item kinds that flow in the order
the process produces them; relations that carry no item (the sponsor's
obligation to the affected populations) are drawn dotted. `ogc views` lists
the registry, `ogc view <name>` prints one view's mermaid with its
perspective, and scripts/render_diagrams.py writes the site's figures from
the same functions, so a figure cannot say what the model does not.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from rdflib import RDF, Graph, Namespace

SYS = Namespace("https://www.omg.org/spec/SysML#")
OGM = Namespace("https://w3id.org/og-caie/model#")
ASSEMBLY = "OgCaieEvaluation"
TOP_PACKAGE = "OGCAIE"
OUTER_PROCESS = "ContractingProcess"
INNER_PROCESS = "EvaluationProcess"
CONTRACT_KINDS = {"Mission", "Need", "Proposal", "ServiceAgreement", "TestItemAccess", "Delivery", "Acceptance", "StakeholderInput"}
CLASSDEFS = ["  classDef person fill:#e8f5e9,stroke:#2e7d32;",
             "  classDef machine fill:#fce4ec,stroke:#ad1457;",
             "  classDef party fill:#fff8e1,stroke:#f9a825,stroke-dasharray: 4 4;"]


@dataclass(frozen=True)
class View:
    name: str
    title: str
    focus: str
    leaves_out: str
    render: Callable[[Graph], str]

    def perspective(self) -> str:
        return f"In focus: {self.focus} Left out: {self.leaves_out}"


# --- readers of the graph -------------------------------------------------

def name(g: Graph, n) -> str:
    return str(g.value(n, SYS.declaredName))


def definitions(g: Graph, kind) -> dict:
    return {name(g, d): d for d in g.subjects(RDF.type, kind)
            if g.value(d, SYS.owner) is not None and name(g, g.value(d, SYS.owner)) == TOP_PACKAGE}


def kind_of(g: Graph, d) -> str:
    """person, organization, machine or party, by walking specializes."""
    seen = set()
    while d is not None and d not in seen:
        seen.add(d)
        n = name(g, d)
        if n in ("Person", "Organization", "Machine"):
            return n.lower()
        d = g.value(d, SYS.specializes)
    return "party"


def steps(g: Graph, proc_name: str = INNER_PROCESS) -> list[str]:
    proc = definitions(g, SYS.ActionDefinition)[proc_name]
    succ = {name(g, g.value(s, OGM["first"])): name(g, g.value(s, OGM["then"]))
            for s in g.subjects(RDF.type, SYS.SuccessionAsUsage) if g.value(s, SYS.owner) == proc}
    first = (set(succ) - set(succ.values())).pop()
    order = [first]
    while order[-1] in succ:
        order.append(succ[order[-1]])
    return order


def part_tree(g: Graph, holder_def, prefix: str = ""):
    """Yield (path, usage, definition) for every part usage under a definition, depth first."""
    for u in sorted(g.subjects(SYS.owner, holder_def), key=lambda x: name(g, x)):
        if (u, RDF.type, SYS.PartUsage) not in g:
            continue
        d = g.value(u, SYS.type)
        path = f"{prefix}{name(g, u)}"
        yield path, u, d
        yield from part_tree(g, d, path + ".")


def item_of_port_def(g: Graph, ptype) -> str:
    return next((name(g, g.value(u, SYS.type)) for u in g.subjects(SYS.owner, ptype) if (u, RDF.type, SYS.ItemUsage) in g), "")


def seam_item(g: Graph, s) -> str:
    return item_of_port_def(g, g.value(g.value(s, OGM.supplierPort), SYS.type))


def seam_slice(g: Graph, s) -> str:
    """A seam belongs to the contracting slice when the item it carries is pinned at the contract (or is a population's input)."""
    return "contracting" if seam_item(g, s) in CONTRACT_KINDS else "evaluation"


def seams(g: Graph, slice_: str | None = None) -> list:
    out = sorted(g.subjects(RDF.type, SYS.InterfaceUsage), key=lambda s: name(g, s))
    return [s for s in out if slice_ is None or seam_slice(g, s) == slice_]


def relations(g: Graph) -> list[tuple]:
    """Connection usages of the assembly that carry no item: (usage, definition name, [from part, to part])."""
    out = []
    for c in sorted(g.subjects(RDF.type, SYS.ConnectionUsage), key=lambda c: name(g, c)):
        out.append((c, name(g, g.value(c, SYS.type)), [g.value(c, OGM.relatesFrom), g.value(c, OGM.relatesTo)]))
    return out


def item_order(g: Graph) -> dict[str, int]:
    """Item kinds in the order the nested process produces them: the outer
    steps in succession, the inner steps in place of the typed step."""
    order: list[str] = []

    def walk(proc_name: str):
        proc = definitions(g, SYS.ActionDefinition)[proc_name]
        for step_name in steps(g, proc_name):
            step = next(u for u in g.subjects(SYS.owner, proc) if (u, RDF.type, SYS.ActionUsage) in g and name(g, u) == step_name)
            typ = g.value(step, SYS.type)
            if typ is not None and (typ, RDF.type, SYS.ActionDefinition) in g:
                walk(name(g, typ))
                continue
            for p in sorted(g.subjects(SYS.owner, step), key=lambda x: name(g, x)):
                if str(g.value(p, SYS.direction)) == "out" and g.value(p, SYS.type) is not None:
                    order.append(name(g, g.value(p, SYS.type)))
    walk(OUTER_PROCESS)
    return {n: i for i, n in enumerate(dict.fromkeys(order))}


# --- renderers ------------------------------------------------------------

def mermaid(block: str) -> str:
    return "```{mermaid}\n" + block.strip() + "\n```\n"


def _shape(nid: str, label: str, kind: str) -> str:
    return {"person": f'{nid}(["{label}"])', "machine": f'{nid}[["{label}"]]', "party": f'{nid}{{{{"{label}"}}}}'}.get(kind, f'{nid}["{label}"]')


def wiring(g: Graph, slice_: str | None = None, nest: bool = False) -> str:
    """The assemblage wired: parts as nodes (organizations as boxes around
    their parts when nest is set), one bundled edge per ordered pair of
    parts labelled by the item kinds that flow, relations dotted."""
    assembly = definitions(g, SYS.PartDefinition)[ASSEMBLY]
    tree = list(part_tree(g, assembly))
    by_def = {d: p for p, u, d in tree}
    by_usage = {u: p for p, u, d in tree}
    chosen = seams(g, slice_)
    rels = [r for r in relations(g) if slice_ in (None, "contracting")]
    used = set()
    for s in chosen:
        for port in (g.value(s, OGM.supplierPort), g.value(s, OGM.consumerPort)):
            used.add(by_def[g.value(port, SYS.owner)])
    for _, _, parts in rels:
        used.update(by_usage[p] for p in parts)
    ids = {p: p.replace(".", "_") for p, _, _ in tree}
    classes: dict[str, list[str]] = {"person": [], "machine": [], "party": []}
    lines = ["flowchart LR"]

    def node(indent: str, path, u, d):
        k = kind_of(g, d)
        lines.append(indent + _shape(ids[path], f"{name(g, u)} : {name(g, d)}", k))
        if k in classes:
            classes[k].append(ids[path])

    if nest:
        top = [(p, u, d) for p, u, d in tree if "." not in p]
        for path, u, d in top:
            children = [(p, cu, cd) for p, cu, cd in tree if p.startswith(path + ".")]
            if children:
                lines.append(f'  subgraph {ids[path]}["{name(g, u)} : {name(g, d)}"]')
                for cp, cu, cd in children:
                    grand = [(p2, u2, d2) for p2, u2, d2 in tree if p2.startswith(cp + ".")]
                    if grand:
                        lines.append(f'    subgraph {ids[cp]}["{name(g, cu)} : {name(g, cd)}"]')
                        for gp, gu, gd in grand:
                            node("      ", gp, gu, gd)
                        lines.append("    end")
                    elif cp.count(".") == 1:
                        node("    ", cp, cu, cd)
                lines.append("  end")
            else:
                node("  ", path, u, d)
    else:
        for path, u, d in tree:
            if path in used:
                node("  ", path, u, d)
    order = item_order(g)
    bundles: dict[tuple[str, str], list[str]] = {}
    for s in chosen:
        src = by_def[g.value(g.value(s, OGM.supplierPort), SYS.owner)]
        dst = by_def[g.value(g.value(s, OGM.consumerPort), SYS.owner)]
        bundles.setdefault((src, dst), []).append(seam_item(g, s))
    for (src, dst), items in sorted(bundles.items()):
        label = ", ".join(sorted(set(items), key=lambda n: (order.get(n, len(order)), n)))
        lines.append(f'  {ids[src]} -- "{label}" --> {ids[dst]}')
    for c, dname, parts in rels:
        a, b = (by_usage[p] for p in parts)
        lines.append(f'  {ids[a]} -. "{name(g, c)}" .-> {ids[b]}')
    lines += CLASSDEFS
    for k in ("person", "machine", "party"):
        if classes[k]:
            lines.append(f"  class {','.join(classes[k])} {k};")
    return "\n".join(lines)


def layers(g: Graph) -> str:
    defs = definitions(g, SYS.PartDefinition)
    people = sorted(n for n, d in defs.items() if kind_of(g, d) == "person")
    machines = sorted(n for n, d in defs.items() if kind_of(g, d) == "machine")
    orgs = sorted(n for n, d in defs.items() if kind_of(g, d) == "organization" and n != "Organization")
    chain = " --> ".join(f"s{i}[{s}]" for i, s in enumerate(steps(g, INNER_PROCESS)))
    cchain = " --> ".join(f"c{i}[{s}]" for i, s in enumerate(steps(g, OUTER_PROCESS)))
    return f"""flowchart TB
  subgraph PARTIES["Contracting lifecycle: the parties ({', '.join(orgs)}; affected populations) pin the first layer of assumptions"]
    direction LR
    {cchain}
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
  EXEC ==> INTERP"""


# --- the registry ---------------------------------------------------------

VIEWS: dict[str, View] = {v.name: v for v in [
    View("layers", "The layers",
         "the two cycles as chains of steps, the DSO as the expert-supplied parameter, and how execution and interpretation rest on the record.",
         "every part, port, seam and item kind; the steps' inputs and outputs; who performs which step.",
         layers),
    View("assemblage", "The assemblage",
         "every party and every part of the testing organization, nested in the organization that holds it, with one bundled edge per pair of parts labelled by the item kinds that flow between them, and the sponsor's obligation to the affected populations dotted.",
         "the seam names and the ports (the wiring table has them, one row per port), and the order in which the items flow.",
         lambda g: wiring(g, None, nest=True)),
    View("contracting", "The contracting slice",
         "the parties to the contract and the two parts of the testing organization they touch, the items pinned at the contract braided into one bundle per pair of parts, and the sponsor's obligation to the affected populations, a relation that carries no item.",
         "the evaluation team, the machines and the test item; the evaluation items; the seam names and the ports; the recorder's fan-out of the record.",
         lambda g: wiring(g, "contracting")),
    View("evaluation", "The evaluation slice",
         "the team, the machines, the test item and the recorder, with the evaluation items braided into one bundle per pair of parts.",
         "the sponsor, the account executive's contracting wires and the accountable organization's access grant; the seam names and the ports.",
         lambda g: wiring(g, "evaluation")),
]}


def view_record(g: Graph, name_: str) -> dict:
    v = VIEWS[name_]
    return {"name": v.name, "title": v.title, "focus": v.focus, "leaves_out": v.leaves_out, "mermaid": v.render(g)}


def views_table() -> list[dict]:
    return [{"name": v.name, "title": v.title, "focus": v.focus, "leaves_out": v.leaves_out} for v in VIEWS.values()]
