"""The end-state demonstration (concern C-30): the executor walks the
process the model states and emits a record that conforms to the shapes,
is complete, has a recomputable coverage and traces fully; every mutation
of that run is caught by a named check; execution is deterministic; and a
model whose step signature disagrees with the templates is refused."""
import pytest
from rdflib import RDF, Graph, Namespace

from conftest import ROOT, load
from ogc import executor

SYS = Namespace("https://www.omg.org/spec/SysML#")


@pytest.fixture(scope="module")
def graphs():
    return load("model/og-caie.model.ttl"), load("shapes/epo.shapes.ttl"), load("vocabulary/epo.ttl")


@pytest.fixture(scope="module")
def demo(graphs):
    return executor.demonstrate(*graphs)


def test_the_run_conforms_is_complete_and_traces(demo):
    run = demo["run"]
    assert run["conforms"] and not run["fired"] and not run["missing"], run
    assert run["coverage"]["coverage"] == pytest.approx(2 / 3, abs=1e-4)
    assert run["coverage"]["passRate"] + run["coverage"]["failRate"] + run["coverage"]["cantTellRate"] == pytest.approx(1)
    assert run["traceback"] == 3  # one row per determination: the operator's is paired with the expert's (sheet 10-15)


def test_variants(demo):
    v = demo["variants"]
    assert v["planned 3 of 3"]["conforms"] and v["planned 3 of 3"]["coverage"]["coverage"] == pytest.approx(1)
    assert v["planned 3 of 3"]["traceback"] == 4
    big = v["two sessions, two requirements"]
    assert big["conforms"] and not big["missing"] and big["coverage"]["coverage"] == pytest.approx(1) and big["traceback"] == 12
    five = v["the five judgments"]  # sheet 10-12: every combination S6 allows conforms; the inapplicable one is not covered
    assert five["conforms"] and not five["missing"] and five["coverage"]["coverage"] == pytest.approx(0.8) and five["coverage"]["cantTellRate"] == pytest.approx(0.5)


EXPECTED = {
    "skip-assessment": {"fired": ["S2-RequirementSet"], "missing": ["AppropriatenessAssessment"]},
    "skip-approval": {"fired": [], "missing": ["PlanApproval"]},
    "skip-access": {"fired": ["S2-RequirementSet"], "missing": ["TestItemAccess"], "traceback": 0},  # sheet 10-17: the envelope's test item must be one an access grant names
    "unwire-evidence": {"fired": ["S5-Evidence", "S6-Attestation"], "traceback": 0},
    "executive-attests": {"fired": ["S6-Attestation"]},
    "attest-without-determination": {"fired": ["S6-Attestation", "S8-Recommendation"], "traceback": 0},
    "requirements-before-agreement": {"fired": ["S0-Layers", "S0-Parties"]},
    "engagement-mismatch": {"fired": ["S0-Population"]},
    "skip-report-approval": {"fired": ["S8-Delivery", "S8-Recommendation", "S9-Acceptance"], "missing": ["ReportApproval"]},  # sheets 10-11, 10-03: the approval owns the recommendation and stands behind the acceptance
    "pad-pass-rate": {"fired": ["S7-Report"]},  # sheet 10-19: the rates recomputed
    "one-person-team": {"fired": ["S0-Roles"]},  # sheet 10-13
    "cherry-pick": {"fired": ["S6-Attestation"], "traceback": 2},  # sheet 10-14
}


def test_every_mutation_is_caught_by_a_named_check(demo):
    assert set(demo["mutations"]) == set(EXPECTED)
    for name, exp in EXPECTED.items():
        got = demo["mutations"][name]
        for k, v in exp.items():
            assert got[k] == v, (name, k, got[k], v)
        assert (not got["conforms"]) or got["missing"] or got["traceback"] == 0, f"{name} was not caught"


def test_execution_is_deterministic(graphs):
    model = graphs[0]
    from rdflib.compare import isomorphic
    a, b = executor.execute(model), executor.execute(model)
    assert len(a) == len(b) and isomorphic(a, b)


def test_executor_refuses_a_model_whose_signature_drifts(graphs):
    model = Graph()
    for t in graphs[0]:
        model.add(t)
    approval = next(p for p in model.subjects(SYS.declaredName, None) if str(model.value(p, SYS.qualifiedName)) == "OGCAIE::EvaluationProcess::plan::approval")
    model.remove((approval, None, None))
    with pytest.raises(RuntimeError, match="step plan"):
        executor.execute(model)


def test_the_executed_record_is_complete_against_the_model(graphs):
    model = graphs[0]
    assert executor.completeness(executor.execute(model), model) == []


def test_the_executed_record_is_a_bundle_with_the_verdict_before_the_report(graphs):
    """Sheets 10-31, 10-41, 10-18, 10-33: one bundle every item and agent is a member of; the verdict's subject is the bundle and it
    ended before the final report was generated; the verdict and the coverage computation carry the current digests; no item asserts a step."""
    from rdflib import URIRef
    from ogc.graph import EPO, OGC, PROV, EARL, digests
    g = executor.execute(graphs[0])
    (bundle,) = list(g.subjects(RDF.type, PROV.Bundle))
    for s in {s for s in g.subjects() if isinstance(s, URIRef)} - {bundle}:
        assert (s, OGC.inRecord, bundle) in g and (s, OGC.synthetic, None) in g, s
    (ver,) = list(g.subjects(RDF.type, EPO.ConformanceVerdict))
    (rep,) = list(g.subjects(RDF.type, EPO.Report))
    assert g.value(ver, EARL.subject) == bundle and (rep, PROV.wasDerivedFrom, ver) in g and str(g.value(rep, EPO.draft)) == "false"
    assert str(g.value(ver, PROV.generatedAtTime)) <= str(g.value(rep, PROV.generatedAtTime))
    from ogc.graph import verdict_digest
    for k, v in digests(ROOT).items():
        assert str(g.value(ver, EPO[k])) == (v if k != "queryDigest" else "None")  # the verdict names the shapes and the ontology; the query is the assembler's (round four, KG 8)
        assert str(g.value(next(g.subjects(RDF.type, EPO.CoverageComputation)), EPO[k])) == v
    assert str(g.value(ver, EPO.recordDigest)) == verdict_digest(g)[ver]  # the record as it stood when the checker ran, recomputable
    assert not list(g.subject_objects(EPO.step))


def test_mutation_shapes_map_equals_the_demonstration(demo):
    """`ogc shape` names the mutations that fire a shape from a static map (round four, M5); the map is the demonstration's own result."""
    assert executor.MUTATION_SHAPES == {name: demo["mutations"][name]["fired"] for name in executor.MUTATIONS}
