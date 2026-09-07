"""The sample report (ruling R-51, sheet 10 items 10-44 and 10-48) is a view of
the record for an executive who knows the domain and little about AI: the JSON
regenerates byte-identically, the share of criteria tested equals
queries/coverage.rq over the record, the visible table has one row per
requirement and every criterion appears once beneath its requirement, the
recommendation is the record's, no sentence in a cell runs past 25 words (a
requirement's why is one sentence per criterion carrying its result), no technical
word and no machine's name reaches the page, the page carries no IRI and no
render-time stamp, d3 comes from the explorer's vendored copy, the record
is read through one function, and the appendix that embeds the report is
the first appendix in the table of contents."""
import json
import re
import sys

import yaml
from rdflib import RDF, RDFS, Literal, Namespace

from conftest import ROOT, load

sys.path.insert(0, str(ROOT / "scripts"))
import render_report as rr  # noqa: E402

EPO = Namespace("https://w3id.org/og-caie/epo#")
EARL = Namespace("http://www.w3.org/ns/earl#")
PROV = Namespace("http://www.w3.org/ns/prov#")
JSON = ROOT / "report" / "report.json"
PAGE = ROOT / "report" / "index.html"
RECORD = ROOT / rr.RECORD_FILE

# The words the reader does not care about (10-48): none may reach the page or the JSON, as whole words,
# in any case. The page says "tested" where the record says coverage.
JARGON = ["ontology", "DSO", "EPO", "SHACL", "pySHACL", "rdflib", "SysML", "requirement set", "attestation",
          "determination", "probe", "trajectory", "IRI", "namespace", "shape", "conformance", "verdict", "bundle",
          "graph", "coverage", "sufficiency", "appropriateness", "evidence item", "software agent", "version identifier"]
RESULT_WORDS = {"met", "not met", "could not tell", "not fully tested"}
BADGES = {"fit to deploy", "fit with conditions", "not fit", "not complete"}


def report() -> dict:
    return json.loads(JSON.read_text())


def strings(x) -> list[str]:
    """Every string value in the JSON, keys excluded: what the page can show."""
    if isinstance(x, str):
        return [x]
    if isinstance(x, dict):
        return [s for v in x.values() for s in strings(v)]
    if isinstance(x, list):
        return [s for v in x for s in strings(v)]
    return []


def test_the_report_regenerates_byte_identically():
    fresh = rr.build(rr.record_graph())
    assert json.dumps(fresh, ensure_ascii=False, sort_keys=True, indent=1) + "\n" == JSON.read_text()
    assert rr.render() == PAGE.read_text()


def test_the_share_tested_and_the_results_equal_the_coverage_query_over_the_record():
    g = load("vocabulary/epo.ttl", rr.RECORD_FILE)
    row = next(iter(g.query((ROOT / "queries" / "coverage.rq").read_text())))
    r = report()
    c = r["criteria"]
    assert c["share"] == float(row.coverage)
    assert c["tested"] == int(row.coveredCount)
    assert c["of"] == len([a for a in g.subjects(RDF.type, EPO.AcceptanceCriterion)])
    assert c["tested"] + len(c["untested"]) == c["of"]
    outcomes = [k["result"] for req in r["results"] for k in req["criteria"] if k["result"] != "not fully tested"]
    assert len(outcomes) == c["tested"]
    for word, rate in (("met", row.passRate), ("not met", row.failRate), ("could not tell", row.cantTellRate)):
        assert abs(outcomes.count(word) - float(rate) * c["tested"]) < 1e-9, word
    if c["share"] == 1:
        assert c["line"] == "Every criterion was tested" and "%" not in c["line"]
        assert not c["untested"]
    else:
        assert c["line"].startswith(f"{c['tested']} of {c['of']} criteria were tested")
        assert c["untested"] and all(u in c["line"] for u in c["untested"])
        assert r["answer"]["badge"] == "not complete"
    assert "%" not in "".join(strings(r)) or c["share"] < 1


