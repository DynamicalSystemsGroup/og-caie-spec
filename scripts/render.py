#!/usr/bin/env python3
"""Render committed Markdown fragments under generated/ from the RDF graphs.
Deterministic: same graphs, same bytes. The gate diffs generated/ after
running this; the site includes the fragments."""
import re
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


SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
XW_FILES = ("vocabulary/crosswalk.ttl", "vocabulary/og-caie.ttl", "vocabulary/epo.ttl", "shapes/epo.shapes.ttl", "shapes/model.shapes.ttl", "sources/sources.ttl")
PROSE_FOR_TERMS = ["index.md", "docs/*.md", "generated/popper.md", "generated/popper-back.md"]
TERM_ROLE = re.compile(r"\{term\}`([^`]+)`")


def term_role(g, t) -> str:
    return "{term}`" + str(g.value(t, SKOS.prefLabel)) + "`"


def crosswalk_rows(g):
    return sorted(g.subjects(RDF.type, OGC.Crosswalk), key=lambda r: int(g.value(r, OGC.order)))


def realizer_name(x) -> str:
    return str(x).rsplit("#", 1)[-1] if "#" in str(x) else str(x).rsplit("/", 1)[-1]


def render_popper() -> str:
    g = Graph()
    for f in XW_FILES:
        g.parse(ROOT / f)
    lines = ["| Popper's element, in the deck's words | The standard terms it lands on | Where it lives in the record | What makes it checkable |",
             "|---|---|---|---|"]
    for r in crosswalk_rows(g):
        terms = ", ".join(term_role(g, t) for t in sorted(g.objects(r, OGC.mapsTo), key=lambda t: str(g.value(t, SKOS.prefLabel)).lower()))
        lines.append(f"| **{cell(g.value(r, RDFS.label))}**: \"{cell(g.value(r, OGC.quote))}\" | {terms} | {cell(g.value(r, OGC.where))} | {cell(g.value(r, OGC.checkable))} |")
    src = g.value(crosswalk_rows(g)[0], OGC.cites)
    lines.append("")
    lines.append(f"The definitions in the first column are the authors' own, from slide 5 of the SciPy 2026 birds-of-a-feather deck, after Popper (1959).")
    return "\n".join(lines) + "\n"


def render_popper_back() -> str:
    g = Graph()
    for f in XW_FILES:
        g.parse(ROOT / f)
    lines = ["| What the record holds and the shapes check | In the standard terms | Popper's element |", "|---|---|---|"]
    for r in crosswalk_rows(g):
        realizers = ", ".join(f"`{realizer_name(x)}`" for x in sorted(g.objects(r, OGC.realizedBy), key=realizer_name))
        terms = ", ".join(term_role(g, t) for t in sorted(g.objects(r, OGC.mapsTo), key=lambda t: str(g.value(t, SKOS.prefLabel)).lower()))
        lines.append(f"| {realizers}: {cell(g.value(r, OGC.checkable))} | {terms} | **{cell(g.value(r, RDFS.label))}** |")
    return "\n".join(lines) + "\n"


def referenced_terms(g):
    """The concepts the prose references with {term} roles, resolved by prefLabel or altLabel (case-insensitive)."""
    labels = {}
    for t in g.subjects(RDF.type, SKOS.Concept):
        for pred in (SKOS.prefLabel, SKOS.altLabel):
            for l in g.objects(t, pred):
                labels.setdefault(str(l).lower(), set()).add(t)
    found, unresolved = {}, []
    for pattern in PROSE_FOR_TERMS:
        for f in sorted(ROOT.glob(pattern)):
            for m in TERM_ROLE.finditer(f.read_text()):
                key = m.group(1)
                if "<" in key:
                    key = key[key.rindex("<") + 1:].rstrip(">").strip()
                hits = labels.get(key.lower(), set())
                if len(hits) != 1:
                    unresolved.append((f.name, key, len(hits)))
                else:
                    found[next(iter(hits))] = key
    return found, unresolved


