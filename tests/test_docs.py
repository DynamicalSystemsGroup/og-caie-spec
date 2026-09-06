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


POPPER_WORDS = ("popper", "hypothesis", "hypotheses", "auxiliary", "prediction", "falsifiable", "falsifiability", "falsified", "falsifier")
POPPER_PAGES = {"index.md", "conclusion.md", "popper.md", "popper-back.md", "rulings.md", "sources.md"}  # rulings quote Z verbatim; the register names Popper 1959


def test_popper_words_only_in_setup_and_conclusion():
    """Ruling R-29: the Popperian vocabulary appears in the front page (the
    setup), the conclusion, and the two crosswalk fragments; every other page
    speaks the standards' terms."""
    pages = [ROOT / "index.md", *sorted((ROOT / "docs").glob("*.md")), *sorted((ROOT / "generated").glob("*.md"))]
    for p in pages:
        if p.name in POPPER_PAGES:
            continue
        text = re.sub(r'"[^"\n]*"', "", p.read_text()).lower()
        hits = [w for w in POPPER_WORDS if re.search(rf"\b{w}\b", text)]
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
    words = sum(len(p.read_text().split()) for p in PROSE if p.name != "README.md")
    assert words < WORD_BUDGET, words
