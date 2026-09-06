"""The measles record conforms to the EPO shapes; each RDF counterexample
fails on exactly the shape it is built to violate; the EPO handle classes
add no semantics beyond PROV-O and EARL subclassing."""
from pyshacl import validate
from rdflib import RDF, RDFS, Namespace

from conftest import EPO, OGC, ROOT, load

SH = Namespace("http://www.w3.org/ns/shacl#")
PROV = Namespace("http://www.w3.org/ns/prov#")
EARL = Namespace("http://www.w3.org/ns/earl#")

COUNTEREXAMPLES = {
    "counterexamples/attestation-without-evidence.ttl": "S6-Attestation",
    "counterexamples/probe-before-requirements.ttl": "S2-RequirementSet",
    "counterexamples/recommendation-untraced.ttl": "S8-Recommendation",
    "counterexamples/attestation-off-plan.ttl": "S6-Attestation",
}


def shapes():
    return load("shapes/epo.shapes.ttl")


def data(*paths):
    return load("vocabulary/epo.ttl", *paths)


def violated_shapes(results_graph):
    return {str(s).rsplit("/", 1)[-1] for s in results_graph.objects(None, SH.sourceShape)}


def test_record_conforms():
    ok, _, report = validate(data("track/measles-run.ttl"), shacl_graph=shapes(), advanced=True)
    assert ok, report


def test_each_counterexample_fails_on_its_shape_only():
    for path, shape in COUNTEREXAMPLES.items():
        ok, results, report = validate(data(path), shacl_graph=shapes(), advanced=True)
        assert not ok, f"{path} conformed; it must not"
        assert violated_shapes(results) == {shape}, f"{path}: {violated_shapes(results)}"


def test_eight_shapes_one_per_sci_group():
    g = shapes()
    names = sorted(str(s).rsplit("/", 1)[-1] for s in g.subjects(RDF.type, SH.NodeShape))
    assert names == ["S1-DsoRelease", "S2-AcceptanceCriterion", "S2-RequirementSet", "S3-Probe", "S3-TestPlan",
                     "S4-ProbeRun", "S5-Evidence", "S6-Attestation", "S7-Report", "S8-Recommendation"]


def test_epo_handles_subclass_prov_or_earl():
    g = load("vocabulary/epo.ttl")
    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    for c in g.subjects(RDF.type, OWL.Class):
        if c in (EPO.EpoStep, EPO.AppropriatenessValue, EPO.SufficiencyValue):
            continue
        supers = set(g.objects(c, RDFS.subClassOf))
        assert supers & {PROV.Entity, PROV.Activity, EARL.Assertion}, c


def test_record_names_every_human_judgment():
    g = data("track/measles-run.ttl")
    for att in g.subjects(RDF.type, EPO.Attestation):
        who = g.value(att, EARL.assertedBy)
        assert (who, RDF.type, PROV.Person) in g
        assert g.value(att, EPO.appropriateness) is not None and g.value(att, EPO.sufficiency) is not None
    assert len(list(g.subjects(RDF.type, EPO.Attestation))) == 2
    assert len(list(g.subjects(RDF.type, EPO.AcceptanceCriterion))) == 3
