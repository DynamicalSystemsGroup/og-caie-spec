"""Coverage and the outcome distribution recomputed from the record equal
the report's stored values exactly; the traceback query returns all five
facets for the recommendation and the parties (sheet 10-05 to 10-07). The
data graph is the record with the EPO vocabulary and the model graph, the
queries' precondition (sheets 10-31, 10-33)."""
from fractions import Fraction

from rdflib import RDF

from conftest import EPO, ROOT, load


def query(name, g):
    return list(g.query((ROOT / "queries" / name).read_text()))


def data():
    return load("vocabulary/epo.ttl", "model/og-caie.model.ttl", "track/measles-evaluation.ttl")


def test_coverage_recomputes_to_the_report():
    g = data()
    (row,) = query("coverage.rq", g)
    assert str(row.record).endswith("evaluation/measles#record")  # one row per record (sheet 10-31)
    report = next(g.subjects(RDF.type, EPO.Report))
    stored = {k: Fraction(str(g.value(report, EPO[k]))) for k in ("coverage", "passRate", "failRate", "cantTellRate")}
    got = {"coverage": Fraction(str(row.coverage)), "passRate": Fraction(str(row.passRate)),
           "failRate": Fraction(str(row.failRate)), "cantTellRate": Fraction(str(row.cantTellRate))}
    assert got == stored, (got, stored)
    assert got["coverage"] == Fraction(3, 4)
    assert int(row.coveredCount) == 2


def test_traceback_returns_the_five_facets():
    g = data()
    rows = query("traceback.rq", g)
    assert len(rows) == 3  # one row per determination an attestation aggregates: attestation-2 has two (sheet 10-15)
    for r in rows:
        assert r.author and r.step and r.assertor and r.criterion and str(r.outcome) == "failed"
        assert r.evidence and r.run and r.operator and r.sut and r.dso and r.dsoApprover
        assert r.probe and r.plan and r.expected
        assert int(r.turnIndex) == 1
        assert str(r.determined) == "failed" and r.determiner
        assert r.agreement and r.proposal and r.sponsor and r.signatory and r.testingOrg and r.independentOf and r.accountable and r.delivery and r.deliverer
        assert str(r.userInterest) == "true" and str(r.record).endswith("#record")
    assert {str(r.assertor) for r in rows} == {"Annie (domain expert)"}
    assert [str(r.determiner) for r in rows] == ["Annie (domain expert)", "Theo (evaluation operator)", "Annie (domain expert)"]
    assert {str(r.deliverer) for r in rows} == {"Mala (authorized representative)"}
    assert {str(r.signatory) for r in rows} == {"Dana Okafor (county health officer, sponsor signatory)"}  # sheet 10-06
    assert {str(r.independentOf) for r in rows} == {"chatbot vendor (test item provider)"}  # sheet 10-07
    assert str(rows[0].step).startswith("6 report")  # derived through the model graph (sheet 10-33)
