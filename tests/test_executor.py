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
    assert run["traceback"] == 2


def test_variants(demo):
    v = demo["variants"]
    assert v["planned 3 of 3"]["conforms"] and v["planned 3 of 3"]["coverage"]["coverage"] == pytest.approx(1)
    assert v["planned 3 of 3"]["traceback"] == 3
    big = v["two sessions, two requirements"]
    assert big["conforms"] and not big["missing"] and big["coverage"]["coverage"] == pytest.approx(1) and big["traceback"] == 8


EXPECTED = {
    "skip-assessment": {"fired": ["S2-RequirementSet"], "missing": ["AppropriatenessAssessment"]},
    "skip-approval": {"fired": [], "missing": ["PlanApproval"]},
    "skip-access": {"fired": [], "missing": ["TestItemAccess"], "traceback": 0},
    "unwire-evidence": {"fired": ["S5-Evidence", "S6-Attestation"], "traceback": 0},
    "executive-attests": {"fired": ["S6-Attestation"]},
    "attest-without-determination": {"fired": ["S6-Attestation", "S8-Recommendation"], "traceback": 0},
    "requirements-before-agreement": {"fired": ["S0-Layers", "S0-Parties"]},
    "engagement-mismatch": {"fired": ["S0-Population"]},
    "skip-report-approval": {"fired": ["S8-Delivery"], "missing": ["ReportApproval"]},
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
