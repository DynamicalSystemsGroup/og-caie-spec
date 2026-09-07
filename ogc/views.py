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

import re
from dataclasses import dataclass
from typing import Callable

from rdflib import RDF, Graph, Namespace

SYS = Namespace("https://www.omg.org/spec/SysML#")
OGM = Namespace("https://w3id.org/og-caie/model#")
SYSX_SOURCE_TEXT = Namespace("urn:opensysml:sysml:")["sourceText"]
ASSEMBLY = "OgCaieEvaluation"
TOP_PACKAGE = "OGCAIE"
OUTER_PROCESS = "ContractingProcess"
INNER_PROCESS = "EvaluationProcess"
CONTRACT_KINDS = {"Mission", "StatementOfWork", "Need", "Proposal", "ServiceAgreement", "TestItemAccess", "Delivery", "Acceptance", "StakeholderInput"}
# Strong, distinct fills with an explicit text colour, so the figures read on
# a light or a dark page (Z, 2026-09-06: pastel fills were hard to read).
# Headwords for the figures where the identifier and the headword differ (R-49); identifiers stay.
DISPLAY = {"AccountExecutive": "authorized representative", "AccountableOrganization": "test item provider", "TestDriver": "test driver",
           "ReportAssembler": "report assembler", "ConformanceChecker": "conformance checker", "SponsorOrganization": "sponsor", "TestingOrganization": "testing organization",
           "AffectedPopulation": "affected population", "DomainExpert": "domain expert", "EvaluationOperator": "evaluation operator", "EvaluationTeam": "evaluation team",
           "Recorder": "recorder", "TestItem": "test item", "Representative": "population representative"}


def display(defname: str) -> str:
    return DISPLAY.get(defname, re.sub(r'(?<!^)(?=[A-Z])', ' ', defname).lower())


CLASSDEFS = ["  classDef person fill:#1b5e20,stroke:#a5d6a7,stroke-width:2px,color:#ffffff;",
             "  classDef machine fill:#880e4f,stroke:#f48fb1,stroke-width:2px,color:#ffffff;",
             "  classDef party fill:#f9a825,stroke:#e65100,stroke-width:2px,stroke-dasharray: 6 3,color:#000000;",
             "  classDef organization fill:#37474f,stroke:#cfd8dc,stroke-width:2px,color:#ffffff;",
             "  linkStyle default stroke:#90a4ae,stroke-width:1.5px;"]


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
    classes: dict[str, list[str]] = {"person": [], "machine": [], "party": [], "organization": []}
    lines = ["flowchart LR"]

    def node(indent: str, path, u, d):
        k = kind_of(g, d)
        lines.append(indent + _shape(ids[path], f"{name(g, u)} : {display(name(g, d))}", k))
        if k in classes:
            classes[k].append(ids[path])

    if nest:
        top = [(p, u, d) for p, u, d in tree if "." not in p]
        for path, u, d in top:
            children = [(p, cu, cd) for p, cu, cd in tree if p.startswith(path + ".")]
            if children:
                lines.append(f'  subgraph {ids[path]}["{name(g, u)} : {display(name(g, d))}"]')
                for cp, cu, cd in children:
                    grand = [(p2, u2, d2) for p2, u2, d2 in tree if p2.startswith(cp + ".")]
                    if grand:
                        lines.append(f'    subgraph {ids[cp]}["{name(g, cu)} : {display(name(g, cd))}"]')
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
    for k in ("person", "machine", "party", "organization"):
        if classes[k]:
            lines.append(f"  class {','.join(classes[k])} {k};")
    return "\n".join(lines)