def render_key_terms() -> str:
    g = Graph()
    for f in ("vocabulary/og-caie.ttl", "sources/sources.ttl"):
        g.parse(ROOT / f)
    found, unresolved = referenced_terms(g)
    if unresolved:
        raise SystemExit(f"unresolved {{term}} roles: {unresolved}")
    lines = ["```{glossary}"]
    for t in sorted(found, key=lambda t: str(g.value(t, SKOS.prefLabel)).lower()):
        c = g.value(t, OGC.canonical)
        src = g.value(c, OGC.cites)
        label = str(g.value(src, RDFS.label)).split(" (")[0].split(", ")[0]
        quote = g.value(c, OGC.quote)
        cite = f"{label}, {cell(g.value(c, OGC.locator))}" + (f': "{cell(quote)}" ({cell(g.value(c, OGC.quoteStatus))})' if quote else "")
        alts = sorted(str(a) for a in g.objects(t, SKOS.altLabel))
        rul = sorted(str(r).rsplit("#", 1)[-1] for r in g.objects(t, PROV.wasDerivedFrom))
        body = cell(g.value(t, SKOS.definition)) + f" Source: {cite}."
        if alts:
            body += f" Also: {', '.join(alts)}."
        if rul:
            body += f" Ruling {', '.join(rul)}."
        lines.append(str(g.value(t, SKOS.prefLabel)))
        lines.append(f": {body}")
        lines.append("")
    lines.append("```")
    return "\n".join(lines) + "\n"


CONTRACT_STEPS = ("need", "propose", "agree", "access", "deliver", "acceptDelivery")


def render_record_chapter(chapter: str) -> str:
    """The walkthrough rows of one chapter: the record's items at that chapter's steps, with who and when."""
    from rdflib import Namespace as NS
    EPO = NS("https://w3id.org/og-caie/epo#")
    PROV = NS("http://www.w3.org/ns/prov#")
    EARL = NS("http://www.w3.org/ns/earl#")
    g = Graph()
    for f in ("vocabulary/epo.ttl", "track/measles-run.ttl"):
        g.parse(ROOT / f)
    want = set(CONTRACT_STEPS) if chapter == "contracting" else None
    rows = []
    for n, st in g.subject_objects(EPO.step):
        step = str(st).rsplit("#", 1)[-1]
        if want is not None and step not in want:
            continue
        if want is None and step in CONTRACT_STEPS:
            continue
        cls = next((c for c in g.objects(n, RDF.type) if str(c).startswith(str(EPO))), None)
        who = [g.value(a, RDFS.label) or str(a).rsplit("#", 1)[-1] for pr in (EARL.assertedBy, EPO.approvedBy, EPO.signedBy, PROV.wasAttributedTo, PROV.wasAssociatedWith) for a in g.objects(n, pr)]
        when = g.value(n, PROV.generatedAtTime) or g.value(n, PROV.startedAtTime) or g.value(n, PROV.endedAtTime) or ""
        label = g.value(n, RDFS.label) or g.value(n, EPO.text) or ""
        order = str(g.value(st, RDFS.label)).split(" ", 1)[0]
        rows.append((order, str(when), f"| {cell(str(g.value(st, RDFS.label)).split(':')[0])} | `{str(n).rsplit('#', 1)[-1]}` ({cell(str(cls).rsplit('#', 1)[-1])}) | {cell(label)} | {cell('; '.join(dict.fromkeys(str(w) for w in who)))} | {cell(str(when)[:10])} |"))
    lines = ["| Step | Item | What it says | Who | When |", "|---|---|---|---|---|"] + [r[2] for r in sorted(rows, key=lambda r: (r[1], r[0]))]
    return "\n".join(lines) + "\n"


def render_layers_walkthrough() -> str:
    """The record split by layer (S0-Layers): for each layer, the item kinds pinned there, how many items, their date span and who made them."""
    from rdflib import Namespace as NS
    EPO = NS("https://w3id.org/og-caie/epo#")
    PROV = NS("http://www.w3.org/ns/prov#")
    EARL = NS("http://www.w3.org/ns/earl#")
    g = Graph()
    for f in ("vocabulary/epo.ttl", "track/measles-run.ttl"):
        g.parse(ROOT / f)
    lines = ["| Layer | Item kinds | Items | First | Last | Who |", "|---|---|---|---|---|---|"]
    for layer in sorted(g.subjects(RDF.type, EPO.Layer), key=lambda l: 0 if str(l).endswith("contract") else 1):
        classes = sorted(g.subjects(OGC.pinnedAt, layer), key=str)
        items, whos, dates = [], [], []
        for c in classes:
            for n in g.subjects(RDF.type, c):
                items.append(n)
                dates += [str(d)[:10] for d in (g.value(n, PROV.generatedAtTime), g.value(n, PROV.startedAtTime)) if d]
                whos += [str(g.value(a, RDFS.label) or a).split(" (")[0] for pr in (EARL.assertedBy, EPO.approvedBy, EPO.signedBy, PROV.wasAttributedTo, PROV.wasAssociatedWith) for a in g.objects(n, pr)]
        kinds = ", ".join(str(c).rsplit("#", 1)[-1] for c in classes if any(True for _ in g.subjects(RDF.type, c)))
        lines.append(f"| {str(layer).rsplit('#', 1)[-1]} | {kinds} | {len(items)} | {min(dates) if dates else ''} | {max(dates) if dates else ''} | {', '.join(sorted(set(whos)))} |")
    return "\n".join(lines) + "\n"


