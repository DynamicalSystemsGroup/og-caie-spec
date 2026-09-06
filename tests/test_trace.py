"""The crosswalk is complete and closed: twelve SCI traces, each with a
statement, a tag, and shapes, terms and sources that exist; every shape of
both families (M over the model graph, S over the record) is reached by
some SCI, so no check is orphaned and no essential is unchecked."""
from rdflib import RDF, RDFS, Namespace

from conftest import OGC, load

SH = Namespace("http://www.w3.org/ns/shacl#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
N = 12


def union():
    return load("model/trace.ttl", "shapes/epo.shapes.ttl", "shapes/model.shapes.ttl",
                "vocabulary/og-caie.ttl", "sources/sources.ttl", "rulings/adjudications.ttl")


def test_twelve_traces_resolve():
    g = union()
    traces = sorted(g.subjects(RDF.type, OGC.Trace), key=str)
    assert [str(t).rsplit("#", 1)[-1] for t in traces] == [f"SCI-{i:02d}" for i in range(1, N + 1)]
    shapes = set(g.subjects(RDF.type, SH.NodeShape))
    terms = set(g.subjects(RDF.type, SKOS.Concept))
    sources = set(g.subjects(RDF.type, OGC.Source)) | set(g.subjects(RDF.type, OGC.Ruling))
    for t in traces:
        assert set(g.objects(t, OGC.checkedBy)) <= shapes, (t, set(g.objects(t, OGC.checkedBy)) - shapes)
        assert set(g.objects(t, OGC.usesTerm)) <= terms, (t, set(g.objects(t, OGC.usesTerm)) - terms)
        assert set(g.objects(t, OGC.restsOn)) <= sources, (t, set(g.objects(t, OGC.restsOn)) - sources)
        assert g.value(t, OGC.tag) is not None and g.value(t, RDFS.comment) is not None
        assert str(g.value(t, OGC.tag)).startswith(("machine", "human"))


def test_every_shape_of_both_families_is_reached():
    g = union()
    reached = set(g.objects(None, OGC.checkedBy))
    assert reached == set(g.subjects(RDF.type, SH.NodeShape)), set(g.subjects(RDF.type, SH.NodeShape)) - reached