def nesting(g: Graph) -> str:
    """The two cycles as chains, the typed step as a black box in the outer
    chain and opened as the inner chain below it; the only edges drawn are
    the flows that cross the boundary, from the outer step that produces an
    item to the inner step that consumes it (through the process's own
    parameter and the bind that hands it on), and back out."""
    outer = definitions(g, SYS.ActionDefinition)[OUTER_PROCESS]
    inner = definitions(g, SYS.ActionDefinition)[INNER_PROCESS]
    outer_steps, inner_steps = steps(g, OUTER_PROCESS), steps(g, INNER_PROCESS)
    typed = {name(g, u) for u in g.subjects(SYS.owner, outer) if (u, RDF.type, SYS.ActionUsage) in g and g.value(u, SYS.type) == inner}
    # the process's own parameters, and the inner step each is bound to
    bound: dict[str, str] = {}
    for b in g.subjects(RDF.type, SYS.BindingConnectorAsUsage):
        if g.value(b, SYS.owner) != inner:
            continue
        m = re.match(r"bind\s+(\S+)\s*=\s*(\S+);", str(g.value(b, SYSX_SOURCE_TEXT) or ""))
        if not m:
            continue
        a, c = m.group(1), m.group(2)
        step_side, param_side = (a, c) if "." in a else (c, a)
        bound[param_side] = step_side.split(".")[0]
    lines = ["flowchart TB", f'  subgraph OUTER["Contracting lifecycle"]', "    direction LR"]
    lines.append("    " + " --> ".join(f'o_{st}[["{st} : {INNER_PROCESS}"]]' if st in typed else f"o_{st}[{st}]" for st in outer_steps))
    lines += ["  end", f'  subgraph INNER["{sorted(typed)[0]}, opened: the evaluation"]', "    direction LR"]
    lines.append("    " + " --> ".join(f"i_{st}[{st}]" for st in inner_steps))
    lines.append("  end")
    crossing = []
    for f in g.subjects(RDF.type, SYS.FlowUsage):
        if g.value(f, SYS.owner) != outer:
            continue
        src, tgt = g.value(f, OGM.flowSource), g.value(f, OGM.flowTarget)
        kind = name(g, g.value(src, SYS.type)) if g.value(src, SYS.type) is not None else name(g, g.value(tgt, SYS.type))
        s_owner, t_owner = g.value(src, SYS.owner), g.value(tgt, SYS.owner)
        if t_owner == inner:  # into the black box: outer step -> inner step bound to that parameter
            crossing.append((f"o_{name(g, s_owner)}", f"i_{bound.get(name(g, tgt), '?')}", kind))
        elif s_owner == inner:  # out of it
            crossing.append((f"i_{bound.get(name(g, src), '?')}", f"o_{name(g, t_owner)}", kind))
    bundles: dict[tuple[str, str], list[str]] = {}
    for a, b, kind in crossing:
        bundles.setdefault((a, b), []).append(kind)
    order = item_order(g)
    supplier: dict[str, str] = {}
    for pd in g.subjects(RDF.type, SYS.PortDefinition):
        item = item_of_port_def(g, pd)
        parts = sorted({name(g, g.value(p, SYS.owner)) for p in g.subjects(SYS.type, pd)
                        if (p, RDF.type, SYS.PortUsage) in g and g.value(p, SYS.isConjugated) is None and g.value(p, SYS.isEnd) is None
                        and (g.value(p, SYS.owner), RDF.type, SYS.PartDefinition) in g})
        if parts:
            supplier[item] = parts[0]
    for (a, b), kinds in sorted(bundles.items()):
        named = [f"{k} (from the {display(supplier[k])})" if k in supplier else k
                 for k in sorted(set(kinds), key=lambda n: (order.get(n, len(order)), n))]
        lines.append(f'  {a} -- "{", ".join(named)}" --> {b}')
    lines.append("  classDef step fill:#37474f,stroke:#cfd8dc,stroke-width:1.5px,color:#ffffff;")
    lines.append("  classDef black fill:#000000,stroke:#ffb300,stroke-width:3px,color:#ffffff;")
    lines.append(f"  class {','.join(f'o_{st}' for st in outer_steps if st not in typed)},{','.join(f'i_{st}' for st in inner_steps)} step;")
    lines.append("  linkStyle default stroke:#90a4ae,stroke-width:1.5px;")
    for st in typed:
        lines.append(f"  class o_{st} black;")
    return "\n".join(lines)


# --- the registry ---------------------------------------------------------

VIEWS: dict[str, View] = {v.name: v for v in [
    View("nesting", "The nested lifecycle",
         "the two cycles as chains of steps, the fulfil step as a black box in the outer chain and opened as the inner chain, and the only wires that cross the boundary: what the contract hands in and what the evaluation hands back, bundled by item kind.",
         "the flows inside each chain, the parties, the parts and ports, the DSO as a parameter, and who performs which step (the two chapters before this one have them).",
         nesting),
    View("assemblage", "The assemblage",
         "every party and every part of the testing organization, nested in the organization that holds it, with one bundled edge per pair of parts labelled by the item kinds that flow between them, and the sponsor's obligation to the affected populations dotted.",
         "the seam names and the ports (the wiring table has them, one row per port), and the order in which the items flow.",
         lambda g: wiring(g, None, nest=True)),
    View("contracting", "The contracting slice",
         "the parties to the contract and the two parts of the testing organization they touch, the items pinned at the contract braided into one bundle per pair of parts, and the sponsor's obligation to the affected populations, a relation that carries no item.",
         "the evaluation team, the machines and the test item; the evaluation items; the seam names and the ports; the recorder's wires to the machines.",
         lambda g: wiring(g, "contracting")),
    View("evaluation", "The evaluation slice",
         "the team, the machines, the test item and the recorder, with the evaluation items braided into one bundle per pair of parts.",
         "the sponsor and the authorized representative's contracting wires; the seam names and the ports.",
         lambda g: wiring(g, "evaluation")),
]}


def view_record(g: Graph, name_: str) -> dict:
    v = VIEWS[name_]
    return {"name": v.name, "title": v.title, "focus": v.focus, "leaves_out": v.leaves_out, "mermaid": v.render(g)}


def views_table() -> list[dict]:
    return [{"name": v.name, "title": v.title, "focus": v.focus, "leaves_out": v.leaves_out} for v in VIEWS.values()]