def render_more(page: str, fragments: list[str], commands: list[str], files: list[str]) -> str:
    """Block 5 of the page pattern: this page is a view; the model is the repository."""
    lines = ["This page is a view. The model is the repository, and it holds more than the page shows.", "",
             "- Rendered here: " + ", ".join(f"`generated/{f}`" for f in fragments) + ", regenerated by the gate from the graphs and diffed byte for byte.",
             "- Ask the graph: " + ", ".join(f"`{c}`" for c in commands) + ".",
             "- Read the sources: " + ", ".join(f"`{f}`" for f in files) + "."]
    return "\n".join(lines) + "\n"


def render_signoff_sheet() -> str:
    """Rulings sheet 05: one row per kind of part and per wire of the canonical model graph, for Z's block-by-block and wire-by-wire validation (C-30)."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from prune_model import OGM, SYS
    g = Graph(); g.parse(ROOT / "model" / "og-caie.model.ttl")
    def nm(n): return str(g.value(n, SYS.declaredName))
    defs = sorted((d for d in g.subjects(RDF.type, SYS.PartDefinition) if any(True for _ in g.subjects(SYS.owner, d))), key=nm)
    lines = ["# Rulings sheet 05: the blocks and the wires (concern C-30)", "",
             "Generated from `model/og-caie.model.ttl` by `scripts/render.py`; do not edit the rows by hand, tick them. One row per kind of part (its inputs and outputs) and one per wire (output port on a part to input port on a part). Z: tick a row when the block or the wire is validated; add a concern for anything wrong.", "",
             "## Blocks", "", "| # | Part kind | Inputs | Outputs | Validated |", "|---|---|---|---|---|"]
    i = 0
    for d in defs:
        ports = [p for p in g.subjects(SYS.owner, d) if (p, RDF.type, SYS.PortUsage) in g]
        if not ports:
            continue
        i += 1
        ins = ", ".join(sorted(nm(p) for p in ports if g.value(p, SYS.isConjugated)))
        outs = ", ".join(sorted(nm(p) for p in ports if not g.value(p, SYS.isConjugated)))
        lines.append(f"| B{i} | {nm(d)} | {ins or '(none)'} | {outs or '(none)'} | [ ] |")
    lines += ["", "## Wires", "", "| # | Wire | From | To | Carries | Validated |", "|---|---|---|---|---|---|"]
    j = 0
    for s in sorted(g.subjects(RDF.type, SYS.InterfaceUsage), key=nm):
        j += 1
        sp, cp = g.value(s, OGM.supplierPort), g.value(s, OGM.consumerPort)
        lines.append(f"| W{j} | {nm(s)} | {nm(g.value(sp, SYS.owner))}.{nm(sp)} | {nm(g.value(cp, SYS.owner))}.{nm(cp)} | {nm(g.value(sp, SYS.type))} | [ ] |")
    lines += ["", "## Relations", "", "Connections that carry no item: a relation between two parties, drawn dotted in the views (R-38).", "",
              "| # | Relation | Kind | Between | Validated |", "|---|---|---|---|---|"]
    k = 0
    for c in sorted(g.subjects(RDF.type, SYS.ConnectionUsage), key=nm):
        k += 1
        parts = " towards ".join(f"{nm(p)} : {nm(g.value(p, SYS.type))}" for p in (g.value(c, OGM.relatesFrom), g.value(c, OGM.relatesTo)))
        lines.append(f"| X{k} | {nm(c)} | {nm(g.value(c, SYS.type))} | {parts} | [ ] |")
    return "\n".join(lines) + "\n"


def render_steps() -> str:
    EPO = Namespace("https://w3id.org/og-caie/epo#")
    g = Graph()
    for f in ("vocabulary/epo.ttl", "sources/sources.ttl"):
        g.parse(ROOT / f)

    def citation(c):
        src = g.value(c, OGC.cites)
        label = str(g.value(src, RDFS.label)).split(" (")[0].split(", ")[0]
        q = g.value(c, OGC.quote)
        return f"{label}, {cell(g.value(c, OGC.locator))}" + (f': "{cell(q)}" ({cell(g.value(c, OGC.quoteStatus))})' if q else "")

    def table(cls, title):
        steps = sorted(g.subjects(RDF.type, cls), key=lambda x: str(g.value(x, RDFS.label)))
        lines = [title, "", "| Step | Matches | Also |", "|---|---|---|"]
        for st in steps:
            canon = citation(g.value(st, OGC.canonical))
            also = "; ".join(citation(c) for c in sorted(g.objects(st, OGC.seeAlso), key=lambda c: (str(g.value(c, OGC.cites)), str(g.value(c, OGC.locator)))))
            lines.append(f"| **{cell(g.value(st, RDFS.label))}** | {canon} | {also} |")
        return "\n".join(lines) + "\n"
    frame = citation(g.value(EPO.ContractingStep, OGC.canonical))
    (OUT / "steps-contracting.md").write_text(table(EPO.ContractingStep, f"The outer cycle, contracting through delivery: {frame}."))
    (OUT / "steps-evaluation.md").write_text(table(EPO.EpoStep, "The inner cycle, performed between access and delivery."))
    return (table(EPO.ContractingStep, f"### The contracting lifecycle, C1 to C6\n\nThe outer cycle, contracting through delivery, whose actors are the parties and whose steps are the agreement processes of the standards ({frame}).")
            + "\n" + table(EPO.EpoStep, "### The evaluation, steps 1 to 6\n\nThe inner cycle, performed between access and delivery."))


def main_all() -> int:
    OUT.mkdir(exist_ok=True)
    (OUT / "rulings.md").write_text(render_rulings())
    (OUT / "glossary.md").write_text(render_glossary())
    (OUT / "sources.md").write_text(render_sources())
    (OUT / "record.md").write_text(render_record())
    (OUT / "popper.md").write_text(render_popper())
    (OUT / "popper-back.md").write_text(render_popper_back())
    (OUT / "key-terms.md").write_text(render_key_terms())
    (OUT / "steps.md").write_text(render_steps())
    (OUT / "record-contracting.md").write_text(render_record_chapter("contracting"))
    (OUT / "record-evaluation.md").write_text(render_record_chapter("evaluation"))
    (OUT / "more-contracting.md").write_text(render_more("contracting",
        ["steps-contracting.md", "wiring-contracting.md", "wiring-table-contracting.md", "sci-contracting.md", "record-contracting.md"],
        ["ogc view contracting", "ogc views", "ogc steps", "ogc sci SCI-10", "ogc term mission", "ogc term customer", "ogc term provider", "ogc term contract", "ogc verify iso-iec-17000-2020", "ogc sparql"],
        ["model/og-caie.sysml", "model/og-caie.model.ttl", "vocabulary/epo.ttl", "shapes/epo.shapes.ttl (S0)", "shapes/model.shapes.ttl (M1, M5)", "ogc/views.py", "track/measles-run.ttl"]))
    (OUT / "layers-walkthrough.md").write_text(render_layers_walkthrough())
    (OUT / "more-evaluation.md").write_text(render_more("evaluation",
        ["steps-evaluation.md", "wiring-evaluation.md", "wiring-table-evaluation.md", "sci-evaluation.md", "record-evaluation.md"],
        ["ogc view evaluation", "ogc steps", "ogc sci SCI-06", "ogc term evidence", "ogc term determination", "ogc term attestation", "ogc term trajectory", "ogc rulings --term evidence", "ogc sparql"],
        ["model/og-caie.sysml", "model/og-caie.model.ttl", "vocabulary/epo.ttl", "shapes/epo.shapes.ttl (S1 to S8)", "shapes/model.shapes.ttl (M2 to M5)", "track/measles-run.ttl", "counterexamples/", "queries/coverage.rq", "queries/traceback.rq"]))
    (OUT / "more-model.md").write_text(render_more("model",
        ["layers.md", "layers-walkthrough.md", "receipts.md"],
        ["ogc view layers", "ogc view assemblage", "ogc steps", "ogc sci SCI-11", "ogc sparql --model"],
        ["model/og-caie.sysml", "model/og-caie.model.ttl", "model/model_manifest.json", "model/sysml_term_map.csv", "scripts/prune_model.py", "shapes/model.shapes.ttl (M4)", "shapes/epo.shapes.ttl (S0-Layers)"]))
    (ROOT / "rulings" / "sheets" / "05-blocks-and-wires.md").write_text(render_signoff_sheet())
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
    order = [EPO.ServiceAgreement, EPO.TestItemAccess, EPO.StakeholderInput, EPO.DsoRelease, EPO.RequirementSet, EPO.Requirement, EPO.AcceptanceCriterion,
             EPO.AppropriatenessAssessment, EPO.TestPlan, EPO.PlanApproval, EPO.Strategy, EPO.Probe,
             EPO.ConsistencyCheck, EPO.TestSuite, EPO.Session, EPO.Turn, EPO.Trajectory, EPO.Response, EPO.Evidence, EPO.Determination, EPO.Attestation,
             EPO.CoverageComputation, EPO.Report, EPO.Recommendation, EPO.Delivery]
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
