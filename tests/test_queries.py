"""Coverage and the outcome distribution recomputed from the record equal
the report's stored values exactly; the traceback query returns all five
facets for the recommendation."""
from fractions import Fraction

from rdflib import RDF

from conftest import EPO, ROOT, load


def query(name, g):
    return list(g.query((ROOT / "queries" / name).read_text()))


def test_coverage_recomputes_to_the_report():
    g = load("vocabulary/epo.ttl", "track/measles-run.ttl")
    (row,) = query("coverage.rq", g)
    report = next(g.subjects(RDF.type, EPO.Report))
    stored = {k: Fraction(str(g.value(report, EPO[k]))) for k in ("coverage", "passRate", "failRate", "cantTellRate")}
    got = {"coverage": Fraction(str(row.coverage)), "passRate": Fraction(str(row.passRate)),
           "failRate": Fraction(str(row.failRate)), "cantTellRate": Fraction(str(row.cantTellRate))}
    assert got == stored, (got, stored)
    assert got["coverage"] == Fraction(3, 4)
    assert int(row.coveredCount) == 2


def test_traceback_returns_the_five_facets():
    g = load("vocabulary/epo.ttl", "track/measles-run.ttl")
    rows = query("traceback.rq", g)
    assert len(rows) == 2
    for r in rows:
        assert r.author and r.step and r.assertor and r.criterion and str(r.outcome) == "failed"
        assert r.evidence and r.run and r.operator and r.sut and r.dso and r.dsoApprover
    assert {str(r.assertor) for r in rows} == {
        "Dr. A, epidemiologist (domain expert)", "B, community public-health educator (domain expert)"}
    assert str(rows[0].step).startswith("5 report")
