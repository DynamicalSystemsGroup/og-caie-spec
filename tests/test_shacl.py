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
NEW_SHAPES = ["S0-Independence", "S0-Member", "S0-Record", "S0-Roles", "S3-PlanDeviation", "S7-CoverageComputation"]  # sheet 10: 10-15, 10-31, 10-13, 10-16; round four, KG 8
# Drift pass 4: the rules the readers found missing, each pinned to the one shape its counterexample fails on alone
# (the contracting officer's findings 4 and 12, the QA reader's 9, 10 and 19).
DRIFT_PASS_4 = {
    "dso-approval-undated": "S1-DsoRelease",              # QA 9: the DSO approval is dated (epo:approvedAt)
    "assessment-after-session": "S2-RequirementSet",      # QA 9: the appropriateness assessment precedes the sessions
    "session-outside-access-period": "S4-Session",        # contracting officer 4: the access period binds the sessions
    "user-interest-denied": "S0-Parties",                 # contracting officer 12: the user-interest declaration agrees with the customer role
}


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


def test_drift_pass_4_counterexamples_fail_on_one_shape_each():
    for name, shape in DRIFT_PASS_4.items():
        assert COUNTEREXAMPLES[name]["shapes"] == [shape], name


def test_every_shape_names_its_counterexamples_and_only_those():
    """Sheet 10-40 and drift pass 4 (QA 20): each node shape carries ogc:counterexample for every file of the generator's table
    whose fault list names it, and for no other, so the counterexamples answer by query and scripts/drift_check.py finds every
    file the annotations name."""
    g = shapes()
    for s in g.subjects(RDF.type, SH.NodeShape):
        name = str(s).rsplit("/", 1)[-1]
        expected = {f"counterexamples/{n}.ttl" for n, spec in COUNTEREXAMPLES.items() if name in spec["shapes"]}
        assert {str(o) for o in g.objects(s, OGC.counterexample)} == expected, name


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
    assert len(rows) == 2 and {float(r.coverage) for r in rows} == {1.0}  # every criterion attested (sheet 10-48, R-51)
    # Round four, KG H3: a foreign attestation, in the second record, on the first record's criterion a1, failed and dated
    # before the first record's draft. Every join is anchored on the record, so the first record's reports still recompute to
    # their own numbers and nothing of the first record fires; what fires is the foreign attestation's own fault (the S6
    # chain rule: the determination it aggregates tests the second record's a1, not the first's).
    second = "https://w3id.org/og-caie/evaluation/measles-second#"
    g.parse(data=f"""
        @prefix ev: <{EV}> . @prefix ev2: <{second}> . @prefix epo: <https://w3id.org/og-caie/epo#> . @prefix ogc: <https://w3id.org/og-caie/> .
        @prefix prov: <http://www.w3.org/ns/prov#> . @prefix earl: <http://www.w3.org/ns/earl#> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ev2:attestation-foreign a epo:Attestation ; earl:test ev:a1 ; earl:subject ev2:chatbot-v1 ; earl:mode earl:manual ; earl:assertedBy ev2:annie ;
            prov:wasAttributedTo ev2:annie ; prov:wasDerivedFrom ev2:determination-1 ;
            earl:result [ a earl:TestResult ; earl:outcome earl:failed ] ; epo:appropriateness epo:appropriate ; epo:sufficiency epo:sufficient ;
            prov:generatedAtTime "2026-08-11T09:11:00Z"^^xsd:dateTime ; ogc:inRecord ev2:record ; ogc:synthetic true .
    """, format="turtle")
    ok, results, report = validate(g, shacl_graph=shapes(), advanced=True)
    assert not ok
    focus = {str(f) for f in results.objects(None, SH.focusNode)}
    assert focus == {second + "attestation-foreign"}, report
    rows = {str(r.record): r for r in g.query((ROOT / "queries" / "coverage.rq").read_text())}
    first = rows[EV + "record"]
    assert (float(first.coverage), float(first.passRate), float(first.failRate), float(first.cantTellRate)) == (1.0, 0.8, 0.2, 0.0)


def test_every_graph_in_one_default_graph_conforms():
    """Round four, KG H2: S0-Member targets the record's own members (the nodes typed by an epo: item class, and the agents
    that hold a role, carry a version or are attributed an item), so the explorer's merged file, every graph of the repository
    in one default graph (the vocabularies, the sources, the rulings, the essentials, the shapes, the model graph and the record),
    conforms to the EPO shapes: the sources, the rulings and their adjudicator are entities and agents of no record and are not
    drawn into the record's constraints."""
    ok, _, report = validate(load("explorer/data/all.ttl"), shacl_graph=shapes(), advanced=True)
    assert ok, report


