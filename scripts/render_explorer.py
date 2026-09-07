#!/usr/bin/env python3
"""Render the knowledge graph explorer (ruling R-39): the human-facing
interface to the same graphs the site is rendered from. An alternative user
interface, not new content.

Reads the vocabulary, the sources, the rulings, the essentials, the shapes,
the canonical model graph (through ogc.graph.load, model=True) and the
measles record, and writes:

- explorer/graph.json: nodes, links, views and the per-node detail (every
  triple the graph holds about the node, outgoing and incoming);
- explorer/index.html: one self-contained page (vendored d3 v7 inlined,
  the same JSON inlined) with a force layout, zoom, pan, drag, a search
  box, a legend, one button per view stating the perspective it encodes in
  two halves (what it brings into focus, what it leaves out), and a detail
  panel that names the `ogc` command that prints the node and links to the
  site page where it is rendered;
- explorer/data/*.ttl: copies of the Turtle files, for the optional SPARQL
  box (oxigraph's WebAssembly build under explorer/vendor/oxigraph/), which
  the d3 explorer never depends on.

Deterministic: same graphs, same bytes. Everything is sorted, blank-node
citations get ids computed from what they cite, and no timestamp is
written. The gate runs this and diffs explorer/.

Links are the graph's own predicates between two nodes, labelled by the
predicate's local name. Four derived links are added, each labelled by
name so a reader can tell them apart: `carries` (a seam to the item kind
its supplier port def carries, the reading ogc/views.py uses), `in` and
`out` (a model step to the item kind of a parameter), `then` (the
successions between steps) and `corresponds` (a model step or item def to
the EPO step or class of the same name, the binding the record relies on
through epo:step).
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

import yaml
from rdflib import RDF, RDFS, BNode, Graph, Literal, Namespace, URIRef

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ogc import views as V  # noqa: E402
from ogc.graph import (EPO, MODEL_FILE, OGC, PREFIXES, RUL, SH, SKOS, SOURCE_FILES, SRC, TERM, TR, XW,  # noqa: E402
                       load)

PROV = Namespace("http://www.w3.org/ns/prov#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
SYS = V.SYS
OGM = V.OGM
RUN = Namespace("https://w3id.org/og-caie/run/measles#")
RECORD_FILE = "track/measles-run.ttl"
OUT = ROOT / "explorer"
TITLE = "OG-CAIE: the knowledge graph explorer"
QNAMES = dict(PREFIXES)
QNAMES["run"] = RUN
QNAMES["owl"] = OWL
QNAMES["prov"] = PROV

# One family per node class: colour, glyph, radius, legend order and text.
FAMILIES = [
    ("term", "#1e88e5", "circle", 7, "glossary term"),
    ("citation", "#64b5f6", "circle", 3.5, "citation (canonical or neighbour)"),
    ("source", "#ab47bc", "circle", 8, "source"),
    ("concern", "#fb8c00", "circle", 6, "concern"),
    ("ruling", "#43a047", "circle", 6, "ruling"),
    ("sci", "#fdd835", "circle", 9, "essential (SCI)"),
    ("shape", "#00acc1", "diamond", 7, "shape (M over the model, S over the record)"),
    ("crosswalk", "#d81b60", "circle", 8, "crosswalk row"),
    ("step", "#7e57c2", "triangle", 8, "EPO step (the two cycles)"),
    ("kind", "#5c6bc0", "square", 6, "item kind (EPO class)"),
    ("layer", "#9575cd", "square", 8, "layer (where an item is pinned)"),
    ("role", "#b39ddb", "circle", 5, "role"),
    ("part", "#26a69a", "circle", 9, "part definition"),
    ("usage", "#80cbc4", "circle", 5, "part usage (the assembly)"),
    ("port", "#4db6ac", "circle", 3.5, "port"),
    ("seam", "#ef5350", "circle", 5, "seam (a wire, one item kind)"),
    ("relation", "#ef9a9a", "circle", 7, "relation that carries no item"),
    ("process", "#8d6e63", "triangle", 10, "action definition (a cycle)"),
    ("action", "#a1887f", "triangle", 7, "model step"),
    ("item", "#bcaaa4", "square", 5, "item definition (model)"),
    ("record", "#ffb74d", "circle", 6, "record item (measles run)"),
    ("agent", "#ffe082", "circle", 7, "agent (measles run)"),
]
LABEL_MAX = 48


# --- helpers ---------------------------------------------------------------

def local(x) -> str:
    s = str(x)
    return s.rsplit("#", 1)[-1] if "#" in s else s.rsplit("/", 1)[-1]


def qname(x) -> str:
    s = str(x)
    for k, ns in sorted(QNAMES.items(), key=lambda kv: -len(str(kv[1]))):
        if s.startswith(str(ns)):
            return f"{k}:{s[len(str(ns)):]}"
    return s


def short(s: str, n: int = LABEL_MAX) -> str:
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def one(g: Graph, s, p, default: str = "") -> str:
    v = g.value(s, p)
    return re.sub(r"\s+", " ", str(v)).strip() if v is not None else default


def slug(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def shell(cmd: str) -> str:
    return f'"{cmd}"' if re.search(r"[\s()]", cmd) else cmd


def site_pages() -> set[str]:
    cfg = yaml.safe_load((ROOT / "myst.yml").read_text())
    out = set()
    for e in cfg["project"]["toc"]:
        f = e.get("file", "")
        out.add("index" if f == "index.md" else Path(f).stem)
    return out


def rendered_terms() -> set[str]:
    """The terms the glossary page renders (generated/key-terms.md), so a term link has an anchor to land on."""
    f = ROOT / "generated" / "key-terms.md"
    if not f.exists():
        return set()
    return set(re.findall(r"^([^:\n`][^\n]*)\n: ", f.read_text(), re.M))


# --- the graph -------------------------------------------------------------

def graph() -> Graph:
    g = load(ROOT, model=True, cache=False)
    g.parse(ROOT / RECORD_FILE)
    return g


class Builder:
    def __init__(self, g: Graph):
        self.g = g
        self.nodes: dict[str, dict] = {}
        self.ids: dict[object, str] = {}  # rdflib term -> node id
        self.derived: list[tuple[str, str, str]] = []
        self.pages = site_pages()
        self.terms_on_page = rendered_terms()

    def page(self, name: str, anchor: str = "") -> str:
        if name not in self.pages:
            return ""
        return ("../" if name == "index" else f"../{name}") + (f"#{anchor}" if anchor else "")

    def add(self, term, cls: str, label: str, desc: str, ogc: str, page: str = "", nid: str | None = None) -> str:
        nid = nid or str(term)
        self.ids[term] = nid
        self.nodes[nid] = dict(id=nid, label=short(label), cls=cls, desc=re.sub(r"[ \t]+", " ", desc).strip(), ogc=ogc, page=page)
        return nid

    # -- vocabulary: terms, sources, citations
    def vocabulary(self):
        g = self.g
        for t in sorted(g.subjects(RDF.type, SKOS.Concept), key=str):
            pref = one(g, t, SKOS.prefLabel)
            anchor = f"term-{slug(pref)}" if pref in self.terms_on_page else ""
            self.add(t, "term", pref, one(g, t, SKOS.definition), f"ogc term {shell(pref)}", self.page("glossary", anchor))
        for s in sorted(g.subjects(RDF.type, OGC.Source), key=str):
            desc = f"{one(g, s, RDFS.label)} Rank {one(g, s, OGC.rank)}, posture {one(g, s, OGC.posture)}."
            self.add(s, "source", local(s), desc, f"ogc source {local(s)}", self.page("glossary"))
        # citations are blank nodes: give each an id from what it cites, in a stable order
        seen: dict[str, int] = {}
        for subj in sorted(set(g.subjects(OGC.canonical, None)) | set(g.subjects(OGC.seeAlso, None)), key=str):
            cites = []
            for pred in (OGC.canonical, OGC.seeAlso):
                for c in g.objects(subj, pred):
                    cites.append((local(pred), one(g, c, OGC.cites), one(g, c, OGC.locator), one(g, c, OGC.quote), c))
            for pred, src, loc, quote, c in sorted(cites, key=lambda x: (x[0], x[1], x[2], x[3])):
                base = f"cite:{local(subj)}:{pred}:{local(src)}:{slug(loc)}"
                n = seen.get(base, 0)
                seen[base] = n + 1
                nid = base if n == 0 else f"{base}:{n}"
                status = one(g, c, OGC.quoteStatus)
                desc = (f"“{quote}”" if quote else "No quote; a locator only.") + (f" [{status}]" if status else "")
                if subj in self.ids and self.nodes[self.ids[subj]]["cls"] == "term":
                    cmd = f"ogc quote {shell(one(g, subj, SKOS.prefLabel))}"
                elif (subj, RDF.type, OGC.Crosswalk) in g:
                    cmd = "ogc crosswalk --popper"
                else:
                    cmd = "ogc steps"
                page = self.nodes[self.ids[subj]]["page"] if subj in self.ids else ""
                self.add(c, "citation", f"{local(src)} {loc}", desc, cmd, page, nid=nid)

    # -- rulings and concerns
    def rulings(self):
        g = self.g
        for c in sorted(g.subjects(RDF.type, OGC.Concern), key=str):
            cid = local(c)
            desc = f"{one(g, c, RDFS.label)} ({one(g, c, OGC.severity)}, {one(g, c, OGC.status)}). {one(g, c, OGC.problem)}"
            self.add(c, "concern", cid, desc, f"ogc concern {cid}", self.page("rulings"))
        for r in sorted(g.subjects(RDF.type, OGC.Ruling), key=str):
            rid = local(r)
            self.add(r, "ruling", rid, one(g, r, OGC.rulingText), f"ogc ruling {rid}", self.page("rulings"))

    # -- essentials, shapes, crosswalk
    def essentials(self):
        g = self.g
        for t in sorted(g.subjects(RDF.type, OGC.Trace), key=str):
            sid = local(t)
            name = one(g, t, RDFS.label).split(" ", 1)[-1]
            self.add(t, "sci", sid, f"{name}: {one(g, t, RDFS.comment)} [{one(g, t, OGC.tag)}]", f"ogc sci {sid}", self.page(one(g, t, OGC.page)))
        for s in sorted(g.subjects(RDF.type, SH.NodeShape), key=str):
            name = local(s)
            msgs = sorted(str(m) for c in g.objects(s, SH.sparql) for m in g.objects(c, SH.message))
            msgs += sorted(str(m) for p in g.objects(s, SH.property) for m in g.objects(p, SH.message))
            target = one(g, s, SH.targetClass)
            desc = (f"Targets {qname(target)}. " if target else "") + " ".join(msgs)
            page = self.page("assemblage") if name.startswith("M") else self.page("record")
            self.add(s, "shape", name, desc or "A shape.", f"ogc sparql {shell(f'DESCRIBE ogc:{name}')}", page)
        for r in sorted(g.subjects(RDF.type, OGC.Crosswalk), key=lambda x: int(one(g, x, OGC.order, "0"))):
            desc = f"“{one(g, r, OGC.quote)}” Where: {one(g, r, OGC.where)} Checkable: {one(g, r, OGC.checkable)}"
            self.add(r, "crosswalk", f"row {one(g, r, OGC.order)}: {one(g, r, RDFS.label)}", desc, "ogc crosswalk --popper", self.page("index"))

    # -- the process: steps, item kinds, layers, roles
    def process(self):
        g = self.g
        for cls in (EPO.ContractingStep, EPO.EpoStep):
            for st in sorted(g.subjects(RDF.type, cls), key=str):
                label = one(g, st, RDFS.label)
                self.add(st, "step", label.split(":", 1)[0], label, "ogc steps", self.page("glossary"))
        for k in sorted(g.subjects(RDF.type, OWL.Class), key=str):
            if not str(k).startswith(str(EPO)) or k in (EPO.EpoStep, EPO.ContractingStep, EPO.Layer, EPO.Role):
                continue
            self.add(k, "kind", local(k), one(g, k, RDFS.label) or local(k), f"ogc sparql {shell(f'DESCRIBE epo:{local(k)}')}")
        for cls, fam in ((EPO.Layer, "layer"), (EPO.Role, "role")):
            for x in sorted(g.subjects(RDF.type, cls), key=str):
                self.add(x, fam, local(x), one(g, x, RDFS.label), f"ogc sparql {shell(f'DESCRIBE epo:{local(x)}')}")

    # -- the model: parts, ports, seams, the obligation, the two cycles and their steps, item defs
    def model(self):
        g = self.g

        def doc(n) -> str:
            bodies = sorted(str(g.value(d, SYS.body)) for d in g.subjects(SYS.owner, n) if (d, RDF.type, SYS.Documentation) in g)
            return " ".join(bodies) or one(g, n, V.SYS.qualifiedName)

        def qual(n) -> str:
            return one(g, n, SYS.qualifiedName).replace(f"{V.TOP_PACKAGE}::", "", 1)

        parts = sorted(g.subjects(RDF.type, SYS.PartDefinition), key=str)
        for d in parts:
            self.add(d, "part", qual(d), doc(d), "ogc view assemblage", self.page("assemblage"))
        for d in parts:
            for p in sorted(g.subjects(SYS.owner, d), key=str):
                if (p, RDF.type, SYS.PortUsage) in g:
                    direction = "in" if g.value(p, SYS.isConjugated) else "out"
                    self.add(p, "port", qual(p), f"{direction} port typed {V.name(g, g.value(p, SYS.type))}, carrying {V.item_of_port_def(g, g.value(p, SYS.type))}.",
                             "ogc view assemblage", self.page("assemblage"))
        for u in sorted(g.subjects(RDF.type, SYS.PartUsage), key=str):
            self.add(u, "usage", f"{qual(u)} : {V.name(g, g.value(u, SYS.type))}", doc(u), "ogc view assemblage", self.page("assemblage"))
        for s in sorted(g.subjects(RDF.type, SYS.InterfaceUsage), key=str):
            slice_ = V.seam_slice(g, s)
            page = self.page("contracting") if slice_ == "contracting" else self.page("assemblage")
            self.add(s, "seam", qual(s), one(g, s, Namespace("urn:opensysml:sysml:").sourceText) or doc(s), f"ogc view {slice_}", page)
            item = next((d for d in g.subjects(RDF.type, SYS.ItemDefinition) if V.name(g, d) == V.seam_item(g, s)), None)
            if item is not None:
                self.derived.append((str(s), str(item), "carries"))
        for c in sorted(g.subjects(RDF.type, SYS.ConnectionUsage), key=str):
            self.add(c, "relation", qual(c), one(g, c, Namespace("urn:opensysml:sysml:").sourceText) or doc(c), "ogc view contracting", self.page("contracting"))
        for a in sorted(g.subjects(RDF.type, SYS.ActionDefinition), key=str):
            self.add(a, "process", qual(a), doc(a), "ogc view layers", self.page("assemblage"))
            for st in sorted(g.subjects(SYS.owner, a), key=str):
                if (st, RDF.type, SYS.ActionUsage) not in g:
                    continue
                self.add(st, "action", qual(st), doc(st), "ogc view layers", self.page("assemblage"))
                for p in sorted(g.subjects(SYS.owner, st), key=str):
                    if (p, RDF.type, SYS.ReferenceUsage) in g and g.value(p, SYS.type) is not None:
                        self.derived.append((str(st), str(g.value(p, SYS.type)), str(g.value(p, SYS.direction))))
            for s in g.subjects(RDF.type, SYS.SuccessionAsUsage):
                if g.value(s, SYS.owner) == a:
                    self.derived.append((str(g.value(s, OGM["first"])), str(g.value(s, OGM["then"])), "then"))
        for d in sorted(g.subjects(RDF.type, SYS.ItemDefinition), key=str):
            self.add(d, "item", qual(d), doc(d), "ogc view layers", self.page("assemblage"))
        # the binding by name between the model and the EPO handles (epo:step in the record relies on it)
        for st in g.subjects(RDF.type, SYS.ActionUsage):
            e = EPO[V.name(g, st)]
            if str(e) in self.nodes:
                self.derived.append((str(st), str(e), "corresponds"))
        for d in g.subjects(RDF.type, SYS.ItemDefinition):
            e = EPO[V.name(g, d)]
            if str(e) in self.nodes:
                self.derived.append((str(d), str(e), "corresponds"))

    # -- the record: the measles run
    def record(self):
        g = self.g
        contracting = {str(s) for s in g.subjects(RDF.type, EPO.ContractingStep)}
        for n in sorted({s for s in g.subjects() if isinstance(s, URIRef) and str(s).startswith(str(RUN))}, key=str):
            types = sorted(qname(t) for t in g.objects(n, RDF.type))
            kind = next((local(t) for t in g.objects(n, RDF.type) if str(t).startswith(str(EPO))), "")
            is_agent = (n, RDF.type, PROV.Agent) in g
            label = one(g, n, RDFS.label) or one(g, n, EPO.text) or local(n)
            desc = f"{label} Types: {', '.join(types)}." + (f" {one(g, n, SKOS.note)}" if one(g, n, SKOS.note) else "")
            step = g.value(n, EPO.step)
            page = self.page("contracting") if step is not None and str(step) in contracting else self.page("record")
            cmd = f"ogc record {shell(local(n))}"  # the reader of the record (ruling R-47, closing C-44): everything the record says about this item
            self.add(n, "agent" if is_agent else "record", local(n), desc, cmd, page)

    # -- links and detail
    def build(self) -> dict:
        g = self.g
        self.vocabulary(); self.rulings(); self.essentials(); self.process(); self.model(); self.record()
        links: set[tuple[str, str, str]] = set()
        # detail[id].out: every statement with the node as subject, as [predicate, object] where the
        # object is {"ref": node id} or {"text": ...}; detail[id].in: only statements whose subject is
        # not a node (a blank node or an IRI outside the explorer); the page derives node-to-node
        # incoming statements from the out lists, so nothing is stored twice.
        detail: dict[str, dict] = {nid: {"out": [], "in": []} for nid in self.nodes}

        def bnode_text(b, skip=None) -> str:
            parts = sorted(f"{qname(p)} {short(str(v), 40)}" for p, v in g.predicate_objects(b) if not isinstance(v, BNode) and v != skip)
            return "[" + "; ".join(parts) + "]"

        def obj(o) -> dict:
            if o in self.ids:
                return {"ref": self.ids[o]}
            if isinstance(o, Literal):
                v = str(o)
                if o.datatype is not None and local(o.datatype) not in ("string", "boolean", "integer", "decimal"):
                    v = f"{v} ({local(o.datatype)})"
                return {"text": v}
            if isinstance(o, BNode):
                return {"text": bnode_text(o)}
            return {"text": qname(o)}

        for s, p, o in g:
            sid = self.ids.get(s)
            oid = self.ids.get(o)
            if sid is not None:
                detail[sid]["out"].append((qname(p), obj(o)))
            if oid is not None and sid != oid:
                if sid is not None:
                    links.add((sid, oid, local(p)))
                elif isinstance(s, BNode):
                    detail[oid]["in"].append((qname(p), {"text": bnode_text(s, skip=o)}))
                else:
                    detail[oid]["in"].append((qname(p), {"text": qname(s)}))
        for a, b, rel in self.derived:
            if a in self.nodes and b in self.nodes and a != b:
                links.add((a, b, rel))
                detail[a]["out"].append((f"{rel} (derived)", {"ref": b}))
        for d in detail.values():
            for key in ("out", "in"):
                d[key] = [list(x) for x in sorted(d[key], key=lambda x: (x[0], json.dumps(x[1], sort_keys=True)))]
        nodes = [self.nodes[k] for k in sorted(self.nodes)]
        link_list = [dict(source=a, target=b, rel=r) for a, b, r in sorted(links)]
        return dict(title=TITLE, nodes=nodes, links=link_list, views=self.views(nodes, link_list), detail=detail,
                    families=[dict(cls=c, color=col, glyph=gl, r=r, text=t) for c, col, gl, r, t in FAMILIES])

    def views(self, nodes: list[dict], links: list[dict]) -> list[dict]:
        by_cls: dict[str, set[str]] = {}
        for n in nodes:
            by_cls.setdefault(n["cls"], set()).add(n["id"])
        cls_of = {n["id"]: n["cls"] for n in nodes}

        def touching(core: set[str], cls: str) -> set[str]:
            return {l[k] for l in links for k, other in (("source", "target"), ("target", "source"))
                    if l[other] in core and cls_of[l[k]] == cls}

        def of(*classes: str) -> set[str]:
            return set().union(*(by_cls.get(c, set()) for c in classes))

        run_core = of("record", "agent")
        rul_core = of("concern", "ruling")
        sci_core = of("sci", "shape")
        xw_core = of("crosswalk")
        spec = [
            ("vocabulary", "Vocabulary",
             "every glossary term, the source it cites and the citation that carries the verbatim quote, canonical or neighbour.",
             "the rulings that settled a term, the essentials stated in it, and the model that binds it.",
             of("term", "source", "citation")),
            ("rulings", "Rulings",
             "every concern, the ruling that resolved it, and the terms a concern names or a ruling derives.",
             "the sources, the citations and the record; a ruling's words are in the panel, not on the canvas.",
             rul_core | touching(rul_core, "term")),
            ("process", "Process",
             "the two cycles as the standards' steps, the item kinds each step consumes and produces, and the layer at which each kind is pinned.",
             "who performs a step and over which wire; the parts and the ports are in the wiring view.",
             of("step", "kind", "layer", "process", "action", "item")),
            ("wiring", "Wiring",
             "the parts of the assemblage, their ports, the seams that join an output port to an input port with the item kind that flows, and the one relation that carries no item.",
             "the steps and their order; the record; the vocabulary the part names come from.",
             of("part", "usage", "port", "seam", "relation", "item")),
            ("record", "Record",
             "the measles run: every recorded item, the agent that produced, signed or attested it, and the provenance chain between them.",
             "the step and the kind each item instantiates, one click away in the panel; the vocabulary and the rulings.",
             run_core),
            ("essentials", "Essentials",
             "the thirteen essentials, the shapes that check each (M over the model graph, S over the record), and the terms each is stated in.",
             "what each essential rests on, sources and rulings, and the record the S-shapes run over.",
             sci_core | touching(of("sci"), "term")),
            ("crosswalk", "Crosswalk",
             "the front page's bridge as data: each row of the crosswalk, the terms it lands on, the kinds and shapes that realize it, and the session it cites.",
             "everything on the far side of the bridge a row does not name; a row's own words are in the panel.",
             xw_core | touching(xw_core, "term") | touching(xw_core, "kind") | touching(xw_core, "shape") | touching(xw_core, "source")),
            ("everything", "Everything",
             "every node and every link the explorer holds, as one graph.",
             "legibility; use it to see the shape of the whole and a view to read a part.",
             set(cls_of)),
        ]
        return [dict(id=i, label=lab, focus=f, leaves_out=lo, present=sorted(p)) for i, lab, f, lo, p in spec]


# --- the page --------------------------------------------------------------

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
  :root{color-scheme:dark}
  body{margin:0;font:13px/1.4 system-ui,sans-serif;background:#0f1115;color:#e6e6e6;overflow:hidden}
  svg{position:fixed;inset:0;width:100vw;height:100vh}
  header{position:fixed;top:0;left:0;right:0;z-index:7;padding:6px 12px;display:flex;gap:8px;
         align-items:baseline;flex-wrap:wrap;background:#171a21ee;border-bottom:1px solid #2a2f3a}
  header h1{font-size:13px;margin:0;font-weight:600;white-space:nowrap}
  #views{display:flex;gap:5px;flex-wrap:wrap}
  #views button{background:#2a2f3a;color:#e6e6e6;border:1px solid #3a4150;border-radius:6px;padding:2px 8px;cursor:pointer;font-size:11px}
  #views button:hover{background:#333a48}
  #views button[aria-pressed="true"]{background:#3d5afe33;border-color:#7986cb;color:#fff}
  #search{margin-left:auto;position:relative}
  #search input{background:#0f1115;color:#e6e6e6;border:1px solid #3a4150;border-radius:6px;padding:2px 8px;font-size:11px;width:180px}
  #hits{position:absolute;right:0;top:22px;background:#171a21;border:1px solid #3a4150;border-radius:6px;min-width:240px;max-height:260px;overflow-y:auto;display:none;z-index:9}
  #hits div{padding:3px 8px;cursor:pointer;font-size:11px;white-space:nowrap}
  #hits div:hover{background:#2a2f3a}
  #hits .c{color:#9aa4b2;margin-left:6px}
  #viewdesc{flex-basis:100%;color:#9aa4b2;font-size:11.5px;min-height:1.2em}
  #viewdesc b{color:#c8cfda;font-weight:600}
  .link{stroke:#3a4150;stroke-width:1;stroke-opacity:.8}
  .link.derived{stroke-dasharray:3 3}
  .node text{font-size:9.5px;fill:#c8cfda;pointer-events:none}
  .node{cursor:pointer}
  #legend{position:fixed;right:12px;bottom:12px;z-index:5;background:#171a21cc;border:1px solid #2a2f3a;border-radius:8px;
          padding:6px 10px;font-size:10.5px;max-width:230px;max-height:45vh;overflow-y:auto}
  #legend .row{display:flex;align-items:center;gap:6px;margin:1px 0}
  #legend .g{width:14px;text-align:center;font-size:12px}
  #legend summary{cursor:pointer;font-weight:600}
  #tip{position:fixed;pointer-events:none;background:#000d;border:1px solid #3a4150;border-radius:6px;padding:5px 8px;font-size:11.5px;
       max-width:320px;display:none;z-index:9;white-space:pre-line}
  #detail{position:fixed;left:12px;top:76px;bottom:12px;width:360px;z-index:5;overflow-y:auto;background:#171a21ee;
          border:1px solid #2a2f3a;border-radius:8px;padding:10px 14px;font-size:12px}
  #detail .empty{color:#6a7480;font-style:italic}
  #detail h2{font-size:14px;margin:0 0 2px;color:#fff;overflow-wrap:anywhere}
  #detail .chip{display:inline-block;font-size:10px;text-transform:uppercase;letter-spacing:.5px;border:1px solid #3a4150;
                border-radius:10px;padding:1px 8px;margin:0 4px 8px 0;color:#9aa4b2}
  #detail .desc{color:#c8cfda;line-height:1.45;margin:6px 0 8px;white-space:pre-line}
  #detail h3{font-size:10px;margin:12px 0 4px;color:#9aa4b2;text-transform:uppercase;letter-spacing:.6px;border-top:1px solid #2a2f3a;padding-top:8px}
  #detail ul{margin:2px 0;padding-left:14px}
  #detail li{margin:3px 0;line-height:1.4;overflow-wrap:anywhere}
  #detail .dim{color:#828c9a}
  #detail .ref{color:#7ab3ef;cursor:pointer;text-decoration:underline dotted}
  #detail .ref:hover{color:#a8cff5}
  #detail code{display:block;background:#0f1115;border:1px solid #2a2f3a;border-radius:6px;padding:5px 8px;font-size:11.5px;
               overflow-wrap:anywhere;user-select:all}
  #detail a{color:#7ab3ef}
  #sparql{position:fixed;left:12px;bottom:12px;z-index:6;width:360px;background:#171a21ee;border:1px solid #2a2f3a;border-radius:8px;font-size:12px}
  #sparql summary{cursor:pointer;padding:6px 12px;font-weight:600}
  #sparql .body{padding:0 12px 10px}
  #sparql textarea{width:100%;box-sizing:border-box;height:110px;background:#0f1115;color:#e6e6e6;border:1px solid #3a4150;border-radius:6px;
                   font:11px/1.4 ui-monospace,Menlo,monospace;padding:6px}
  #sparql button{background:#2a2f3a;color:#e6e6e6;border:1px solid #3a4150;border-radius:6px;padding:2px 10px;cursor:pointer;font-size:11px;margin-top:4px}
  #sparql .status{color:#9aa4b2;font-size:11px;margin:4px 0}
  #sparql .out{max-height:200px;overflow:auto;margin-top:4px}
  #sparql table{border-collapse:collapse;font-size:10.5px;white-space:nowrap}
  #sparql td,#sparql th{border:1px solid #2a2f3a;padding:2px 5px;text-align:left}
  #sparql th{color:#9aa4b2;font-weight:600}
  #full{font-size:11px;color:#7ab3ef;white-space:nowrap;display:none}
  #close{float:right;background:none;border:none;color:#9aa4b2;font-size:16px;cursor:pointer;padding:0 2px;display:none}
  body.embed #viewdesc{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
  body.embed #detail{width:min(300px,70vw)}
  body.embed #detail.idle{display:none}
  body.embed #close,body.embed #full{display:inline}
  body.embed #sparql{display:none}
  body.embed #legend{max-width:170px;max-height:35vh}
</style></head>
<body>
<svg id="graph"></svg>
<header>
  <h1>__TITLE__</h1>
  <nav id="views"></nav>
  <div id="search"><input id="q" type="search" placeholder="find a node" autocomplete="off"><div id="hits"></div></div>
  <a id="full" href="../explorer/index.html" target="_top" title="open the explorer in the whole window">full screen ↗</a>
  <span id="viewdesc"></span>
</header>
<aside id="detail" class="idle"><div class="empty">click a node to read it; drag to pin, double-click to release</div></aside>
<details id="legend" open><summary>legend</summary><div id="legendrows"></div></details>
<details id="sparql"><summary>SPARQL over the same graphs</summary><div class="body">
  <textarea id="qtext" spellcheck="false"></textarea>
  <div><button id="run">run</button> <span class="status" id="qstatus">SELECT queries; prefixes are injected; the store loads on first run.</span></div>
  <div class="out" id="qout"></div>
</div></details>
<div id="tip"></div>
<script>/*__D3__*/</script>
<script>
const MODEL = /*__DATA__*/;
const NODES = MODEL.nodes.map(n=>Object.assign({},n));
const ALL_LINKS = MODEL.links.map(e=>({source:e.source,target:e.target,rel:e.rel}));
const VIEWS = MODEL.views, DETAIL = MODEL.detail, FAM = Object.fromEntries(MODEL.families.map(f=>[f.cls,f]));
const DERIVED = new Set(["carries","in","out","then","corresponds"]);
const byId = new Map(NODES.map(n=>[n.id,n]));
const GLYPH = {circle:d3.symbolCircle, diamond:d3.symbolDiamond, square:d3.symbolSquare, triangle:d3.symbolTriangle};
let cur = 0, selectedId = null;
const view = ()=>VIEWS[cur];
// embedded in the appendix (an iframe, or a small window): panels give way to the canvas until a node is clicked
const EMBED = (window.self !== window.top) || window.innerHeight < 560;
if(EMBED){ document.body.classList.add("embed"); document.getElementById("legend").open = false; }
const radius = d=>(FAM[d.cls]||{r:6}).r;
const color = d=>(FAM[d.cls]||{color:"#78909c"}).color;
const symPath = d=>d3.symbol().type(GLYPH[(FAM[d.cls]||{}).glyph]||d3.symbolCircle).size(Math.PI*radius(d)*radius(d)*1.4)();

const svg = d3.select("#graph"), tip = d3.select("#tip");
const W = window.innerWidth, H = window.innerHeight;
svg.attr("viewBox",[0,0,W,H]);
const g = svg.append("g");
const linkLayer = g.append("g"), nodeLayer = g.append("g");
const zoom = d3.zoom().scaleExtent([.15,5]).on("zoom",ev=>g.attr("transform",ev.transform));
svg.call(zoom);
let fitTimer = null;
function fit(){  // zoom so the current view's nodes fill the canvas beside the panels, once the layout has settled
  const nodes = sim.nodes(); if(!nodes.length) return;
  const xs = nodes.map(d=>d.x), ys = nodes.map(d=>d.y);
  const x0 = Math.min(...xs)-30, x1 = Math.max(...xs)+120, y0 = Math.min(...ys)-30, y1 = Math.max(...ys)+30;
  const hh = document.querySelector("header").offsetHeight;
  const left = (EMBED || detailEl.classList.contains("idle")) ? 0 : 390;
  const k = Math.max(.15, Math.min(2.5, .95*Math.min((W-left)/(x1-x0), (H-hh)/(y1-y0))));
  const t = d3.zoomIdentity.translate(left+(W-left)/2-k*(x0+x1)/2, hh+(H-hh)/2-k*(y0+y1)/2).scale(k);
  svg.transition().duration(500).call(zoom.transform, t);
}
function scheduleFit(){ clearTimeout(fitTimer); fitTimer = setTimeout(fit, 1400); }
let linkSel = linkLayer.selectAll("line"), nodeSel = nodeLayer.selectAll("g");
const sim = d3.forceSimulation()
  .force("link",d3.forceLink().id(d=>d.id).distance(l=>40+radius(l.source)+radius(l.target)).strength(.4))
  .force("charge",d3.forceManyBody().strength(-160))
  .force("center",d3.forceCenter(W*.58,H*.54))
  .force("x",d3.forceX(W*.58).strength(.05))
  .force("y",d3.forceY(H*.54).strength(.07))
  .force("collide",d3.forceCollide().radius(d=>radius(d)+6))
  .on("tick",()=>{
    linkSel.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y).attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
    nodeSel.attr("transform",d=>`translate(${d.x},${d.y})`);
  });

function nodeStroke(d){ return d.id===selectedId ? "#fff" : "#0b0d11"; }
function paint(){
  const present = new Set(view().present);
  const nodes = NODES.filter(n=>present.has(n.id));
  const links = ALL_LINKS.filter(l=>present.has(typeof l.source==="string"?l.source:l.source.id)&&present.has(typeof l.target==="string"?l.target:l.target.id));
  const showLabels = nodes.length <= 320;
  linkSel = linkLayer.selectAll("line").data(links, l=>`${typeof l.source==="string"?l.source:l.source.id}|${typeof l.target==="string"?l.target:l.target.id}|${l.rel}`)
    .join("line").attr("class",l=>"link"+(DERIVED.has(l.rel)?" derived":""))
    .on("mousemove",(ev,l)=>{tip.style("display","block").style("left",(ev.clientX+12)+"px").style("top",(ev.clientY+12)+"px")
        .text(`${byId.get(l.source.id||l.source).label}\n  ${l.rel}\n${byId.get(l.target.id||l.target).label}`);})
    .on("mouseout",()=>tip.style("display","none"));
  nodeSel = nodeLayer.selectAll("g").data(nodes, d=>d.id).join(enter=>{
      const e = enter.append("g").attr("class","node")
        .call(d3.drag()
          .on("start",(ev,d)=>{if(!ev.active)sim.alphaTarget(.3).restart();d.fx=d.x;d.fy=d.y;})
          .on("drag",(ev,d)=>{d.fx=ev.x;d.fy=ev.y;})
          .on("end",(ev,d)=>{if(!ev.active)sim.alphaTarget(0);}))
        .on("dblclick",(ev,d)=>{d.fx=null;d.fy=null;sim.alphaTarget(.2).restart();setTimeout(()=>sim.alphaTarget(0),400);ev.stopPropagation();})
        .on("click",(ev,d)=>{showDetail(d.id);ev.stopPropagation();})
        .on("mousemove",(ev,d)=>{tip.style("display","block").style("left",(ev.clientX+12)+"px").style("top",(ev.clientY+12)+"px")
            .text(`${d.label}\n${(FAM[d.cls]||{text:d.cls}).text}\n${d.desc.length>220?d.desc.slice(0,219)+"…":d.desc}`);})
        .on("mouseout",()=>tip.style("display","none"));
      e.append("path"); e.append("text").attr("y",3); return e; });
  nodeSel.select("path").attr("d",symPath).attr("fill",color).attr("stroke",nodeStroke).attr("stroke-width",d=>d.id===selectedId?2.4:1.2);
  nodeSel.select("text").attr("x",d=>radius(d)+3).text(d=>showLabels||d.id===selectedId?d.label:"");
  nodeSel.style("opacity",1);
  sim.nodes(nodes); sim.force("link").links(links);
  sim.alpha(.6).restart(); scheduleFit();
  const v = view();
  const desc = d3.select("#viewdesc").text("");
  desc.append("b").text("In focus: "); desc.append("span").text(v.focus+" ");
  desc.append("b").text("Left out: "); desc.append("span").text(v.leaves_out+` (${nodes.length} nodes, ${links.length} links)`);
  d3.select("#views").selectAll("button").attr("aria-pressed",(x,i)=>String(i===cur));
  writeHash();
}
function repaintSelection(){
  nodeSel.select("path").attr("stroke",nodeStroke).attr("stroke-width",d=>d.id===selectedId?2.4:1.2);
}
d3.select("#views").selectAll("button").data(VIEWS).join("button").attr("aria-pressed","false").attr("title",v=>`In focus: ${v.focus} Left out: ${v.leaves_out}`)
  .text(v=>v.label).on("click",(ev,v)=>{cur=VIEWS.indexOf(v);paint();});

// --- detail panel: everything the graph says about the node; refs click-navigate; all prose via textContent ---
const detailEl = document.getElementById("detail");
function el(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!=null)e.textContent=text;return e;}
function refSpan(r){ if(r.ref&&byId.has(r.ref)){const s=el("span","ref",byId.get(r.ref).label);s.dataset.ref=r.ref;return s;} return el("span",null,r.text!=null?r.text:r.ref); }
// incoming statements between nodes are derived from the outgoing lists, so the data holds each statement once
const INCOMING = new Map(NODES.map(n=>[n.id,[]]));
for(const [id,d] of Object.entries(DETAIL)) for(const [p,o] of d.out) if(o.ref&&INCOMING.has(o.ref)) INCOMING.get(o.ref).push([p,{ref:id}]);
function section(title){detailEl.appendChild(el("h3",null,title));const ul=el("ul");detailEl.appendChild(ul);return ul;}
function showDetail(id){
  const n = byId.get(id), d = DETAIL[id]; if(!n||!d) return;
  selectedId = id;
  if(!view().present.includes(id)){ cur = VIEWS.findIndex(v=>v.present.includes(id)); if(cur<0) cur = VIEWS.length-1; paint(); } else { repaintSelection(); writeHash(); }
  detailEl.textContent = ""; detailEl.classList.remove("idle");
  const close = el("button",null,"×"); close.id = "close"; close.title = "close"; close.addEventListener("click",clearDetail); detailEl.appendChild(close);
  detailEl.appendChild(el("h2",null,n.label));
  detailEl.appendChild(el("span","chip",(FAM[n.cls]||{text:n.cls}).text));
  detailEl.appendChild(el("div","desc",n.desc));
  detailEl.appendChild(el("h3",null,"ask the machine"));
  detailEl.appendChild(el("code",null,"uv run -q "+n.ogc));
  if(n.page){ const h=el("h3",null,"rendered on the site"); detailEl.appendChild(h);
    const a=el("a",null,n.page.replace(/^\.\.\//,"").split("#")[0]||"front page"); a.href=n.page; a.target="_top"; detailEl.appendChild(a); }
  if(d.out.length){ const ul=section("the node says"); for(const [p,o] of d.out){ const li=el("li"); li.appendChild(el("span","dim",p+" ")); li.appendChild(refSpan(o)); ul.appendChild(li);} }
  const incoming = INCOMING.get(id).map(([p,s])=>[p,s,byId.get(s.ref).label]).sort((a,b)=>a[0].localeCompare(b[0])||a[2].localeCompare(b[2])).map(x=>[x[0],x[1]]).concat(d.in);
  if(incoming.length){ const ul=section("said of the node"); for(const [p,s] of incoming){ const li=el("li"); li.appendChild(refSpan(s)); li.appendChild(el("span","dim"," "+p)); ul.appendChild(li);} }
  const ids = new Set(view().present);
  const nb = ALL_LINKS.filter(l=>{const a=l.source.id||l.source,b=l.target.id||l.target;return (a===id||b===id)&&(ids.has(a)&&ids.has(b));}).length;
  detailEl.appendChild(el("div","dim",`${nb} links in this view; the id is ${id}`));
  detailEl.scrollTop = 0;
}
detailEl.addEventListener("click",ev=>{const r=ev.target&&ev.target.dataset&&ev.target.dataset.ref; if(r) showDetail(r);});
function clearDetail(){ selectedId=null; repaintSelection(); detailEl.textContent=""; detailEl.classList.add("idle");
  detailEl.appendChild(el("div","empty","click a node to read it; drag to pin, double-click to release")); writeHash(); }
svg.on("click",()=>{ if(selectedId) clearDetail(); });

// --- search: label substring, jump to the node ---
const q = document.getElementById("q"), hits = document.getElementById("hits");
q.addEventListener("input",()=>{
  const s = q.value.trim().toLowerCase(); hits.textContent="";
  if(!s){hits.style.display="none";return;}
  const m = NODES.filter(n=>n.label.toLowerCase().includes(s)||n.id.toLowerCase().includes(s)).slice(0,14);
  for(const n of m){ const d=el("div",null,n.label); d.appendChild(el("span","c",n.cls)); d.addEventListener("click",()=>{showDetail(n.id);hits.style.display="none";q.value="";}); hits.appendChild(d); }
  hits.style.display = m.length?"block":"none";
});
q.addEventListener("keydown",ev=>{ if(ev.key==="Enter"&&hits.firstChild) hits.firstChild.click(); if(ev.key==="Escape"){hits.style.display="none";} });

// --- legend ---
const L = d3.select("#legendrows");
const GL = {circle:"●",diamond:"◆",square:"■",triangle:"▲"};
for(const f of MODEL.families){ const r=L.append("div").attr("class","row"); r.append("span").attr("class","g").style("color",f.color).text(GL[f.glyph]||"●"); r.append("span").text(f.text); }
{ const r=L.append("div").attr("class","row"); r.append("span").attr("class","g").text("┈"); r.append("span").text("derived link (carries, in, out, then, corresponds)"); }

// --- SPARQL box (optional): oxigraph in WebAssembly over copies of the Turtle files; needs the site served over http ---
const DATA_FILES = /*__FILES__*/;
const PREFIXES = /*__PREFIXES__*/;
document.getElementById("qtext").value = "SELECT ?term ?definition WHERE {\n  ?term a skos:Concept ; skos:prefLabel ?l ; skos:definition ?definition .\n  FILTER(CONTAINS(LCASE(STR(?l)), \"evidence\"))\n} ORDER BY ?term";
let store = null;
async function getStore(){
  if(store) return store;
  const st = document.getElementById("qstatus"); st.textContent = "loading oxigraph and the Turtle files…";
  const mod = await import(new URL("../explorer/vendor/oxigraph/web.js", location.href).href);
  await mod.default();
  const s = new mod.Store();
  for(const f of DATA_FILES){
    const r = await fetch(new URL("../explorer/data/"+f, location.href).href);
    if(!r.ok) throw new Error(`could not fetch ${f}: ${r.status}`);
    s.load(await r.text(), {format:"text/turtle", base_iri:"https://w3id.org/og-caie/"});
  }
  store = s; st.textContent = `${s.size} triples loaded.`; return s;
}
document.getElementById("run").addEventListener("click", async ()=>{
  const st = document.getElementById("qstatus"), out = document.getElementById("qout"); out.textContent = "";
  try{
    const s = await getStore();
    const res = s.query(PREFIXES + document.getElementById("qtext").value);
    if(!Array.isArray(res) || !res.length){ st.textContent = typeof res==="boolean" ? `ASK: ${res}` : "no rows"; return; }
    if(!(res[0] instanceof Map)){ st.textContent = `${res.length} triples (CONSTRUCT and DESCRIBE render as text)`; out.appendChild(el("pre",null,res.slice(0,200).map(q=>`${q.subject.value} ${q.predicate.value} ${q.object.value}`).join("\n"))); return; }
    const cols = [...res[0].keys()]; const t = el("table"); const th = el("tr"); for(const c of cols) th.appendChild(el("th",null,"?"+c)); t.appendChild(th);
    for(const row of res.slice(0,200)){ const tr=el("tr"); for(const c of cols){ const v=row.get(c); const td=el("td",null,v?(v.termType==="NamedNode"?shortIri(v.value):v.value):""); if(v&&v.termType==="NamedNode"&&byId.has(v.value)){td.className="ref";td.dataset.ref=v.value;} tr.appendChild(td);} t.appendChild(tr); }
    out.appendChild(t); st.textContent = `${res.length} rows${res.length>200?", first 200 shown":""}; a cell that is a node is clickable.`;
  }catch(e){ st.textContent = "SPARQL needs the site served over http (the WebAssembly store cannot load from a file: URL); use `uv run -q ogc sparql` instead. " + (e && e.message ? e.message : e); }
});
document.getElementById("qout").addEventListener("click",ev=>{const r=ev.target&&ev.target.dataset&&ev.target.dataset.ref; if(r) showDetail(r);});
function shortIri(v){ for(const [k,ns] of PREFIX_LIST) if(v.startsWith(ns)) return k+":"+v.slice(ns.length); return v; }
const PREFIX_LIST = PREFIXES.trim().split("\n").map(l=>{const m=l.match(/^PREFIX (\w*): <([^>]*)>/);return m?[m[1],m[2]]:null;}).filter(Boolean).sort((a,b)=>b[1].length-a[1].length);

function layout(){
  const hh = document.querySelector("header").offsetHeight;
  detailEl.style.top = (hh+12)+"px";
  detailEl.style.bottom = (document.getElementById("sparql").offsetHeight+24)+"px";
  const cy = hh + (H-hh)*.5, cx = EMBED ? W*.5 : W*.58;
  sim.force("center").x(cx).y(cy); sim.force("x").x(cx); sim.force("y").y(cy);
}
// deep links: #view=<view id>&node=<node id>, read on load and kept current, so a view or a node can be linked to
function readHash(){ const p = new URLSearchParams(location.hash.slice(1)); const v = VIEWS.findIndex(x=>x.id===p.get("view")); if(v>=0) cur=v; return p.get("node"); }
function writeHash(){ const p = new URLSearchParams(); p.set("view", view().id); if(selectedId) p.set("node", selectedId); try{ history.replaceState(null,"","#"+p.toString()); }catch(e){} }
const startNode = readHash();
paint(); layout();
if(startNode && byId.has(startNode)) showDetail(startNode);
window.addEventListener("resize",layout);
window.addEventListener("hashchange",()=>{ const n = readHash(); paint(); if(n && byId.has(n)) showDetail(n); });
document.getElementById("sparql").addEventListener("toggle",layout);
</script>
</body></html>
"""


