"""Prose discipline: retired words never appear, no em-dashes in prose,
every glossary term is actually used somewhere in the docs or the model
(so the glossary carries no dead weight), and the pages stay under budget."""
import re

from rdflib import RDF

from conftest import ROOT, load
from rdflib import Namespace

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
PROSE = [ROOT / "index.md", *sorted((ROOT / "docs").glob("*.md")), ROOT / "README.md"]
WORD_BUDGET = 4000
RETIRED = {"adequacy", "adequate", "inadequate", "conformance"}


def prose_text():
    return "\n".join(p.read_text() for p in PROSE)


def test_no_retired_words_in_prose_or_model():
    text = prose_text() + (ROOT / "model" / "og-caie.sysml").read_text()
    # the model's doc comments explain the R-08 replacement; those two mentions are allowed
    text = text.replace('replaces the earlier label "adequacy"', "").replace("conformance is synonymous but deprecated", "")
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


def test_word_budget():
    words = sum(len(p.read_text().split()) for p in PROSE if p.name != "README.md")
    assert words < WORD_BUDGET, words
