"""The record is consistent with PROV-O and EARL (round four, KG H1): under
the OWL RL closure of the EPO, the register, the model predicates, PROV-O
and EARL (the vendored copies under sources/archive/), no member of the
measles evaluation, and none of the executed record, is an instance of two
disjoint classes. PROV-O declares prov:Activity disjoint with prov:Entity;
the assertions of the record (determinations, attestations, the verdict,
the approvals, the assessments, the consistency checks) are entities, dated
by prov:generatedAtTime, attributed by prov:wasAttributedTo and
earl:assertedBy, and derived from what they rule on by
prov:wasDerivedFrom; prov:used is reserved for the activities (sessions,
turns, the probe derivation, the coverage computations)."""
from owlrl import DeductiveClosure, OWLRL_Semantics
from rdflib import OWL, RDF, Graph, Literal

from conftest import EPO, ROOT, load
from ogc import executor

VOCABULARIES = ["vocabulary/epo.ttl", "vocabulary/register.ttl", "vocabulary/ogm.ttl",
                "sources/archive/prov-o-20130430.ttl", "sources/archive/earl10-schema-20170202.rdf"]
ASSERTIONS = ["Determination", "Attestation", "ConformanceVerdict", "ReportApproval", "AppropriatenessAssessment", "PlanApproval", "ConsistencyCheck"]


def closure(*data: Graph) -> Graph:
    g = load(*VOCABULARIES)
    for d in data:
        for t in d:
            g.add(t)
    DeductiveClosure(OWLRL_Semantics).expand(g)
    return g


def instances_of_two_disjoint_classes(g: Graph) -> list:
    bad = []
    for a, b in g.subject_objects(OWL.disjointWith):
        for x in set(g.subjects(RDF.type, a)) & set(g.subjects(RDF.type, b)):
            if not isinstance(x, Literal):  # the datatype axioms type literals; the record's nodes are what is checked
                bad.append((str(x), str(a), str(b)))
    bad += [(str(x), "owl:Nothing", "") for x in g.subjects(RDF.type, OWL.Nothing)]
    return sorted(set(bad))


def test_prov_o_states_the_disjointness_the_test_relies_on():
    g = load("sources/archive/prov-o-20130430.ttl")
    PROV = "http://www.w3.org/ns/prov#"
    from rdflib import URIRef
    assert (URIRef(PROV + "Activity"), OWL.disjointWith, URIRef(PROV + "Entity")) in g


def test_the_measles_record_is_consistent_with_prov_o_and_earl():
    g = closure(load("track/measles-evaluation.ttl"))
    assert instances_of_two_disjoint_classes(g) == []


def test_the_executed_record_is_consistent_with_prov_o_and_earl():
    g = closure(executor.execute(load("model/og-caie.model.ttl")))
    assert instances_of_two_disjoint_classes(g) == []


def test_the_assertion_classes_are_entities_not_activities():
    from rdflib import RDFS, URIRef
    g = load("vocabulary/epo.ttl")
    PROV = "http://www.w3.org/ns/prov#"
    for name in ASSERTIONS:
        supers = set(g.objects(EPO[name], RDFS.subClassOf))
        assert URIRef("http://www.w3.org/ns/earl#Assertion") in supers and URIRef(PROV + "Entity") in supers and URIRef(PROV + "Activity") not in supers, name
    for c in g.subjects(RDF.type, OWL.Class):
        supers = set(g.objects(c, RDFS.subClassOf))
        assert not ({URIRef(PROV + "Entity"), URIRef(PROV + "Activity")} <= supers), c