def data_files() -> list[str]:
    return [Path(f).name for f in (*SOURCE_FILES, MODEL_FILE, RECORD_FILE)]


def sparql_prefixes() -> str:
    return "".join(f"PREFIX {k}: <{v}>\n" for k, v in sorted(QNAMES.items()))


def render(model: dict) -> str:
    d3 = (OUT / "vendor" / "d3.v7.min.js").read_text()
    data = json.dumps(model, ensure_ascii=False, sort_keys=True, separators=(",", ":")).replace("</", "<\\/")
    return (PAGE.replace("__TITLE__", TITLE).replace("/*__D3__*/", d3).replace("/*__DATA__*/", data)
            .replace("/*__FILES__*/", json.dumps(data_files())).replace("/*__PREFIXES__*/", json.dumps(sparql_prefixes())))


def main() -> int:
    OUT.mkdir(exist_ok=True)
    (OUT / "data").mkdir(exist_ok=True)
    for f in (*SOURCE_FILES, MODEL_FILE, RECORD_FILE):
        shutil.copyfile(ROOT / f, OUT / "data" / Path(f).name)
    model = Builder(graph()).build()
    (OUT / "graph.json").write_text(json.dumps(model, ensure_ascii=False, sort_keys=True, indent=1) + "\n")
    (OUT / "index.html").write_text(render(model))
    print(f"explorer: {len(model['nodes'])} nodes, {len(model['links'])} links, {len(model['views'])} views")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
