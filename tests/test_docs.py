"""Prose discipline: retired words never appear, no em-dashes in prose,
every glossary term is actually used somewhere in the docs or the model
(so the glossary carries no dead weight), and the pages stay under budget."""
import re

from rdflib import RDF

from conftest import ROOT, load
from rdflib import Namespace

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
PROSE = [ROOT / "index.md", *sorted((ROOT / "docs").glob("*.md")), ROOT / "README.md"]
WORD_BUDGET = 6200  # the main path only; the appendices are backup and are not counted.
# Raised from 5500 on R-47 (sheet 06): terms defined at first use in each chapter (06-05), the
# outline headings and the lead-ins to the command blocks (06-03) paid for by trims, not by cuts to the graph.
RETIRED = {"adequacy", "adequate", "inadequate"}


def prose_text():
    return "\n".join(p.read_text() for p in PROSE)


def test_no_retired_words_in_prose_or_model():
    text = prose_text() + (ROOT / "model" / "og-caie.sysml").read_text()
    # Deliberate mentions are allowed: text inside double quotes (a source
    # quoted verbatim) and the phrase that explains the retirement itself.
    text = re.sub(r'"[^"\n]*"', "", text)
    text = text.replace("the word adequacy", "").replace("the earlier label adequacy", "")
    for w in RETIRED:
        hits = [m.start() for m in re.finditer(rf"\b{w}\b", text, re.I)]
        assert not hits, f"retired word {w!r} in prose/model at offsets {hits[:3]}"


def test_no_em_dashes_in_prose():
    for p in PROSE:
        assert "—" not in p.read_text(), f"em-dash in {p.name}"


def test_every_glossary_term_is_used():
    g = load("vocabulary/og-caie.ttl")
    haystack = (prose_text() + (ROOT / "model" / "og-caie.sysml").read_text()
                + (ROOT / "track" / "measles-run.ttl").read_text() + (ROOT / "shapes" / "epo.shapes.ttl").read_text()).lower()
    unused = []
    for t in g.subjects(RDF.type, SKOS.Concept):
        labels = [str(l).lower() for l in g.objects(t, SKOS.prefLabel)] + [str(l).lower() for l in g.objects(t, SKOS.altLabel)]
        stems = labels + [l.rstrip("s") for l in labels] + [l.replace("-", " ") for l in labels]
        if not any(s in haystack for s in stems):
            unused.append(str(g.value(t, SKOS.prefLabel)))
    assert not unused, unused


POPPER_MARKERS = ("popper", "popperian", "falsifiable", "falsifiability", "falsified", "falsifier", "falsifiers")
POPPER_PAGES = {"index.md", "conclusion.md", "popper.md", "popper-back.md", "rulings.md", "sources.md",
                "cited-index.md", "cited-conclusion.md", "cited-all.md"}  # rulings quote Z verbatim; the register names Popper 1959; the bookends' works cited and the aggregate (R-48) list it


def test_popper_argument_only_in_the_bookends():
    """Rulings R-29 and R-30: the argument grounded in Popper (why and what)
    lives on the front page and the conclusion; the inner chapters achieve it
    through the engineering standards (what and how). The restriction is on
    using the words in Popper's sense, not on ordinary English, so the test
    checks only the name and the terms of art that have no everyday use;
    hypothesis, prediction, evidence and assumption stay free words, and the
    sense rule is read, not grepped."""
    pages = [ROOT / "index.md", *sorted((ROOT / "docs").glob("*.md")), *sorted((ROOT / "generated").glob("*.md"))]
    for p in pages:
        if p.name in POPPER_PAGES:
            continue
        text = re.sub(r'"[^"\n]*"', "", p.read_text()).lower()
        hits = [w for w in POPPER_MARKERS if re.search(rf"\b{w}\b", text)]
        assert not hits, f"{p.name}: {hits}"


def test_term_roles_resolve_and_key_terms_match():
    """Every {term} role resolves to exactly one concept; the key-terms
    fragment lists exactly the referenced concepts, so a hover never fails
    and the glossary page carries no dead entry."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from render import referenced_terms
    g = load("vocabulary/og-caie.ttl")
    found, unresolved = referenced_terms(g)
    assert not unresolved, unresolved
    rendered = re.findall(r"^([^:\n`][^\n]*)\n: ", (ROOT / "generated" / "key-terms.md").read_text(), re.M)
    expected = sorted(str(g.value(t, SKOS.prefLabel)) for t in found)
    assert sorted(rendered) == expected, (sorted(set(rendered) ^ set(expected)))
    assert len(found) >= 15


def test_word_budget():
    """The budget guards the main path, calibrated for a human reader (R-34);
    the appendices are backup a reader may skip and are not counted."""
    main_path = [p for p in PROSE if p.name != "README.md" and p.name != "rulings.md" and not p.name.startswith("appendix-")]
    words = sum(len(p.read_text().split()) for p in main_path)
    assert words < WORD_BUDGET, words


PATTERN = ["What the standards say", "The specification", "The walkthrough", "Checked", "There is more in the model"]
BOXES = ["Verdict", "Ask the graph"]
CHAPTERS = ["contracting.md", "evaluation.md", "model.md", "guarantees.md"]
INCLUDE = re.compile(r"```\{(?:literal)?include\}[^\n]*\n(?::[^\n]*\n)*```")
CLI_INCLUDE = re.compile(r"```\{literalinclude\} \.\./generated/cli/[\w-]+\.md\n```")


def test_chapter_pages_follow_the_pattern():
    """R-34 as revised by R-47 (sheet 06, item 06-03): every chapter keeps
    the five parts in order as level-2 headings, so the contents panel shows
    the outline, with prose between them; admonitions are reserved for the
    two places that earn a box, the Verdict under Checked and Ask the graph
    under There is more in the model; and at least one block shows an `ogc`
    command and what it prints, rendered into generated/cli/ (06-15: what a
    page says a command prints is what it prints)."""
    for name in CHAPTERS:
        text = (ROOT / "docs" / name).read_text()
        positions = [text.find(f"\n## {title}\n") for title in PATTERN]
        assert all(p >= 0 for p in positions), (name, dict(zip(PATTERN, positions)))
        assert positions == sorted(positions), name
        boxes = re.findall(r"^:::\{admonition\} (.*)$", text, re.M)
        assert boxes == BOXES, (name, boxes)
        assert text.find(":::{admonition} Verdict") > positions[3], name
        assert text.find(":::{admonition} Ask the graph") > positions[4], name
        assert CLI_INCLUDE.search(text), (name, "no generated/cli/ block")
        prose = INCLUDE.sub("", text)
        words = len(prose.split())
        assert 400 <= words <= 1400, (name, words)


def test_every_essential_has_a_page_and_each_chapter_shows_its_own():
    g = load("model/trace.ttl")
    from conftest import OGC as O
    pages = {str(t).rsplit("#", 1)[-1]: str(g.value(t, O.page)) for t in g.subjects(RDF.type, O.Trace)}
    assert set(pages.values()) <= {"contracting", "evaluation", "guarantees"}, pages
    for chapter in ("contracting", "evaluation", "guarantees"):
        frag = (ROOT / "generated" / f"sci-{chapter}.md").read_text()
        for sid, pg in pages.items():
            assert (sid in frag) == (pg == chapter), (chapter, sid)