def test_one_row_per_requirement_and_every_criterion_once_beneath_its_requirement():
    g = load("vocabulary/epo.ttl", rr.RECORD_FILE)
    r = report()
    requirements = sorted(str(g.value(q, EPO.text)) for q in g.subjects(RDF.type, EPO.Requirement))
    assert sorted(row["requirement"] for row in r["results"]) == requirements
    assert len(r["results"]) == len(requirements)
    criteria = sorted(str(g.value(a, EPO.text)) for a in g.subjects(RDF.type, EPO.AcceptanceCriterion))
    shown = sorted(k["text"] for row in r["results"] for k in row["criteria"])
    assert shown == criteria
    for row in r["results"]:
        assert row["result"] in RESULT_WORDS and row["why"], row["requirement"]
        for k in row["criteria"]:
            assert k["result"] in RESULT_WORDS and k["why"], k["text"]
            criterion = next(g.subjects(EPO.text, Literal(k["text"])))
            assert str(g.value(g.value(criterion, PROV.wasDerivedFrom), EPO.text)) == row["requirement"], k["text"]
        # the requirement's word is decided by its criteria: not met beats could not tell beats not fully tested beats met
        words = {k["result"] for k in row["criteria"]}
        expected = next(w for w in ("not met", "could not tell", "not fully tested", "met") if w in words)
        assert row["result"] == expected, row["requirement"]
    # the page builds exactly these rows: one visible row per requirement, the criteria in a fold beneath
    html = PAGE.read_text()
    assert 'for (const row of R.results)' in html and 'class", "fold"' in html


def test_the_answer_is_the_records_and_says_when_the_evaluation_is_not_complete():
    g = load("vocabulary/epo.ttl", rr.RECORD_FILE)
    rec = next(g.subjects(RDF.type, EPO.Recommendation))
    r = report()
    a = r["answer"]
    assert a["recommendation"] == str(g.value(rec, EPO.text))
    assert a["badge"] in BADGES
    assert a["complete"] == (a["badge"] != "not complete")
    if a["complete"]:
        assert a["headline"] == a["recommendation"].split(". ")[0].rstrip(".") + "."
    else:
        assert a["headline"].startswith("This evaluation is not complete")
    assert a["approved_by"] and a["recommended_by"] and a["date"]
    assert r["question"]
    assert r["item"]["name"] and r["item"]["version"] and r["item"]["purpose"] and r["item"]["environment"] and r["item"]["assumptions"]
    assert r["rests_on"]["tested_by"] and r["rests_on"]["judged_by"] and r["rests_on"]["checked"]["outcome"] and r["rests_on"]["checked"]["date"]
    assert isinstance(r["next"], list)
    assert "synthetic case" in r["note"].lower()


def test_no_cell_runs_past_twenty_five_words():
    """A criterion's cells are one sentence of at most 25 words; a requirement's why is one such sentence per
    criterion carrying its result (drift pass 4, contracting officer 7), so the cap there is per sentence."""
    for row in report()["results"]:
        for cell in (row["requirement"], *(k["text"] for k in row["criteria"]), *(k["why"] for k in row["criteria"])):
            assert len(cell.split()) <= 25, cell
            assert "\n" not in cell
        deciding = [k for k in row["criteria"] if k["result"] == row["result"]]
        assert "\n" not in row["why"] and len(row["why"].split()) <= 25 * max(1, len(deciding)), row["why"]
        for sentence in rr.sentences(row["why"]):
            assert len(sentence.split()) <= 25, sentence


def test_d4_requirement_why_joins_every_deciding_criterion():
    """Contracting officer 7: a requirement's why is the whys of every criterion carrying its result word, in
    criterion order, not the first one's alone."""
    for row in report()["results"]:
        deciding = [k["why"] for k in row["criteria"] if k["result"] == row["result"]]
        assert deciding and row["why"] == " ".join(deciding), row["requirement"]
    assert any(len([k for k in row["criteria"] if k["result"] == row["result"]]) > 1 for row in report()["results"])


def test_no_technical_word_and_no_machines_name_reaches_the_page():
    """The reader is the executive who knows the domain and little about AI (10-48): the page and the JSON's
    visible strings carry none of the words the record and the specification use among themselves, and no
    machine that took part (other than the item tested) is named or versioned on the page."""
    html = PAGE.read_text()
    r = report()
    note = r.pop("note")  # the record's own note, verbatim by the brief; the record words it for the reader
    assert "synthetic case" in note.lower()
    visible = "\n".join(strings(r))
    for word in JARGON:
        pattern = re.compile(rf"\b{re.escape(word)}\b", re.I)
        assert not pattern.search(html), word
        assert not pattern.search(visible), word
    g = load("vocabulary/epo.ttl", rr.RECORD_FILE)
    item = r["item"]["name"]
    for agent in g.subjects(RDF.type, PROV.SoftwareAgent):
        name = str(g.value(agent, RDFS.label) or "")
        if name == item:
            continue
        assert name and name not in visible and name not in html, name
        version = g.value(agent, EPO.version)
        if version is not None:
            assert re.search(rf"(?<![\w.]){re.escape(str(version))}(?![\w.])", visible) is None, str(version)


