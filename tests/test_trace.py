"""The crosswalk is complete and closed: nine SCI traces, each naming shapes,
terms and sources that exist; every EPO shape is reached by some SCI; the
machine/human tag in the trace agrees with the doc comment in the model."""
import re

from rdflib import RDF, Namespace

from conftest import OGC, ROOT, load

SH = Namespace("http://www.w3.org/ns/shacl#")
TR = Namespace("https://w3id.org/og-caie/trace#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")


def union():
    return load("model/trace.ttl", "shapes/epo.shapes.ttl", "vocabulary/og-caie.ttl", "sources/sources.ttl", "rulings/adjudications.ttl")


def test_nine_traces_resolve():
    g = union()
    traces = sorted(g.subjects(RDF.type, OGC.Trace), key=str)
    assert [str(t).rsplit("#", 1)[-1] for t in traces] == [f"SCI-0{i}" for i in range(1, 10)]
    shapes = set(g.subjects(RDF.type, SH.NodeShape))
    terms = set(g.subjects(RDF.type, SKOS.Concept))
    sources = set(g.subjects(RDF.type, OGC.Source)) | set(g.subjects(RDF.type, OGC.Ruling))
    for t in traces:
        assert set(g.objects(t, OGC.checkedBy)) <= shapes, t
        assert set(g.objects(t, OGC.usesTerm)) <= terms, t
        assert set(g.objects(t, OGC.restsOn)) <= sources, t
        assert g.value(t, OGC.tag) is not None


def test_every_epo_shape_is_reached():
    g = union()
    reached = set(g.objects(None, OGC.checkedBy))
    assert reached == set(g.subjects(RDF.type, SH.NodeShape))


def test_tags_agree_with_the_model():
    g = union()
    model = (ROOT / "model" / "og-caie.sysml").read_text()
    docs = dict(re.findall(r"requirement def <'(SCI-\d\d)'> \w+ \{\s*doc /\*(.*?)\*/", model, re.S))
    for t in g.subjects(RDF.type, OGC.Trace):
        sid = str(t).rsplit("#", 1)[-1]
        tag = str(g.value(t, OGC.tag))
        assert ("human" in tag) == ("human" in docs[sid].split(".")[0]), sid
