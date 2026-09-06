"""The Popper crosswalk (ruling R-29) is closed: every row cites the BoF deck
with a quote located in its digest, maps to glossary terms that exist, and
is realized by EPO classes or shapes that exist; the rows are ordered."""
from rdflib import RDF, Namespace

from conftest import OGC, ROOT, load, normalized

SH = Namespace("http://www.w3.org/ns/shacl#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
ROWS = 6


def union():
    return load("vocabulary/crosswalk.ttl", "vocabulary/og-caie.ttl", "vocabulary/epo.ttl",
                "shapes/epo.shapes.ttl", "shapes/model.shapes.ttl", "sources/sources.ttl")


def test_rows_closed():
    g = union()
    rows = sorted(g.subjects(RDF.type, OGC.Crosswalk), key=lambda r: int(g.value(r, OGC.order)))
    assert len(rows) == ROWS
    assert [int(g.value(r, OGC.order)) for r in rows] == list(range(1, ROWS + 1))
    terms = set(g.subjects(RDF.type, SKOS.Concept))
    realizers = set(g.subjects(RDF.type, OWL.Class)) | set(g.subjects(RDF.type, SH.NodeShape))
    digest = normalized((ROOT / "sources" / "digests" / "bof-deck-2026-07.md").read_text())
    for r in rows:
        assert set(g.objects(r, OGC.mapsTo)) <= terms, (r, set(g.objects(r, OGC.mapsTo)) - terms)
        assert set(g.objects(r, OGC.realizedBy)) <= realizers, (r, set(g.objects(r, OGC.realizedBy)) - realizers)
        assert (g.value(r, OGC.cites), RDF.type, OGC.Source) in g
        assert normalized(str(g.value(r, OGC.quote))) in digest, r
        for p in (OGC.where, OGC.checkable, OGC.locator):
            assert g.value(r, p) is not None, (r, p)