def test_the_page_carries_no_iri_and_no_render_time_stamp():
    """The page names nothing by IRI, prefix or shape; every date in the JSON
    is one the record holds; nothing is stamped at render time; at most the
    dates the sections name."""
    html = PAGE.read_text()
    text = JSON.read_text()
    for blob in (html, text):
        assert not re.search(r"https?://", blob)
        assert not re.search(r"\b(run|ev|epo|prov|earl|ogc):[a-zA-Z]", blob)
        assert not re.search(r"\bS[0-9]\b", blob)
        assert not re.search(r"(?i)(generated|rendered|built) (at|on) \d", blob)
    record = RECORD.read_text()
    stamps = set(re.findall(r"\d{4}-\d{2}-\d{2}(?:T[\d:]+Z?)?", text))
    for stamp in stamps:
        assert stamp in record, stamp
    assert len({s[:10] for s in stamps}) <= 3
    assert not re.search(r"\d{4}-\d{2}-\d{2}", html)
    assert "—" not in html and "—" not in text


def test_the_page_loads_d3_from_the_explorers_vendored_copy_and_the_json_by_a_relative_path():
    html = PAGE.read_text()
    assert '<script src="../explorer/vendor/d3.v7.min.js"></script>' in html
    assert (PAGE.parent / rr.D3).resolve() == (ROOT / "explorer" / "vendor" / "d3.v7.min.js").resolve()
    assert 'fetch(new URL("report.json", location.href).href)' in html
    assert html.count("<script") == 2  # the library and the page's own script, nothing else
    assert 'href="../explorer/index.html"' in html  # the one link to everything the report leaves out
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
    assert "measles" not in src.lower() and "chatbot" not in src.lower()  # the case's words come from the record


def test_the_page_has_the_six_sections_in_order_and_reads_at_a_phone_width():
    html = PAGE.read_text()
    sections = ["The answer", "What was tested", "How it did", "What it rests on", "What to do next", "A sample report for a synthetic case"]
    positions = [html.find(f'"{s}"') if s != sections[-1] else html.find(s) for s in sections]
    assert all(p >= 0 for p in positions), dict(zip(sections, positions))
    assert positions == sorted(positions)
    for word in ("prefers-color-scheme", "viewport", "@media (max-width", "--met", "--notmet", "--canttell", "--untested"):
        assert word in html, word
    css = html.split("<style>", 1)[1].split("</style>", 1)[0]
    for m in re.finditer(r"(?<![-\w])(width|min-width)\s*:\s*(\d+)px", css):
        assert int(m.group(2)) <= 375, m.group(0)  # nothing fixed wider than a phone
    assert "max-width" in css


def test_the_appendix_is_the_first_appendix_and_embeds_the_report():
    """Appendix A is the sample report (sheet 10 item 10-44); the explorer follows as Appendix B."""
    page = ROOT / "docs" / "appendix-report.md"
    assert page.exists()
    cfg = yaml.safe_load((ROOT / "myst.yml").read_text())
    files = [e.get("file") for e in cfg["project"]["toc"]]
    assert files[files.index("docs/conclusion.md") + 1] == "docs/appendix-report.md"
    assert files[files.index("docs/appendix-report.md") + 1] == "docs/appendix-explorer.md"
    text = page.read_text()
    assert text.startswith("# Appendix A: the sample report\n")
    assert "```{iframe} report/index.html" in text and "(../report/index.html)" in text
    assert "synthetic" in text.lower() and "[Appendix B](appendix-explorer.md)" in text
    assert "executive" in text and "little about AI" in text
    assert "—" not in text
    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    assert len(prose.split()) < 320, len(prose.split())
    guarantees = (ROOT / "docs" / "guarantees.md").read_text()
    assert "appendix-report.md" in guarantees  # Records and reporting points at the sample report
