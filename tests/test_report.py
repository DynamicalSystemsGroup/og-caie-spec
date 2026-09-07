"""The sample report (ruling R-51, sheet 10 item 10-44) is a view of the
measles record and nothing else: the JSON regenerates byte-identically, its
coverage and rates equal queries/coverage.rq over the record, every
criterion of the record appears once, the recommendation is the record's,
the page carries no IRI and no render-time stamp, d3 comes from the
explorer's vendored copy, the record is read through one function, and the
appendix that embeds the report is the first appendix in the table of
contents."""
import json
import re
import sys

import yaml
from rdflib import RDF, Namespace

from conftest import ROOT, load

sys.path.insert(0, str(ROOT / "scripts"))
import render_report as rr  # noqa: E402

EPO = Namespace("https://w3id.org/og-caie/epo#")
EARL = Namespace("http://www.w3.org/ns/earl#")
PROV = Namespace("http://www.w3.org/ns/prov#")
JSON = ROOT / "report" / "report.json"
PAGE = ROOT / "report" / "index.html"
RECORD = ROOT / rr.RECORD_FILE


def report() -> dict:
    return json.loads(JSON.read_text())


def test_the_report_regenerates_byte_identically():
    fresh = rr.build(rr.record_graph())
    assert json.dumps(fresh, ensure_ascii=False, sort_keys=True, indent=1) + "\n" == JSON.read_text()
    assert rr.render() == PAGE.read_text()


def test_coverage_and_the_rates_equal_the_coverage_query_over_the_record():
    g = load("vocabulary/epo.ttl", rr.RECORD_FILE)
    row = next(iter(g.query((ROOT / "queries" / "coverage.rq").read_text())))
    c = report()["coverage"]
    assert c["coverage"] == float(row.coverage)
    assert c["pass_rate"] == float(row.passRate)
    assert c["fail_rate"] == float(row.failRate)
    assert c["cant_tell_rate"] == float(row.cantTellRate)
    assert c["covered_count"] == int(row.coveredCount)
    assert 0 < c["coverage"] < 1  # the measles case leaves one criterion unplanned
    assert abs(c["pass_rate"] + c["fail_rate"] + c["cant_tell_rate"] - 1) < 1e-9


def test_every_criterion_of_the_record_appears_once_with_its_requirement():
    g = load("vocabulary/epo.ttl", rr.RECORD_FILE)
    ids = [c["id"] for c in report()["criteria"]]
    assert ids == sorted(str(a).rsplit("#", 1)[-1] for a in g.subjects(RDF.type, EPO.AcceptanceCriterion))
    assert len(ids) == len(set(ids))
    planned = {str(a).rsplit("#", 1)[-1] for p in g.subjects(RDF.type, EPO.TestPlan) for a in g.objects(p, EPO.objective)}
    for c in report()["criteria"]:
        assert c["requirement"] and c["text"] and c["expected"] and c["weight"] > 0, c["id"]
        assert c["planned"] == (c["id"] in planned)
        assert c["outcome"] in {"passed", "failed", "cannot tell", "not planned", "not attested"}
        if c["outcome"] == "not planned":
            assert not c["attestations"] and not c["planned"]
        for a in c["attestations"]:
            assert a["by"] and a["date"] and a["appropriateness"] and a["sufficiency"], c["id"]
            for d in a["determinations"]:
                assert d["by"] and d["outcome"] and d["evidence"], c["id"]
                for e in d["evidence"]:
                    assert e["probe"]["text"] and e["response"]["text"], c["id"]


def test_the_recommendation_and_the_synthetic_note_are_the_records_own():
    g = load("vocabulary/epo.ttl", rr.RECORD_FILE)
    rec = next(g.subjects(RDF.type, EPO.Recommendation))
    r = report()
    assert r["recommendation"]["text"] == str(g.value(rec, EPO.text))
    assert r["verdict"] in {"passed", "failed", "cannot tell"}
    assert "Synthetic case" in r["record"]["note"]
    assert r["sponsor"]["need"] and r["sponsor"]["mission"] and r["test_item"]["version"]


def test_the_page_carries_no_iri_and_no_render_time_stamp():
    """The page names nothing by IRI, prefix or shape; every date in the JSON
    is one the record holds; nothing is stamped at render time."""
    html = PAGE.read_text()
    text = JSON.read_text()
    for blob in (html, text):
        assert not re.search(r"https?://", blob)
        assert not re.search(r"\b(run|ev|epo|prov|earl|ogc):[a-zA-Z]", blob)
        assert not re.search(r"\bS[0-9]\b", blob)
        assert not re.search(r"(?i)(generated|rendered|built) (at|on) \d", blob)
    record = RECORD.read_text()
    for stamp in set(re.findall(r"\d{4}-\d{2}-\d{2}(?:T[\d:]+Z?)?", text)):
        assert stamp in record, stamp
    assert not re.search(r"\d{4}-\d{2}-\d{2}", html)
    assert "—" not in html and "—" not in text


def test_the_page_loads_d3_from_the_explorers_vendored_copy_and_the_json_by_a_relative_path():
    html = PAGE.read_text()
    assert '<script src="../explorer/vendor/d3.v7.min.js"></script>' in html
    assert (PAGE.parent / rr.D3).resolve() == (ROOT / "explorer" / "vendor" / "d3.v7.min.js").resolve()
    assert 'fetch(new URL("report.json", location.href).href)' in html
    assert html.count("<script") == 2  # the library and the page's own script, nothing else
    for word in ("report/", "appendix-report/report", "explorer/vendor/d3.v7.min.js"):
        assert word in (ROOT / "scripts" / "copy_explorer.sh").read_text(), word
    assert "scripts/render_report.py" in (ROOT / "checks" / "regen.sh").read_text()


def test_the_record_is_read_through_one_function():
    """Renaming the record is a change to ogc.graph.RECORD_FILE; this script names neither the file nor its namespace."""
    src = (ROOT / "scripts" / "render_report.py").read_text()
    assert src.count("ROOT / RECORD_FILE") == 1  # the one read
    assert re.search(r"^from ogc\.graph import .*\bRECORD_FILE\b", src, re.M)  # the name comes from the tool, not from here
    assert "track/" not in src and "w3id.org" not in src
    assert src.count("g.parse(") == 2  # the EPO and the record, both in record_graph


def test_the_dashboard_shows_every_section_the_brief_names():
    html = PAGE.read_text()
    for section in ("The criteria, by weight and outcome", "Each criterion, and what it was judged on", "What the judgments assume",
                    "The chain of custody", "Who was party to it", "A sample report for a synthetic case"):
        assert section in html, section
    for word in ("prefers-color-scheme", "viewport", "max-width:640px", "--passed", "--failed", "--canttell", "--notplanned"):
        assert word in html, word
    r = report()
    assert len(r["timeline"]) >= 10 and r["timeline"] == sorted(r["timeline"], key=lambda e: (e["date"], e["what"], e["who"]))
    assert r["conformance"]["outcome"] and r["approval"]["outcome"] and r["delivery"]["date"] and r["acceptance"]["date"]
    assert r["assumptions"]["dso"]["label"] and r["assumptions"]["environment"]
    assert set(r["parties"]) == {"organizations", "people", "populations"}
