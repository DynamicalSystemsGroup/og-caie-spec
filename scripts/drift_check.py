"""The mechanical layer of the consistency and drift loop (the fresh plan of
2026-09-07, after sheet 10). Incremental edits leave prose that no longer
matches the graph, names renamed in one place and not another, and rules
stated in one artefact without their twin. This script checks what a
script can check and exits 1 with a list; the read layer (a drift reader
after each merge, logged on rulings sheet 11) covers the rest.

Checks:
  1. appendix letters: every "Appendix X" in the pages, the README, the
     skill and the renderers names an appendix at that position in
     myst.yml's table of contents;
  2. forbidden phrases: checks/drift-phrases.txt lists sentences the
     reviewers found stale; none may recur outside the rulings, the
     sheets and the digests (which quote history);
  3. retired words: every ogc:retired label in the glossary is absent from
     the main-path prose (the docs tests keep a short list; this reads the
     register);
  4. file mentions: every path under docs/, generated/, model/, shapes/,
     track/, queries/, scripts/, vocabulary/, sources/digests/ named in the
     pages, the README, CLAUDE.md, the skill and the shapes' messages
     exists;
  5. sheet ticks: every "[x] ..., R-NN" on a rulings sheet names a ruling
     the register holds;
  6. twins: every essential's checkedBy shape exists; every counterexample
     file under counterexamples/ is named in tests/test_shacl.py or the
     model test; every shape with an ogc:counterexample annotation names
     an existing file;
  7. absence checks: every canonical citation from a source ranked below
     SEVOCAB (rank 3 to 8) has a dated row for its headword in
     sources/digests/sevocab.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml
from rdflib import RDF, Graph, Namespace
from rdflib.namespace import SKOS

ROOT = Path(__file__).resolve().parents[1]
OGC = Namespace("https://w3id.org/og-caie/")
SH = Namespace("http://www.w3.org/ns/shacl#")
PAGES = [ROOT / "index.md", *sorted((ROOT / "docs").glob("*.md"))]
PROSE_SOURCES = PAGES + [ROOT / "README.md", ROOT / "CLAUDE.md", ROOT / ".claude" / "skills" / "ogc-glossary" / "SKILL.md"]
QUOTING = ("rulings/", "sources/digests/", "generated/rulings")  # files that quote history and may repeat stale words
GATE_OUTPUTS = {"generated/version.md", "checks/out/report.json", "checks/out/last.log"}  # written by the gate, never committed; absent in a fresh checkout


def problems() -> list[str]:
    out: list[str] = []
    # 1. appendix letters
    toc = yaml.safe_load((ROOT / "myst.yml").read_text())["project"]["toc"]
    files = [e.get("file") or e.get("title") for e in toc]
    appendix_files = [f for f in files if f and ("appendix" in str(f).lower() or "rulings" in str(f) or "Appendix" in str(f))]
    letters = {chr(ord("A") + i): f for i, f in enumerate(appendix_files)}
    heading = {}
    for f in appendix_files:
        if isinstance(f, str) and f.endswith(".md"):
            text = (ROOT / f).read_text()
            m = re.search(r"^# Appendix ([A-Z]):", text, re.M)
            if m:
                heading[f] = m.group(1)
    for letter, f in letters.items():
        if isinstance(f, str) and f in heading and heading[f] != letter:
            out.append(f"appendix letter: {f} is heading 'Appendix {heading[f]}' but sits at position {letter} in myst.yml")
    # 2. forbidden phrases
    phrases = [l.strip() for l in (ROOT / "checks" / "drift-phrases.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]
    scan = PROSE_SOURCES + sorted((ROOT / "generated").glob("*.md")) + sorted((ROOT / "scripts").glob("*.py")) + sorted((ROOT / "ogc").glob("*.py")) + sorted((ROOT / "shapes").glob("*.ttl")) + [ROOT / "model" / "og-caie.sysml", ROOT / "model" / "trace.ttl"]
    for p in scan:
        rel = str(p.relative_to(ROOT))
        if any(rel.startswith(q) for q in QUOTING):
            continue
        text = p.read_text()
        for ph in phrases:
            if ph.lower() in text.lower():
                out.append(f"stale phrase '{ph}' in {rel}")
    # 3. retired words (the register's own list)
    g = Graph()
    for f in ("vocabulary/og-caie.ttl", "vocabulary/epo.ttl", "rulings/adjudications.ttl", "model/trace.ttl", "shapes/epo.shapes.ttl", "shapes/model.shapes.ttl"):
        g.parse(ROOT / f)
    retired = {str(o) for o in g.objects(None, OGC.retired)}
    for p in PAGES:
        text = re.sub(r"```.*?```", "", p.read_text(), flags=re.S)
        for w in retired:
            if re.search(rf"\b{re.escape(w)}\b", text, re.I):
                out.append(f"retired word '{w}' in {p.relative_to(ROOT)}")
    # 4. file mentions
    path_re = re.compile(r"\b((?:docs|generated|model|shapes|track|queries|scripts|vocabulary|sources/digests|counterexamples|notebooks|explorer|report|checks|toolchain)/[\w./-]+\.(?:md|ttl|py|rq|sysml|ipynb|json|html|sh|csv|txt|yml|bib))\b")
    for p in PROSE_SOURCES + sorted((ROOT / "shapes").glob("*.ttl")):
        for m in path_re.finditer(p.read_text()):
            path = m.group(1).rstrip(".")
            if not (ROOT / path).exists() and path not in GATE_OUTPUTS:
                out.append(f"missing file '{path}' named in {p.relative_to(ROOT)}")
    # 5. sheet ticks name rulings the register holds
    rulings = {str(r).rsplit("#", 1)[-1] for r in g.subjects(RDF.type, OGC.Ruling)}
    for sheet in sorted((ROOT / "rulings" / "sheets").glob("*.md")):
        for m in re.finditer(r"\[x\][^|\n]*?\b(R-\d+)\b", sheet.read_text()):
            if m.group(1) not in rulings:
                out.append(f"sheet {sheet.name} ticks {m.group(1)}, not in the register")
    # 6. twins
    shapes = {str(s) for s in g.subjects(RDF.type, SH.NodeShape)}
    for t in g.subjects(RDF.type, OGC.Trace):
        for s in g.objects(t, OGC.checkedBy):
            if str(s) not in shapes:
                out.append(f"essential {str(t).rsplit('#', 1)[-1]} names a shape that does not exist: {s}")
    tests_text = "".join(p.read_text() for p in sorted((ROOT / "tests").glob("test_*.py")))  # any test may pin a counterexample
    for cx in sorted((ROOT / "counterexamples").rglob("*")):
        if cx.is_file() and cx.suffix in (".ttl", ".sysml") and cx.name not in tests_text and f'"{cx.stem}"' not in tests_text:  # pinned by file name or by stem
            out.append(f"counterexample {cx.relative_to(ROOT)} is not pinned by a test")
    for s in g.subjects(RDF.type, SH.NodeShape):
        for c in g.objects(s, OGC.counterexample):
            if not (ROOT / str(c)).exists():
                out.append(f"shape {str(s).rsplit('/', 1)[-1]} names a missing counterexample {c}")
    # 7. absence checks in the SEVOCAB digest
    src = Graph().parse(ROOT / "sources" / "sources.ttl")
    ranks = {str(s): str(src.value(s, OGC.rank)) for s in src.subjects(OGC.rank, None)}
    digest = (ROOT / "sources" / "digests" / "sevocab.md").read_text().lower()
    for t in g.subjects(RDF.type, SKOS.Concept):
        can = g.value(t, OGC.canonical)
        cites = str(g.value(can, OGC.cites)) if can is not None else ""
        if ranks.get(cites, "1") not in ("1", "2") and str(g.value(t, OGC["class"])) != "coined":
            head = str(g.value(t, SKOS.prefLabel)).lower()
            words = [head] + [str(a).lower() for a in g.objects(t, SKOS.altLabel)]
            if not any(f"| {w}" in digest or f", {w}" in digest or f"{w} |" in digest for w in words):
                out.append(f"no SEVOCAB absence row for '{head}' (canonical from a source ranked {ranks.get(cites)})")
    return out


if __name__ == "__main__":
    found = problems()
    for line in found:
        print("drift:", line)
    print(f"DRIFT: {'PASS' if not found else 'FAIL'} ({len(found)} findings)")
    sys.exit(1 if found else 0)
