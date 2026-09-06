#!/usr/bin/env python3
"""Render the SysML model as RDF with the pinned OpenSysML converter, keep
only the terms in model/sysml_term_map.csv, resolve every interface and
succession end to the element it names, and write the canonical model
graph (model/og-caie.model.ttl) with its manifest (model/model_manifest.json).

Ruling R-22: the SysML source is the authoring view; this graph is the
canonical structure. The parsimony pattern (term map, manifest, triple
budget with a rationale) follows ADCS-lifecycle-demo/scripts/build_ontology.py.

Deterministic: same source, same converter, same term map, same bytes, on
every platform: the manifest names the converter by its pinned release and
digest file, not by the local binary, and records the raw conversion's size
but not its hash (the raw text is the converter's business; the pruned,
sorted graph is the artifact that must not drift).
Usage: uv run python scripts/prune_model.py [SOURCE.sysml OUT.ttl MANIFEST.json]
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, URIRef

ROOT = Path(__file__).resolve().parents[1]
SYSML = ROOT / "toolchain" / "bin" / "sysml"
PINNED = ROOT / "toolchain" / "sysml-binaries.sha256"
TOOL_VERSION = "v0.4.3"
TERM_MAP = ROOT / "model" / "sysml_term_map.csv"
SOURCE = ROOT / "model" / "og-caie.sysml"
OUT = ROOT / "model" / "og-caie.model.ttl"
MANIFEST = ROOT / "model" / "model_manifest.json"

SYS = Namespace("https://www.omg.org/spec/SysML#")
SYSX = Namespace("urn:opensysml:sysml:")
OGM = Namespace("https://w3id.org/og-caie/model#")
PREFIXES = {"sysml": SYS, "sysx": SYSX, "ogm": OGM, "elmt": Namespace("urn:sysmlv2:element:"),
            "expr": Namespace("urn:opensysml:expr:"), "xsd": Namespace("http://www.w3.org/2001/XMLSchema#")}

# Parsimony gate. The pruned graph is the canonical structure; it must stay
# small enough to read. Bumping is a deliberate act with a rationale.
#   2026-09-06 set 3600: the first pruned build of the structure-only model
#     (27 seams, 54 ports, 20 item kinds, 7 steps, one run binding names and
#     two party facts) is 2,997 triples of the converter's 10,693; about
#     500 headroom for further seams. Set from measurement, not a guess.
TRIPLE_BUDGET = 3600
TRIPLE_BUDGET_RATIONALE = ("Parsimony gate on the canonical model graph: the structure-only model "
                           "plus resolved ends; bump with a rationale when a seam or a party is added.")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_term_map():
    with TERM_MAP.open() as f:
        rows = list(csv.DictReader(f))
    classes, predicates = set(), {RDF.type}
    for r in rows:
        ns = {"omg": SYS, "opensysml": SYSX, "derived": OGM}[r["source"]]
        (classes if r["kind"] == "class" else predicates).add(ns[r["term"]])
    return rows, classes, predicates


def convert(source: Path) -> bytes:
    r = subprocess.run([str(SYSML), str(source), "-convert", "ttl"], cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr.decode())
        raise SystemExit(f"convert failed with exit {r.returncode}")
    return r.stdout


def feature_named(g: Graph, owner: URIRef, name: str):
    for f in g.subjects(SYS.owner, owner):
        if str(g.value(f, SYS.declaredName)) == name:
            return f
    raise SystemExit(f"unresolved chain step: {name} is not a feature of {owner}")


def resolve(g: Graph, expr: URIRef):
    """Return (feature, holder): the element an end expression names and the
    usage it is a feature of (None for a bare reference)."""
    kinds = set(g.objects(expr, RDF.type))
    if SYS.FeatureReferenceExpression in kinds:
        return g.value(expr, SYS.referent), None
    if SYS.FeatureChainExpression in kinds:
        head, _ = resolve(g, g.value(expr, SYS.argument))
        head_type = g.value(head, SYS.type)
        if head_type is None:
            raise SystemExit(f"chain head {head} has no type")
        return feature_named(g, head_type, str(g.value(expr, SYS.targetFeature))), head
    raise SystemExit(f"unexpected end expression {expr}: {kinds}")


def derive(raw: Graph, pruned: Graph) -> int:
    n = 0
    for iface in raw.subjects(RDF.type, SYS.InterfaceUsage):
        ends = list(raw.objects(iface, SYSX.relatedFeature))
        if len(ends) != 2:
            raise SystemExit(f"{iface}: {len(ends)} ends")
        for e in ends:
            port, holder = resolve(raw, e)
            pruned.add((e, OGM.resolvesTo, port)); n += 1
            if holder is not None:
                pruned.add((e, OGM.endPart, holder)); n += 1
            conj = raw.value(port, SYS.isConjugated)
            role = OGM.consumerPort if conj is not None and bool(conj.toPython()) else OGM.supplierPort
            pruned.add((iface, role, port)); n += 1
    for succ in raw.subjects(RDF.type, SYS.SuccessionAsUsage):
        ends = sorted(raw.objects(succ, SYSX.relatedFeature), key=lambda e: int(raw.value(e, SYSX.endIndex)))
        if len(ends) != 2:
            raise SystemExit(f"{succ}: {len(ends)} ends")
        pruned.add((succ, OGM["first"], resolve(raw, ends[0])[0])); n += 1
        pruned.add((succ, OGM["then"], resolve(raw, ends[1])[0])); n += 1
    return n


def prune(raw: Graph, classes, predicates) -> Graph:
    keep_nodes = {s for s, t in raw.subject_objects(RDF.type) if t in classes}
    out = Graph()
    for s, p, o in raw:
        if s in keep_nodes and p in predicates:
            if isinstance(o, URIRef) and (o, RDF.type, None) in raw and o not in keep_nodes:
                continue  # a pointer into a pruned node (a membership)
            out.add((s, p, o))
    return out


def qname(g: Graph, term) -> str:
    if isinstance(term, Literal):
        return term.n3(g.namespace_manager)
    for prefix, ns in PREFIXES.items():
        if str(term).startswith(str(ns)):
            local = str(term)[len(str(ns)):]
            if local and all(c.isalnum() or c in "_-." for c in local) and not local.startswith("."):
                return f"{prefix}:{local}"
    return f"<{term}>"


def serialize(g: Graph) -> str:
    """Sorted, prefix-shortened Turtle: deterministic by construction."""
    lines = [f"@prefix {p}: <{ns}> ." for p, ns in PREFIXES.items()]
    lines.append("")
    lines.append("# Canonical model graph of OG-CAIE (ruling R-22). Generated by scripts/prune_model.py")
    lines.append("# from model/og-caie.sysml with the pinned OpenSysML converter; do not edit by hand.")
    lines.append("")
    by_subject: dict = {}
    for s, p, o in g:
        by_subject.setdefault(s, {}).setdefault(p, []).append(o)
    for s in sorted(by_subject, key=lambda x: qname(g, x)):
        preds = by_subject[s]
        order = sorted(preds, key=lambda p: (p != RDF.type, qname(g, p)))
        lines.append(qname(g, s))
        for i, p in enumerate(order):
            objs = ", ".join(sorted(qname(g, o) for o in preds[p]))
            pn = "a" if p == RDF.type else qname(g, p)
            end = " ." if i == len(order) - 1 else " ;"
            lines.append(f"    {pn} {objs}{end}")
        lines.append("")
    return "\n".join(lines)


def build(source: Path, out: Path, manifest: Path | None) -> Graph:
    rows, classes, predicates = load_term_map()
    raw_bytes = convert(source)
    raw = Graph(); raw.parse(data=raw_bytes, format="turtle")
    pruned = prune(raw, classes, predicates)
    derived = derive(raw, pruned)
    for p, ns in PREFIXES.items():
        pruned.bind(p, ns)
    text = serialize(pruned)
    out.write_text(text)
    if manifest is not None:
        used_terms = {qname(pruned, t) for _, t in pruned.subject_objects(RDF.type)} | {qname(pruned, p) for p in set(pruned.predicates())}
        manifest.write_text(json.dumps({
            "source": {"path": str(source.relative_to(ROOT)), "sha256": sha(source.read_bytes())},
            "converter": {"release": f"OpenSysML {TOOL_VERSION}", "pinned_digests": str(PINNED.relative_to(ROOT)),
                          "pinned_digests_sha256": sha(PINNED.read_bytes()), "invocation": "-convert ttl"},
            "term_map": {"path": str(TERM_MAP.relative_to(ROOT)), "sha256": sha(TERM_MAP.read_bytes()), "terms": len(rows)},
            "raw": {"triples": len(raw)},
            "artifact": {"path": str(out.relative_to(ROOT)) if out.is_relative_to(ROOT) else out.name, "sha256": sha(text.encode()), "triples": len(pruned),
                         "derived_triples": derived, "terms_used": sorted(used_terms)},
            "triple_budget": {"value": TRIPLE_BUDGET, "headroom": TRIPLE_BUDGET - len(pruned), "rationale": TRIPLE_BUDGET_RATIONALE},
        }, indent=1, sort_keys=True) + "\n")
    if len(pruned) > TRIPLE_BUDGET:
        raise SystemExit(f"model graph exceeds triple budget: {len(pruned)} > {TRIPLE_BUDGET}")
    return pruned


def main(argv) -> int:
    if len(argv) == 3:
        build(Path(argv[0]), Path(argv[1]), Path(argv[2]) if argv[2] != "-" else None)
    else:
        build(SOURCE, OUT, MANIFEST)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
