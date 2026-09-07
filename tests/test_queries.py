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
    (report,) = [r for r in g.subjects(RDF.type, EPO.Report) if str(g.value(r, EPO.draft)) == "false"]  # the final report; the draft is a snapshot of its day (sheet 10-48)
    stored = {k: Fraction(str(g.value(report, EPO[k]))) for k in ("coverage", "passRate", "failRate", "cantTellRate")}
    got = {"coverage": Fraction(str(row.coverage)), "passRate": Fraction(str(row.passRate)),
           "failRate": Fraction(str(row.failRate)), "cantTellRate": Fraction(str(row.cantTellRate))}
    assert got == stored, (got, stored)
    assert got["coverage"] == Fraction(1)  # every criterion attested (sheet 10-48, R-51)
    assert int(row.coveredCount) == 5
    assert got["passRate"] == Fraction(4, 5) and got["failRate"] == Fraction(1, 5) and got["cantTellRate"] == 0  # a2 counts once, passed: the later attestation
    (draft,) = [r for r in g.subjects(RDF.type, EPO.Report) if str(g.value(r, EPO.draft)) == "true"]
    assert Fraction(str(g.value(draft, EPO.cantTellRate))) == Fraction(1, 5) and g.value(draft, EPO.gaps) is not None  # the draft flagged the cannot-tell of its day


def test_traceback_returns_the_five_facets():
    g = data()
    rows = query("traceback.rq", g)
    assert len(rows) == 20  # one row per response a determination rests on: seven evidence items over twelve responses, a3 paired, a2 judged twice (sheet 10-15)
    for r in rows:
        assert r.author and r.step and r.assertor and r.criterion and str(r.outcome) in ("passed", "failed", "cantTell")
        assert r.evidence and r.run and r.operator and r.sut and r.dso and r.dsoApprover
        assert r.probe and r.plan and r.expected
        assert 1 <= int(r.turnIndex) <= 3
        assert str(r.determined) in ("passed", "failed", "cantTell") and r.determiner
        assert r.agreement and r.proposal and r.sponsor and r.signatory and r.testingOrg and r.independentOf and r.accountable and r.delivery and r.deliverer
        assert str(r.userInterest) == "true" and str(r.record).endswith("#record")
    assert {str(r.assertor) for r in rows} == {"Annie (domain expert)"}
    assert {str(r.determiner) for r in rows} == {"Annie (domain expert)", "Theo (evaluation operator)"}
    by_attestation = {}
    for r in rows:
        by_attestation.setdefault(str(r.attestation).rsplit("#", 1)[-1], set()).add((str(r.outcome), str(r.determined)))
    assert by_attestation["attestation-3"] == {("failed", "failed")}  # the unmet criterion, two rulings agreeing
    assert by_attestation["attestation-6"] == {("passed", "cantTell"), ("passed", "passed")}  # the superseding attestation names the earlier ruling too
    assert [(str(r.attestation).rsplit("#", 1)[-1], str(r.determination).rsplit("#", 1)[-1], str(r.run).rsplit("#", 1)[-1], int(r.turnIndex)) for r in rows] == sorted(
        (str(r.attestation).rsplit("#", 1)[-1], str(r.determination).rsplit("#", 1)[-1], str(r.run).rsplit("#", 1)[-1], int(r.turnIndex)) for r in rows)  # ordered, so the fragment regenerates byte for byte
    assert {str(r.deliverer) for r in rows} == {"Mala (authorized representative)"}
    assert {str(r.signatory) for r in rows} == {"Dana Okafor (county health officer, sponsor signatory)"}  # sheet 10-06
    assert {str(r.independentOf) for r in rows} == {"Meridian Health Software, the chatbot's vendor (test item provider; an invented company)"}  # sheet 10-07
    assert str(rows[0].step).startswith("6 report")  # derived through the model graph (sheet 10-33)
