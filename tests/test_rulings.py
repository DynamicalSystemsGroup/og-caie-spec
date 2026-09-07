"""The judgment record is well-formed: every ruling attributed, dated,
resolving a recorded concern, and carrying two texts (R-47): the decision in
the register's own words (ogc:rulingText, a formal register, no chat) and
the message as sent, untouched (ogc:verbatim; R-01 to R-46 held against the
texts committed before the rework). Counts pinned so a silent addition or
deletion fails."""
import json
import re

from pyshacl import validate
from rdflib import RDF

from conftest import OGC, ROOT, load

CONCERNS = 54
RULINGS = 48
# What a message to an assistant leaves behind and a decision must not: an addressee,
# hedging, the tooling, the tick. Matched case-insensitively as substrings.
CHAT_MARKERS = ("you ", "i think", "plan mode", "tick all", "go ahead", "assistant", "claude")
# The texts as committed before R-47 (git show 7cd0595:rulings/adjudications.ttl,
# ogc:rulingText of R-01 to R-46), now the ogc:verbatim of each.
VERBATIM_SNAPSHOT = ROOT / "tests" / "fixtures" / "rulings-verbatim.json"


def rulings_in_order(g):
    return sorted(g.subjects(RDF.type, OGC.Ruling), key=lambda r: int(g.value(r, OGC.order)))


def test_rulings_conform_to_shapes(rulings):
    shapes = load("shapes/rulings.shapes.ttl")
    ok, _, report = validate(rulings, shacl_graph=shapes, advanced=True)
    assert ok, report


def test_counts_pinned(rulings):
    assert len(set(rulings.subjects(RDF.type, OGC.Concern))) == CONCERNS
    assert len(set(rulings.subjects(RDF.type, OGC.Ruling))) == RULINGS


def test_every_concern_is_ruled_or_open(rulings):
    for c in rulings.subjects(RDF.type, OGC.Concern):
        status = str(rulings.value(c, OGC.status))
        resolved = any(True for _ in rulings.subjects(OGC.resolves, c))
        assert (status == "open") != resolved, f"{c}: status {status}, resolved {resolved}"


def test_ruling_order_is_a_permutation(rulings):
    orders = sorted(int(rulings.value(r, OGC.order)) for r in rulings.subjects(RDF.type, OGC.Ruling))
    assert orders == list(range(1, RULINGS + 1))


def test_every_ruling_carries_both_texts_once(rulings):
    """R-47: exactly one decision in the register's words and exactly one
    message as sent, both non-empty, and the two are never the same string
    (a decision is written, never copied)."""
    for r in rulings_in_order(rulings):
        texts = [str(t) for t in rulings.objects(r, OGC.rulingText)]
        sent = [str(t) for t in rulings.objects(r, OGC.verbatim)]
        assert len(texts) == 1 and texts[0].strip(), r
        assert len(sent) == 1 and sent[0].strip(), r
        assert texts[0] != sent[0], r


def test_formal_text_has_no_chat_markers(rulings):
    """The decision reads as a standards editor's: no addressee, no hedging,
    no tooling, no first person singular, no em-dashes."""
    for r in rulings_in_order(rulings):
        text = str(rulings.value(r, OGC.rulingText))
        low = text.lower()
        hits = [m for m in CHAT_MARKERS if m in low]
        assert not hits, (r, hits)
        assert not re.search(r"\bi\b", text), (r, "first person singular")
        assert "—" not in text, r
        assert 1 <= len(text.split()) <= 700, (r, len(text.split()))


def test_verbatim_of_the_first_forty_six_is_the_text_committed_before_the_rework(rulings):
    """Nothing is lost: the ogc:verbatim of R-01 to R-46 equals, byte for byte,
    the ogc:rulingText each carried before R-47."""
    snapshot = json.loads(VERBATIM_SNAPSHOT.read_text())
    assert sorted(snapshot, key=lambda k: int(k[2:])) == [f"R-{i:02d}" for i in range(1, 47)]
    for rid, before in snapshot.items():
        r = next(r for r in rulings.subjects(RDF.type, OGC.Ruling) if str(r).endswith("#" + rid))
        assert str(rulings.value(r, OGC.verbatim)) == before, rid
