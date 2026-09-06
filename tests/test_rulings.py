"""The judgment record is well-formed: every ruling attributed, dated,
verbatim, and resolving a recorded concern; counts pinned so a silent
addition or deletion fails."""
from pyshacl import validate
from rdflib import RDF

from conftest import OGC, load

CONCERNS = 46
RULINGS = 40


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
