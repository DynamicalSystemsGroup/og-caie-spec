"""The measles evaluation conforms to the EPO shapes; each RDF counterexample
fails on exactly the shapes it is built to violate; two records loaded into
one graph both conform (sheet 10-31); the record's digests are current
(sheet 10-18); the EPO handle classes add no semantics beyond PROV-O and
EARL subclassing.

The data graph is always the EPO vocabulary, the model graph and the record
together (the shapes' two preconditions, sheets 10-31 and 10-33): the step is
derived through the model graph."""
import hashlib
import sys

from pyshacl import validate
from rdflib import RDF, RDFS, Graph, Namespace

from conftest import EPO, OGC, ROOT, load

sys.path.insert(0, str(ROOT / "scripts"))
from render_counterexamples import COUNTEREXAMPLES, render_all  # noqa: E402

SH = Namespace("http://www.w3.org/ns/shacl#")
PROV = Namespace("http://www.w3.org/ns/prov#")
EARL = Namespace("http://www.w3.org/ns/earl#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
RECORD = "track/measles-evaluation.ttl"
EV = "https://w3id.org/og-caie/evaluation/measles#"
NEW_SHAPES = ["S0-Independence", "S0-Member", "S0-Record", "S0-Roles", "S3-PlanDeviation"]  # sheet 10: 10-15, 10-31, 10-13, 10-16


def shapes():
    return load("shapes/epo.shapes.ttl")


def data(*paths):
    return load("vocabulary/epo.ttl", "model/og-caie.model.ttl", *paths)


def violated_shapes(results_graph, shapes_graph):
    """The node shapes that fired, a property shape named by the node shape that owns it."""
    out = set()
    for s in results_graph.objects(None, SH.sourceShape):
        if not str(s).startswith(str(OGC)):
            s = next((ns for ns in shapes_graph.subjects(SH.property, s)), s)
        out.add(str(s).rsplit("/", 1)[-1])
    return out


def test_record_conforms():
    ok, _, report = validate(data(RECORD), shacl_graph=shapes(), advanced=True)
    assert ok, report


def test_each_counterexample_fails_on_its_shapes_only():
    sg = shapes()
    for name, spec in COUNTEREXAMPLES.items():
        ok, results, report = validate(data(f"counterexamples/{name}.ttl"), shacl_graph=sg, advanced=True)
        assert not ok, f"{name} conformed; it must not"
        assert violated_shapes(results, sg) == set(spec["shapes"]), f"{name}: {sorted(violated_shapes(results, sg))}"


def test_counterexamples_are_the_record_with_one_change():
    """Every file under counterexamples/ is what scripts/render_counterexamples.py writes from the current record (sheet 10-19)."""
    rendered = render_all()
    files = sorted(p.stem for p in (ROOT / "counterexamples").glob("*.ttl"))
    assert files == sorted(rendered), "counterexamples/ and the generator's table differ"
    for name, text in rendered.items():
        assert (ROOT / "counterexamples" / f"{name}.ttl").read_text() == text, f"{name} is stale: run scripts/render_counterexamples.py"
        assert text.splitlines()[0].startswith("# Counterexample for " + spec_shape(name))


def spec_shape(name):
    return COUNTEREXAMPLES[name]["shapes"][0]


def test_every_new_shape_has_a_counterexample():
    covered = {s for spec in COUNTEREXAMPLES.values() for s in spec["shapes"]}
    assert set(NEW_SHAPES) <= covered, sorted(set(NEW_SHAPES) - covered)


def test_two_records_in_one_graph_both_conform():
    """Sheet 10-31: every global constraint is anchored on the record reachable
    from its focus node, so the measles evaluation loaded twice under two
    namespaces into one default graph conforms, and each record's coverage
    comes out once."""
    text = (ROOT / RECORD).read_text()
    other = text.replace(EV, "https://w3id.org/og-caie/evaluation/measles-second#")
    g = data(RECORD)
    g.parse(data=other, format="turtle")
    assert len(list(g.subjects(RDF.type, PROV.Bundle))) == 2
    ok, _, report = validate(g, shacl_graph=shapes(), advanced=True)
    assert ok, report
    rows = list(g.query((ROOT / "queries" / "coverage.rq").read_text()))
    assert len(rows) == 2 and {float(r.coverage) for r in rows} == {0.75}


def test_record_digests_are_current():
    """Sheet 10-18: the verdict and the coverage computation name the shapes, the ontology and the query by sha256; the values equal the files'."""
    g = data(RECORD)
    expected = {k: hashlib.sha256((ROOT / f).read_bytes()).hexdigest()
                for k, f in (("shapesDigest", "shapes/epo.shapes.ttl"), ("ontologyDigest", "vocabulary/epo.ttl"), ("queryDigest", "queries/coverage.rq"))}
    holders = list(g.subjects(RDF.type, EPO.ConformanceVerdict)) + list(g.subjects(RDF.type, EPO.CoverageComputation))
    assert len(holders) == 2
    for h in holders:
        for k, v in expected.items():
            assert str(g.value(h, EPO[k])) == v, f"{h} {k} is stale: run scripts/stamp_digests.py"


def test_shapes_s0_to_s9():
    g = shapes()
    names = sorted(str(s).rsplit("/", 1)[-1] for s in g.subjects(RDF.type, SH.NodeShape))
    assert names == ["S0-Access", "S0-Independence", "S0-Layers", "S0-Member", "S0-Mission", "S0-Need", "S0-Parties", "S0-Population", "S0-Proposal", "S0-Record", "S0-Roles", "S0-StatementOfWork",
                     "S1-DsoRelease", "S2-AcceptanceCriterion", "S2-Requirement", "S2-RequirementSet",
                     "S3-PlanApproval", "S3-PlanDeviation", "S3-Probe", "S3-Strategy", "S3-TestPlan",
                     "S4-Session", "S4-TestSuite", "S4-Turn", "S5-Evidence", "S5-Response", "S6-Attestation", "S6-Determination",
                     "S7-ConformanceVerdict", "S7-Report", "S7-ReportApproval", "S8-Delivery", "S8-Recommendation", "S9-Acceptance"]


def test_no_record_asserts_a_step():
    """Sheet 10-33: the step is derived through the model graph; no record file and no counterexample carries epo:step."""
    for f in [ROOT / RECORD, *sorted((ROOT / "counterexamples").glob("*.ttl"))]:
        g = Graph().parse(f)
        assert not list(g.subject_objects(EPO.step)), f.name


def test_epo_handles_subclass_prov_or_earl():
    g = load("vocabulary/epo.ttl")
    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    roles = {c for c in g.subjects(RDF.type, OWL.Class) if EPO.Role in g.transitive_objects(c, RDFS.subClassOf)}  # the role classes sit under prov:Role (sheet 08)
    for c in g.subjects(RDF.type, OWL.Class):
        if c in (EPO.Step, EPO.EpoStep, EPO.ContractingStep, EPO.Layer, EPO.AppropriatenessValue, EPO.SufficiencyValue, EPO.Engagement, EPO.Affectedness, EPO.IndependenceLevel) or c in roles:
            continue
        if c == EPO.Strategy:  # a prov:Plan, itself a prov:Entity
            continue
        supers = set(g.objects(c, RDFS.subClassOf))
        assert supers & {PROV.Entity, PROV.Activity, PROV.Agent, EARL.Assertion}, c


def test_record_names_every_human_judgment():
    g = data(RECORD)
    for att in g.subjects(RDF.type, EPO.Attestation):
        who = g.value(att, EARL.assertedBy)
        assert (who, RDF.type, PROV.Person) in g
        assert g.value(att, EPO.appropriateness) is not None and g.value(att, EPO.sufficiency) is not None
        assert (who, EPO.role, EPO.domainExpertRole) in g
    assert len(list(g.subjects(RDF.type, EPO.Attestation))) == 2
    assert len(list(g.subjects(RDF.type, EPO.AcceptanceCriterion))) == 3
    assert len(list(g.subjects(RDF.type, EPO.Determination))) == 3  # sheet 10-15: Theo's determination on a2 is paired with Annie's


def test_record_names_the_parties_and_roles():
    g = data(RECORD)
    roles = {str(r).rsplit("#", 1)[-1] for r in g.objects(None, EPO.role)}
    assert roles == {"sponsorRole", "testingOrganizationRole", "accountableOrganizationRole",
                     "authorizedRepresentativeRole", "domainExpertRole", "evaluationOperatorRole",
                     "testItemCustomerRole", "sponsorSignatoryRole"}  # sheet 08: the sponsor is also the customer of the chatbot it deploys; sheet 10-06: the sponsor's signatory
    persons = [a for a in g.subjects(RDF.type, PROV.Person)]
    assert len(persons) == 4
    for person in persons:
        assert g.value(person, SKOS.note) is not None, "synthetic-case note (R-23)"
    populations = list(g.subjects(RDF.type, EPO.Population))
    assert len(populations) == 2
    # sheet 10-07, 10-09: the party facts are declarations and a provider fact, not booleans
    assert len(list(g.subjects(RDF.type, EPO.IndependenceDeclaration))) == 1 and len(list(g.subjects(RDF.type, EPO.UserInterestDeclaration))) == 1
    assert {str(o) for o in g.objects(None, EPO.providesTestItem)} == {"true", "false"}
    assert not list(g.subject_objects(EPO.isAccountable)) and not list(g.subject_objects(EPO.independentOfAccountable))


def test_record_is_a_bundle_every_member_tagged_synthetic():
    """Sheets 10-31 and 10-43: one bundle; every named subject a member of it; every member and the bundle tagged synthetic."""
    g = Graph().parse(ROOT / RECORD)
    from rdflib import URIRef, Literal
    bundles = list(g.subjects(RDF.type, PROV.Bundle))
    assert len(bundles) == 1
    subjects = {s for s in g.subjects() if isinstance(s, URIRef) and str(s).startswith(EV)} - set(bundles)
    for s in subjects:
        assert (s, OGC.inRecord, bundles[0]) in g, s
        assert (s, OGC.synthetic, Literal(True)) in g, s
    assert (bundles[0], OGC.synthetic, Literal(True)) in g