def test_record_digests_are_current():
    """Sheet 10-18: the verdict names the shapes and the ontology by sha256 and the record it judged by the digest of its canonical
    member triples as they stood at the verdict (round four, KG 8); the two coverage computations name the shapes, the ontology and
    the query; every value equals what is recomputed from the checkout."""
    from ogc.graph import verdict_digest
    g = data(RECORD)
    expected = {k: hashlib.sha256((ROOT / f).read_bytes()).hexdigest()
                for k, f in (("shapesDigest", "shapes/epo.shapes.ttl"), ("ontologyDigest", "vocabulary/epo.ttl"), ("queryDigest", "queries/coverage.rq"))}
    (verdict,) = list(g.subjects(RDF.type, EPO.ConformanceVerdict))
    computations = list(g.subjects(RDF.type, EPO.CoverageComputation))
    assert len(computations) == 2  # the draft's coverage computation and the final's (sheet 10-41)
    for k in ("shapesDigest", "ontologyDigest"):
        assert str(g.value(verdict, EPO[k])) == expected[k], f"{k} is stale: run scripts/stamp_digests.py"
    assert g.value(verdict, EPO.queryDigest) is None  # the query is the assembler's tool, not the checker's
    assert str(g.value(verdict, EPO.recordDigest)) == verdict_digest(g)[verdict], "the record digest is stale: run scripts/stamp_digests.py"
    raw = Graph().parse(ROOT / RECORD)  # the digest does not depend on the derived steps or the vocabulary being loaded
    assert verdict_digest(raw)[verdict] == verdict_digest(g)[verdict]
    for c in computations:
        for k, v in expected.items():
            assert str(g.value(c, EPO[k])) == v, f"{c} {k} is stale: run scripts/stamp_digests.py"
        assert g.value(c, EPO.recordDigest) is None


def test_record_digest_covers_the_record_as_it_stood_and_nothing_later():
    """Round four, KG 8: a change to a member dated before the verdict changes the digest; a change to a member dated after it
    (the final report), or to the verdict itself, does not; a comment or a prefix in the file does not."""
    from rdflib import Literal, URIRef
    from ogc.graph import record_digest
    g = Graph().parse(ROOT / RECORD)
    (verdict,) = list(g.subjects(RDF.type, EPO.ConformanceVerdict))
    rec, when = g.value(verdict, OGC.inRecord), g.value(verdict, PROV.generatedAtTime)
    before = record_digest(g, rec, when, exclude={verdict})
    g.add((URIRef(EV + "report"), EPO.gaps, Literal("a later item, after the verdict")))
    g.add((verdict, EPO.text, Literal("the verdict itself")))
    assert record_digest(g, rec, when, exclude={verdict}) == before
    g.add((URIRef(EV + "a1"), EPO.text, Literal("a criterion, dated before the verdict")))
    assert record_digest(g, rec, when, exclude={verdict}) != before


def test_shapes_s0_to_s9():
    g = shapes()
    names = sorted(str(s).rsplit("/", 1)[-1] for s in g.subjects(RDF.type, SH.NodeShape))
    assert names == ["S0-Access", "S0-Independence", "S0-Layers", "S0-Member", "S0-Mission", "S0-Need", "S0-Parties", "S0-Population", "S0-Proposal", "S0-Record", "S0-Roles", "S0-StatementOfWork",
                     "S1-DsoRelease", "S2-AcceptanceCriterion", "S2-Requirement", "S2-RequirementSet",
                     "S3-PlanApproval", "S3-PlanDeviation", "S3-Probe", "S3-Strategy", "S3-TestPlan",
                     "S4-Session", "S4-TestSuite", "S4-Turn", "S5-Evidence", "S5-Response", "S6-Attestation", "S6-Determination",
                     "S7-ConformanceVerdict", "S7-CoverageComputation", "S7-Report", "S7-ReportApproval", "S8-Delivery", "S8-Recommendation", "S9-Acceptance"]


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
        if c in (EPO.Step, EPO.EpoStep, EPO.ContractingStep, EPO.Layer, EPO.AppropriatenessValue, EPO.SufficiencyValue, EPO.FitnessValue, EPO.Engagement, EPO.Affectedness, EPO.IndependenceLevel) or c in roles:
            continue
        if c == EPO.Strategy:  # a prov:Plan, itself a prov:Entity
            continue
        supers = set(g.objects(c, RDFS.subClassOf))
        assert supers & {PROV.Entity, PROV.Activity, PROV.Agent, EARL.Assertion}, c
        assert not ({PROV.Entity, PROV.Activity} <= supers), f"{c}: PROV-O declares prov:Entity and prov:Activity disjoint (round four, KG H1)"
        if EARL.Assertion in supers:
            assert PROV.Entity in supers and PROV.Activity not in supers, f"{c}: an assertion is an entity, dated by prov:generatedAtTime"


def test_record_names_every_human_judgment():
    g = data(RECORD)
    for att in g.subjects(RDF.type, EPO.Attestation):
        who = g.value(att, EARL.assertedBy)
        assert (who, RDF.type, PROV.Person) in g
        assert g.value(att, EPO.appropriateness) is not None and g.value(att, EPO.sufficiency) is not None
        assert (who, EPO.role, EPO.domainExpertRole) in g
    assert len(list(g.subjects(RDF.type, EPO.Attestation))) == 6  # five criteria, a2 attested twice: cannot tell, then passed after the follow-up (sheet 10-48)
    assert len(list(g.subjects(RDF.type, EPO.AcceptanceCriterion))) == 5
    assert len(list(g.subjects(RDF.type, EPO.Determination))) == 7  # sheet 10-15: Theo's determination on a3 is paired with Annie's; a2 determined twice
    a2 = [t for t in g.subjects(RDF.type, EPO.Attestation) if str(g.value(t, EARL.test)).endswith("#a2")]
    assert sorted(str(g.value(g.value(t, EARL.result), EARL.outcome)).rsplit("#", 1)[-1] for t in a2) == ["cantTell", "passed"]
    later = max(a2, key=lambda t: str(g.value(t, PROV.generatedAtTime)))
    assert len(list(g.objects(later, PROV.wasDerivedFrom))) == 2  # the superseding attestation names both determinations (no cherry-picking, sheet 10-14)


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
