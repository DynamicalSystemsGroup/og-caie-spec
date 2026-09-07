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
    "counterexamples/attestation-off-turn.ttl": "S6-Attestation",
    "counterexamples/requirements-before-agreement.ttl": {"S0-Parties", "S0-Layers"},
    "counterexamples/population-unrepresented.ttl": "S0-Population",
    "counterexamples/engagement-mismatch.ttl": "S0-Population",
    "counterexamples/expert-administers-tests.ttl": "S4-Session",
    "counterexamples/executive-attests.ttl": "S6-Attestation",
    "counterexamples/dso-before-stakeholder-input.ttl": "S1-DsoRelease",  # sheet 08: the population's input came after the DSO approval
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
        expected = shape if isinstance(shape, set) else {shape}
        assert violated_shapes(results) == expected, f"{path}: {violated_shapes(results)}"


def test_shapes_s0_to_s8():
    g = shapes()
    names = sorted(str(s).rsplit("/", 1)[-1] for s in g.subjects(RDF.type, SH.NodeShape))
    assert names == ["S0-Access", "S0-Layers", "S0-Mission", "S0-Need", "S0-Parties", "S0-Population", "S0-Proposal", "S0-StatementOfWork",
                     "S1-DsoRelease", "S2-AcceptanceCriterion", "S2-Requirement", "S2-RequirementSet",
                     "S3-PlanApproval", "S3-Probe", "S3-Strategy", "S3-TestPlan",
                     "S4-Session", "S4-TestSuite", "S4-Turn", "S5-Evidence", "S5-Response", "S6-Attestation", "S6-Determination",
                     "S7-Report", "S8-Delivery", "S8-Recommendation", "S9-Acceptance"]


def test_epo_handles_subclass_prov_or_earl():
    g = load("vocabulary/epo.ttl")
    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    roles = {c for c in g.subjects(RDF.type, OWL.Class) if EPO.Role in g.transitive_objects(c, RDFS.subClassOf)}  # the role classes sit under prov:Role (sheet 08)
    for c in g.subjects(RDF.type, OWL.Class):
        if c in (EPO.EpoStep, EPO.ContractingStep, EPO.Layer, EPO.AppropriatenessValue, EPO.SufficiencyValue, EPO.Engagement, EPO.Affectedness) or c in roles:
            continue
        if c == EPO.Strategy:  # a prov:Plan, itself a prov:Entity
            continue
        supers = set(g.objects(c, RDFS.subClassOf))
        assert supers & {PROV.Entity, PROV.Activity, PROV.Agent, EARL.Assertion}, c


def test_record_names_every_human_judgment():
    g = data("track/measles-run.ttl")
    for att in g.subjects(RDF.type, EPO.Attestation):
        who = g.value(att, EARL.assertedBy)
        assert (who, RDF.type, PROV.Person) in g
        assert g.value(att, EPO.appropriateness) is not None and g.value(att, EPO.sufficiency) is not None
        assert (who, EPO.role, EPO.domainExpertRole) in g
    assert len(list(g.subjects(RDF.type, EPO.Attestation))) == 2
    assert len(list(g.subjects(RDF.type, EPO.AcceptanceCriterion))) == 3


def test_record_names_the_parties_and_roles():
    g = data("track/measles-run.ttl")
    roles = {str(r).rsplit("#", 1)[-1] for r in g.objects(None, EPO.role)}
    assert roles == {"sponsorRole", "testingOrganizationRole", "accountableOrganizationRole",
                     "accountExecutiveRole", "domainExpertRole", "evaluationOperatorRole",
                     "testItemCustomerRole"}  # sheet 08: the sponsor is also the customer of the chatbot it deploys
    persons = [a for a in g.subjects(RDF.type, PROV.Person)]
    assert len(persons) == 3
    for person in persons:
        assert g.value(person, Namespace("http://www.w3.org/2004/02/skos/core#").note) is not None, "synthetic-case note (R-23)"
    populations = list(g.subjects(RDF.type, EPO.Population))
    assert len(populations) == 2
