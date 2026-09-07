"""The `ogc` navigation tool (ruling R-29): every command is deterministic,
carries the invocation and commit in its first line, exits 0 / 1 / 2 as
documented, resolves every glossary label to one term, refuses to write,
and its doctor passes on the committed graphs. The `test_finding_NN` tests
hold the fixes from the machine-user review of 2026-09-06, one per finding."""
import json
import re
import subprocess
import sys

import pytest
from rdflib import RDF

from conftest import EPO, OGC, ROOT, load

SKOS = "http://www.w3.org/2004/02/skos/core#"
COMMANDS = [
    ["schema"], ["find", "probe"], ["find", "probe", "--no-quotes"], ["term", "probe"], ["define", "conformance"], ["quote", "attestation"], ["quote", "1 scope"],
    ["list", "--class", "coined"], ["list", "--source", "sevocab"], ["source", "sevocab"], ["sources"], ["ruling", "r-16"], ["rulings", "--grep", "conformance"],
    ["concern", "c-24"], ["concerns", "--open"], ["sci"], ["sci", "SCI-11"], ["steps"], ["views"], ["view", "contracting"], ["execute"], ["crosswalk", "--class", "refined"], ["crosswalk", "--popper"],
    ["check-word", "adequacy", "evidence", "probe"], ["verify", "conformance"], ["verify", "sevocab"], ["verify", "need"], ["verify", "--all"],
    ["shapes"], ["shape", "S3-PlanApproval"], ["shape", "m1-parties"],
    ["sparql", 'SELECT ?l WHERE { ?t a skos:Concept ; ogc:class "coined" ; skos:prefLabel ?l }'],
    ["sparql", "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 20"],
    ["sparql", "CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o } LIMIT 30"],
    ["record"], ["record", "mission-1"], ["record", "attestation-1"], ["--record", "sparql", "DESCRIBE run:mission-1"],
    ["execute", "--planned", "3", "--sessions", "2"],
]
# A mutated run fails its VERDICT on purpose (finding 9): deterministic, exit 1.
MUTATED = [["execute", "--mutate", "skip-access"]]


def run(*args):
    return subprocess.run([sys.executable, "-m", "ogc", "--no-cache", *args], cwd=ROOT, capture_output=True, text=True)


def test_every_command_is_deterministic_and_exits_zero():
    for cmd in COMMANDS:
        a, b = run(*cmd), run(*cmd)
        assert a.returncode == 0, (cmd, a.stdout, a.stderr)
        assert a.stdout == b.stdout, cmd
        assert a.stdout.startswith("# ogc "), cmd
    for cmd in MUTATED:
        a, b = run(*cmd), run(*cmd)
        assert a.returncode == 1, (cmd, a.stdout, a.stderr)
        assert a.stdout == b.stdout, cmd
        assert a.stdout.startswith("# ogc "), cmd


def test_json_twin_parses():
    for cmd in COMMANDS + MUTATED:
        r = run(*cmd, "--json")
        assert r.returncode == (1 if cmd in MUTATED else 0), (cmd, r.stderr)
        d = json.loads(r.stdout)
        assert isinstance(d, dict), cmd
        assert d["_ogc"]["command"] == next(x for x in cmd if not x.startswith("--")) and d["_ogc"]["sha"], cmd  # finding 13: every JSON object is citable


def test_exit_codes():
    assert run("term", "no-such-term-xyz").returncode == 1
    assert run("ruling", "R-99").returncode == 1
    assert run("concerns", "--status", "bogus").returncode == 1
    assert run("verify").returncode == 2
    assert run("sparql", "SELECT ?s WHERE { SERVICE <http://x> { ?s ?p ?o } }").returncode == 2
    assert run("sparql", "DELETE WHERE { ?s ?p ?o }").returncode == 2
    assert run("sparql", "SELECT ?s WHERE { ?s ?p").returncode == 2


def test_every_label_resolves_to_exactly_one_term():
    sys.path.insert(0, str(ROOT))
    from ogc import api
    g = load("vocabulary/og-caie.ttl")
    assert api.ambiguous_labels(g) == []
    for t in g.subjects(RDF.type, __import__("rdflib").URIRef(SKOS + "Concept")):
        for l in [g.value(t, __import__("rdflib").URIRef(SKOS + "prefLabel")), *g.objects(t, __import__("rdflib").URIRef(SKOS + "altLabel"))]:
            iri, cands, meta = api.resolve_term(g, str(l))
            assert iri == t, (str(l), cands)


def test_check_word_semantics():
    r = run("check-word", "adequacy", "--json")
    d = json.loads(r.stdout)["rows"][0]
    assert d["retired"] and not d["registered"]
    r = run("check-word", "system under test", "--json")
    d = json.loads(r.stdout)["rows"][0]
    assert d["registered"] and d["matched_as"] == "alt" and d["term"] == "test item"
    assert "{term}`system under test <test item>`" in d["advice"]


def test_verify_agrees_with_the_citation_tests():
    r = run("verify", "--all", "--json")
    rows = json.loads(r.stdout)["rows"]
    states = {x["state"] for x in rows}
    assert "NOT FOUND" not in states, [x for x in rows if x["state"] == "NOT FOUND"]
    assert sum(1 for x in rows if x["state"] == "pending") == 0  # sheet 04 ticked (R-47)


def test_doctor_passes():
    r = run("doctor")
    assert r.returncode == 0, r.stdout
    assert r.stdout.rstrip().splitlines()[-1].startswith("VERDICT: PASS")


# ---------------------------------------------------------------- the review findings, one test each

def test_finding_01_graph_keyword_is_refused_not_a_traceback():
    r = run("sparql", "SELECT ?g WHERE { GRAPH ?g { ?s ?p ?o } } LIMIT 3")
    assert r.returncode == 2 and "named graphs are not exposed" in r.stderr and "Traceback" not in r.stderr


def test_finding_02_limit_without_order_by_is_deterministic_and_bnodes_are_labelled():
    q = "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 20"
    a, b = run("sparql", q), run("sparql", q)
    assert a.stdout == b.stdout and "_:b" in a.stdout and not re.search(r"\bn[0-9a-f]{32}\b", a.stdout)
    c = "CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o } LIMIT 30"
    a, b = run("sparql", c), run("sparql", c)
    assert a.stdout == b.stdout and a.stdout.count("@prefix") == a.stdout.count("@prefix")
    ordered = run("sparql", "SELECT ?l WHERE { ?t a skos:Concept ; skos:prefLabel ?l } ORDER BY DESC(?l) LIMIT 2").stdout
    assert ordered.splitlines()[3] > ordered.splitlines()[4]  # ORDER BY is honoured, not re-sorted


def test_finding_03_model_flag_is_in_the_printed_header():
    q = "SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }"
    with_model, without = run("--model", "sparql", q), run("sparql", q)
    assert with_model.stdout.splitlines()[0] != without.stdout.splitlines()[0]
    assert "--model" in with_model.stdout.splitlines()[0] and "--no-quotes" in run("find", "probe", "--no-quotes").stdout.splitlines()[0]


def test_finding_04_source_filter_is_validated_and_case_insensitive():
    for cmd in (["list", "--source", "bogus"], ["crosswalk", "--source", "nope"]):
        r = run(*cmd)
        assert r.returncode == 1 and "candidate:" in r.stdout, cmd
    r = run("list", "--source", "SEVOCAB")
    assert r.returncode == 0 and "(none)" not in r.stdout


def test_finding_05_one_id_normaliser_for_rulings_concerns_and_essentials():
    for cmd in (["ruling", "r-5"], ["ruling", "R16"], ["ruling", "R-016"], ["ruling", "16"], ["concern", "c-7"], ["concern", "C7"], ["concern", "c-025"],
                ["sci", "SCI07"], ["sci", "sci-7"], ["sci", "SCI-7"], ["sci", "7"]):
        assert run(*cmd).returncode == 0, cmd
    assert run("ruling", "C-5").returncode == 1


def test_finding_06_sci_help_states_the_range_the_graph_holds():
    sys.path.insert(0, str(ROOT))
    from ogc import api, cli
    g = load("model/trace.ttl")
    ids = sorted(api.local(t) for t in g.subjects(RDF.type, OGC.Trace))
    assert cli.SCI_RANGE == f"{ids[0]}..{ids[-1][-2:]}"
    assert cli.SCI_RANGE in run("sci", "--help").stdout


def test_finding_07_empty_word_is_a_usage_error():
    assert run("check-word", "").returncode == 2
    assert run("check-word", "   ").returncode == 2
    assert run("check-word", "probe", "").returncode == 2


def test_finding_08_mutations_are_validated_and_repeatable():
    r = run("execute", "--mutate", "")
    assert r.returncode == 1 and "candidate: skip-access" in r.stdout
    r = run("execute", "--mutate", "skip-approval", "--mutate", "skip-access", "--json")
    assert json.loads(r.stdout)["mutations"] == ["skip-approval", "skip-access"]


def test_finding_09_execute_prints_a_verdict_and_fails_on_a_missing_item_kind():
    r = run("execute", "--mutate", "skip-approval")
    assert r.returncode == 1 and "VERDICT: FAIL" in r.stdout and "missing item kinds: PlanApproval" in r.stdout
    r = run("execute")
    assert r.returncode == 0 and r.stdout.rstrip().splitlines()[-1].startswith("VERDICT: PASS")


def test_finding_10_verify_and_quote_accept_a_step():
    for what in ("scope", "1 scope", "C1 need", "need", "acceptDelivery"):
        assert run("verify", what).returncode == 0, what
        assert run("quote", what).returncode == 0, what
    rows = json.loads(run("verify", "--all", "--json").stdout)["rows"]
    assert {"holder", "citation"} <= set(rows[0]) and "term" not in rows[0]


def test_finding_11_one_status_vocabulary_everywhere():
    steps = json.loads(run("steps", "--json").stdout)["rows"]
    statuses = {a["status"] for r in steps for a in r["also"]} | {r["status"] for r in steps}
    assert "" not in statuses and "cite-only" in statuses
    assert "(cite-only)" not in run("steps").stdout
    verify = json.loads(run("verify", "--all", "--json").stdout)["rows"]
    assert {r["status"] for r in verify if r["state"] == "cite-only"} == {"cite-only"}
    assert json.loads(run("define", "probe", "--json").stdout)["status"] == "machine"
    assert "[]" not in run("check-word", "OG-CAIE").stdout


def test_finding_12_help_lists_the_allowed_values():
    assert "skip-approval" in run("execute", "--help").stdout
    assert "adopted, refined, coined" in run("list", "--help").stdout
    assert "heldLocally" in run("sources", "--help").stdout
    assert "open, ruled, closed" in run("concerns", "--help").stdout and "H, M, L" in run("concerns", "--help").stdout
    assert "1 scope" in run("verify", "--help").stdout and "SCI-01" in run("sci", "--help").stdout


def test_finding_13_json_carries_the_invocation_and_sha():
    d = json.loads(run("term", "probe", "--json").stdout)
    assert d["_ogc"] == {"command": "term", "args": "probe", "sha": d["_ogc"]["sha"]} and len(d["_ogc"]["sha"]) >= 7
    d = json.loads(run("list", "--class", "coined", "--json").stdout)
    assert d["_ogc"]["args"] == "--class coined" and len(d["rows"]) == 4


def test_finding_14_json_summary_and_no_empty_grep_fields():
    d = json.loads(run("verify", "--all", "--json").stdout)
    assert d["summary"]["citations"] == len(d["rows"]) and sum(d["summary"]["states"].values()) == len(d["rows"])
    rows = json.loads(run("rulings", "--term", "probe", "--json").stdout)["rows"]
    assert rows and all("matched" not in r and "snippet" not in r for r in rows)


def test_finding_15_slug_is_stripped_before_the_iri_is_built():
    r = run("source", "sevocab ")
    assert r.returncode == 0 and "does not look like a valid URI" not in r.stderr


def test_finding_16_all_and_a_term_together_is_a_usage_error():
    assert run("verify", "--all", "probe").returncode == 2


def test_finding_17_names_and_filter_values_are_case_insensitive():
    for cmd in (["view", "Contracting"], ["source", "SEVOCAB"], ["execute", "--mutate", "Skip-Access"], ["list", "--class", "Coined"],
                ["sources", "--posture", "heldlocally"], ["concerns", "--severity", "h"], ["concerns", "--status", "Open"], ["shape", "s3-planapproval"]):
        assert run(*cmd).returncode in (0, 1) and run(*cmd).stdout.startswith("# ogc " + cmd[0]), cmd


def test_finding_18_a_huge_query_is_refused_as_too_long():
    r = run("sparql", "SELECT ?s WHERE { " + "?s ?p ?o . " * 2500 + "}")  # over the 20,000-character cap, under the OS argument limit
    assert r.returncode == 2 and "too long" in r.stderr and "recursion" not in r.stderr


def test_finding_19_shape_reader():
    d = json.loads(run("shape", "S3-PlanApproval", "--json").stdout)
    assert d["target"] == ["epo:PlanApproval"] and d["file"] == "shapes/epo.shapes.ttl"
    assert any(p["path"] == "epo:approves" and p["min"] == "1" and p["class"] == "epo:TestPlan" for p in d["properties"])
    assert d["sparql"] and all(m for m in d["sparql"])
    rows = json.loads(run("shapes", "--json").stdout)["rows"]
    assert {r["file"] for r in rows} >= {"shapes/epo.shapes.ttl", "shapes/model.shapes.ttl", "shapes/rulings.shapes.ttl"}
    assert any(r["id"] == "RulingShape" and r["target"] == ["ogc:Ruling"] for r in rows)
    assert run("shape", "nope").returncode == 1


def test_finding_20_coverage_is_prose_and_empty_grep_is_usage():
    out = run("execute").stdout
    assert re.search(r"^coverage: \d\.\d{4} \(pass \d\.\d\d, fail \d\.\d\d, cannot tell \d\.\d\d\)$", out, re.M) and "{'coverage'" not in out
    assert run("rulings", "--grep", "").returncode == 2


# ---------------------------------------------------------------- the record (C-44, ruling R-47) and the executor's parameters

def _rows(*cmd):
    return json.loads(run(*cmd, "--json").stdout)["rows"]


def test_record_lists_every_stepped_item_by_step():
    rg = load("track/measles-run.ttl")
    stepped = {str(s).rsplit("#", 1)[-1] for s in rg.subjects(EPO.step, None)}
    r = run("record")
    assert r.returncode == 0, r.stderr
    rows = _rows("record")
    assert {x["item"] for x in rows if x["group"] == "step"} == stepped and len(stepped) > 20
    orders = [x["order"] for x in rows if x["group"] == "step"]
    assert orders == sorted(orders) and orders[0] == 1 and orders[-1] == 16  # C1..C6 then 1..6
    steps = [x["step"] for x in rows if x["group"] == "step"]
    assert steps[0] == "C1 need" and steps[-1] == "6 report" and steps.index("C6 accept") < steps.index("1 scope")
    for name in stepped:
        assert re.search(rf"^\S.*\s{re.escape(name)}\s", r.stdout, re.M), name
    assert "without a step" in r.stdout and any(x["item"] == "turn-1" and x["group"] == "no-step" for x in rows)
    assert [x["item"] for x in rows if x["group"] == "record"] == ["record"]  # the record's own entity heads the listing in its own section (round three, M7)
    who = next(x for x in rows if x["item"] == "attestation-1")
    assert who["who"] == ["Annie (domain expert)"] and who["when"] == "2026-08-11"
    assert any(x["item"] == "annie" and x["group"] == "party" for x in rows)


def test_record_item_prints_its_label_and_step():
    r = run("record", "mission-1")
    assert r.returncode == 0 and "C1 need" in r.stdout and "protect the health of county residents" in r.stdout
    d = json.loads(run("record", "mission-1", "--json").stdout)
    assert d["item"] == "mission-1" and d["step"] == "C1 need" and d["class"] == "Mission"
    assert any(t["predicate"] == "epo:regards" and t["object"] == "run:commuters" and t["label"].startswith("commuters") for t in d["triples"])
    assert any(t["predicate"] == "epo:underMission" and t["subject"] == "run:need-1" for t in d["referenced_by"])
    r = run("record", "attestation-1")
    assert "earl:outcome earl:failed" in r.stdout  # a blank node's triples are printed inline
    assert run("record", "MISSION-1").returncode == 0
    r = run("record", "mission")
    assert r.returncode == 1 and "candidate: mission-1" in r.stdout
    assert run("record", "no-such-item-xyz").returncode == 1


def test_record_flag_loads_the_record_for_sparql():
    q = "SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }"
    with_record, without = run("--record", "sparql", q), run("sparql", q)
    assert with_record.stdout.splitlines()[0] != without.stdout.splitlines()[0] and "--record" in with_record.stdout.splitlines()[0]
    n = lambda r: int(json.loads(r.stdout)["rows"][0]["n"])
    assert n(run("--record", "sparql", q, "--json")) > n(run("sparql", q, "--json"))
    assert "--record" in json.loads(run("sparql", q, "--record", "--json").stdout)["_ogc"]["args"]
    assert "run:mission-1" in run("sparql", "DESCRIBE run:mission-1", "--record").stdout


def test_execute_exposes_the_executor_parameters():
    r = run("execute", "--planned", "3")
    assert r.returncode == 0, r.stdout
    assert "coverage: 1.0000" in r.stdout and "traceback rows: 3" in r.stdout and r.stdout.rstrip().splitlines()[-1].startswith("VERDICT: PASS")
    assert re.search(r"^parameters: requirements 1, criteria 3, planned 3, sessions 1, populations 2$", r.stdout, re.M)
    d = json.loads(run("execute", "--planned", "3", "--json").stdout)
    assert d["params"] == {"requirements": 1, "criteria": 3, "planned": 3, "sessions": 1, "populations": 2}
    assert d["coverage"]["coverage"] == 1 and d["traceback"] == 3 and d["_ogc"]["args"] == "--planned 3"
    r = run("execute", "--planned", "9")
    assert r.returncode == 1 and "at most" in r.stdout and "VERDICT" not in r.stdout
    assert json.loads(run("execute", "--planned", "9", "--json").stdout)["error"]
    for bad in (["--sessions", "0"], ["--requirements", "-1"], ["--criteria", "0"], ["--populations", "0"]):
        assert run("execute", *bad).returncode == 1, bad
    assert run("execute", "--planned", "x").returncode == 2
    d = json.loads(run("execute", "--requirements", "2", "--criteria", "2", "--planned", "4", "--sessions", "2", "--json").stdout)
    assert d["ok"] and d["traceback"] == 8 and d["params"]["sessions"] == 2


# ---------------------------------------------------------------- the second review (2026-09-06), one test each

import hashlib  # noqa: E402

SKILL = ROOT / ".claude" / "skills" / "ogc-glossary" / "SKILL.md"
NUMBER_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]


def _json(*cmd):
    r = run(*cmd, "--json")
    return r, json.loads(r.stdout)


def test_r2_finding_01_query_file_that_is_a_directory_is_a_usage_error():
    for f in ("@.", f"@{ROOT}"):  # a bare `@` is "no path after @" since round three (L6)
        r = run("sparql", f)
        assert r.returncode == 2 and "query file is a directory" in r.stderr and "Traceback" not in r.stderr, f
    r, d = _json("sparql", "@.")
    assert r.returncode == 2 and d["error"] == "usage" and d["_ogc"]["command"] == "sparql" and r.stderr == ""


def test_r2_finding_02_execute_is_capped():
    r = run("execute", "--requirements", "20", "--criteria", "20", "--planned", "400")
    assert r.returncode == 1 and "at most 100" in r.stdout and "VERDICT" not in r.stdout
    r = run("execute", "--sessions", "21")
    assert r.returncode == 1 and "at most 20" in r.stdout
    assert run("execute", "--populations", "21").returncode == 1
    r = run("execute", "--requirements", "5", "--criteria", "5", "--planned", "25", "--sessions", "5")  # 125 criterion-sessions of work
    assert r.returncode == 1 and "times sessions must be at most 100" in r.stdout
    r, d = _json("execute", "--sessions", "21")
    assert r.returncode == 1 and d["_ogc"]["command"] == "execute" and "at most 20" in d["hint"]
    help_ = run("execute", "--help").stdout
    assert "requirements times criteria at most 100" in help_ and "sessions at most 20" in help_
    assert "requirements times criteria at most 100" in SKILL.read_text()


def test_r2_finding_03_query_naming_the_record_without_the_flag_is_refused_with_a_hint():
    for q in ("DESCRIBE run:mission-1", "SELECT ?a WHERE { ?a a epo:Attestation }", "SELECT ?s WHERE { ?s rdf:type epo:Session }",
              "SELECT ?e WHERE { ?e a epo:Evidence }", "ASK { <https://w3id.org/og-caie/run/measles#mission-1> ?p ?o }"):
        r = run("sparql", q)
        assert r.returncode == 1 and "add --record" in r.stderr and r.stdout == "", (q, r.stdout, r.stderr)
        assert run("sparql", q, "--record").returncode == 0, q
    assert run("sparql", "DESCRIBE epo:Attestation").returncode == 0  # the class itself lives in the vocabulary
    assert run("sparql", "SELECT ?s WHERE { ?s a epo:EpoStep }").returncode == 0  # steps are instances in the vocabulary
    r, d = _json("sparql", "DESCRIBE run:mission-1")
    assert r.returncode == 1 and "add --record" in d["hint"] and d["_ogc"]["command"] == "sparql" and d["candidates"] == []


def test_r2_finding_04_curie_and_iri_forms_resolve_to_the_local_name():
    for cmd in (["record", "run:mission-1"], ["term", "term:probe"], ["define", "term:probe"], ["quote", "term:probe"], ["quote", "epo:scope"],
                ["ruling", "rul:R-16"], ["concern", "rul:C-30"], ["sci", "tr:SCI-07"], ["source", "src:sevocab"], ["shape", "ogc:S0-Population"],
                ["term", "https://w3id.org/og-caie/terms#probe"], ["ruling", "<https://w3id.org/og-caie/rulings#R-16>"],
                ["record", "https://w3id.org/og-caie/run/measles#mission-1"], ["verify", "term:probe"], ["verify", "src:sevocab"],
                ["rulings", "--term", "term:probe"], ["list", "--source", "src:sevocab"], ["check-word", "term:probe"]):
        r = run(*cmd)
        assert r.returncode == 0, (cmd, r.stdout, r.stderr)
    assert run("term", "customer (ISO 9000:2026 3.9.1, of the evaluation)").returncode == 0  # a colon inside a label is not a prefix
    assert run("term", "term:no-such-term").returncode == 1


def test_r2_finding_05_candidates_on_a_miss_are_near_misses_never_the_whole_list():
    r, d = _json("record", "statement-of-work-1")
    assert r.returncode == 1 and "statement-of-work" in d["candidates"]
    r, d = _json("record", "attestation")
    assert d["candidates"][:2] == ["attestation-1", "attestation-2"]
    r, d = _json("record", "atestation-1")
    assert "attestation-1" in d["candidates"]
    r, d = _json("shape", "nonexistent")
    assert r.returncode == 1 and d["candidates"] == []
    r, d = _json("shape", "S3-PlanAproval")
    assert "S3-PlanApproval" in d["candidates"] and len(d["candidates"]) <= 8
    n = len(_json("shapes")[1]["rows"])
    r, d = _json("shape", "s")
    assert 0 < len(d["candidates"]) <= 8 < n
    r, d = _json("source", "sevocb")
    assert d["candidates"] == ["sevocab"]


def test_r2_finding_06_sparql_header_is_re_runnable():
    q = '# the coined terms\nSELECT ?l WHERE {\n  ?t ogc:class "coined" ; skos:prefLabel ?l\n}'
    r = run("sparql", q)
    head = r.stdout.splitlines()[0]
    assert r.returncode == 0 and "# the coined terms\\nSELECT" in head, head
    m = re.fullmatch(r"# ogc sparql (.*) #sha256:([0-9a-f]{12}) @ \S+", head)
    assert m and m.group(2) == hashlib.sha256(q.encode()).hexdigest()[:12]
    again = run("sparql", m.group(1).replace("\\n", "\n"))
    assert again.stdout.splitlines()[1:] == r.stdout.splitlines()[1:] and "(4 rows)" in again.stdout
    assert json.loads(run("sparql", q, "--json").stdout)["_ogc"]["args"] == head[len("# ogc sparql "):].rsplit(" @ ", 1)[0]
    f = ROOT / ".cache" / "r2-finding-06.rq"
    f.parent.mkdir(exist_ok=True)
    f.write_text(q)
    try:
        r = run("sparql", f"@{f}", "--record")
        head = r.stdout.splitlines()[0]
        assert head == f"# ogc sparql @{f} --record #sha256:{hashlib.sha256(q.encode()).hexdigest()[:12]} @ " + head.rsplit(" @ ", 1)[1]
    finally:
        f.unlink()


def test_r2_finding_07_empty_ids_are_usage_errors_everywhere():
    for cmd in ("term", "quote", "define", "find", "check-word", "record", "source", "ruling", "concern", "shape", "view", "sci", "verify"):
        for empty in ("", "  "):
            r = run(cmd, empty)
            assert r.returncode == 2 and r.stdout == "" and r.stderr.startswith("ogc: "), (cmd, empty, r.stdout, r.stderr)
            r, d = _json(cmd, empty)
            assert r.returncode == 2 and d["error"] == "usage" and d["_ogc"]["command"] == cmd and d["candidates"] == [], (cmd, empty)


def test_r2_finding_08_json_usage_errors_are_one_envelope_with_the_real_command():
    cases = [(["term"], "term"), (["term", "probe", "extra"], "term"), (["execute", "--planned", "x"], "execute"), (["term", "probe", "--model"], "term"),
             (["sparql", "@."], "sparql"), (["verify", "--all", "probe"], "verify"), (["bogus-command"], "ogc"), ([], "ogc")]
    for cmd, name in cases:
        r, d = _json(*cmd)
        assert r.returncode == 2 and r.stderr == "", (cmd, r.stderr)
        assert d["_ogc"]["command"] == name and d["_ogc"]["sha"] and d["error"] == "usage" and d["hint"] and d["candidates"] == [], (cmd, d)
        assert set(d) == {"_ogc", "error", "hint", "candidates"}, cmd
    r, d = _json("term", "no-such-term-xyz")
    assert r.returncode == 1 and d["_ogc"]["command"] == "term" and d["_ogc"]["args"] == "no-such-term-xyz" and set(d) == {"_ogc", "error", "hint", "candidates"}


def test_r2_finding_09_doctor_verdict_is_portable():
    r = run("doctor")
    last = r.stdout.rstrip().splitlines()[-1]
    assert last == "VERDICT: PASS (ogc doctor)" and str(ROOT) not in r.stdout
    r, d = _json("doctor")
    assert "sha" not in d and d["_ogc"]["sha"] and d["verdict"] == last


def test_r2_finding_10_execute_verdict_repeats_the_header_args():
    r = run("execute", "--sessions", "2", "--planned", "3", "--mutate", "skip-access")
    head, last = r.stdout.splitlines()[0], r.stdout.rstrip().splitlines()[-1]
    argstr = re.fullmatch(r"# ogc execute (.*) @ \S+", head).group(1)
    assert argstr == "--sessions 2 --planned 3 --mutate skip-access" and last == f"VERDICT: FAIL (ogc execute {argstr})"
    assert run("execute").stdout.rstrip().splitlines()[-1] == "VERDICT: PASS (ogc execute)"


def test_r2_finding_11_execute_json_carries_mutations_only():
    r, d = _json("execute", "--mutate", "skip-access")
    assert "mutation" not in d and d["mutations"] == ["skip-access"]


def test_r2_finding_12_schema_and_shapes_count_the_same_files_and_doctor_parses_them_all():
    n = len(_json("shapes")[1]["rows"])
    assert _json("schema")[1]["counts"]["shapes"] == n and n > 45
    r = run("doctor")
    for f in ("shapes/glossary.shapes.ttl", "shapes/rulings.shapes.ttl", "track/measles-run.ttl", "model/og-caie.model.ttl"):
        assert re.search(rf"^ok\s+{re.escape(f)} \(\d+ triples\)$", r.stdout, re.M), f


def test_r2_finding_13_shape_prints_each_sparql_constraint_with_its_select_body():
    r = run("shape", "S0-Layers")
    assert re.search(r"^\s{4,}SELECT \$this", r.stdout, re.M) and "S0 two layers" in r.stdout
    r, d = _json("shape", "S0-Layers")
    assert d["sparql"] and all(set(c) == {"message", "select"} and "SELECT" in c["select"] and c["message"] for c in d["sparql"])
    assert d["message"] is None and d["closed"] is None


def test_r2_finding_14_citation_is_the_kind_everywhere():
    r, d = _json("quote", "probe")
    assert d["quotes"] and all("holder" not in q and q["citation"] in ("canonical", "seeAlso") for q in d["quotes"])
    r, d = _json("quote", "scope")
    assert d["quotes"] and all("holder" not in q and q["citation"] in ("canonical", "seeAlso") for q in d["quotes"])
    r, d = _json("source", "scipy-2026-bof")
    assert d["citations"] and all("holder" not in c and c["citation"] in ("canonical", "seeAlso", "crosswalk") for c in d["citations"])
    assert "[crosswalk]" in run("source", "scipy-2026-bof").stdout and "[canonical]" in run("source", "sevocab").stdout
    rows = _json("verify", "--all")[1]["rows"]
    assert {x["citation"] for x in rows} == {"canonical", "seeAlso", "crosswalk"}


def test_r2_finding_15_record_item_json_keys_and_nulls():
    r, d = _json("record", "mission-1")
    assert {"triples", "referenced_by"} <= set(d) and "out" not in d and "in" not in d and d["who"] and d["when"]
    assert any(t["predicate"] == "epo:regards" for t in d["triples"]) and any(t["predicate"] == "epo:underMission" for t in d["referenced_by"])
    assert _json("record", "turn-1")[1]["who"] is None and _json("record", "annie")[1]["when"] is None
    rows = _json("record")[1]["rows"]
    assert not any(x["who"] == [] or x["when"] == "" for x in rows) and any(x["who"] is None for x in rows)
    assert "None" not in run("record").stdout and "None" not in run("record", "annie").stdout


def test_r2_finding_16_model_and_record_flags_only_where_they_matter():
    for cmd in (["term", "probe", "--model"], ["--record", "term", "probe"], ["list", "--record"], ["schema", "--model"], ["doctor", "--model"], ["shapes", "--record"]):
        r = run(*cmd)
        assert r.returncode == 2 and "--model and --record" in r.stderr and "sparql, record, execute, view and views" in r.stderr, (cmd, r.stderr)
    for cmd in (["--model", "sparql", "ASK { ?s ?p ?o }"], ["record", "--record"], ["execute", "--model"], ["view", "nesting", "--model"], ["views", "--model"], ["sparql", "ASK { ?s ?p ?o }", "--record"]):
        assert run(*cmd).returncode == 0, cmd  # `views --record` left this list in round three (L2): views reads the model graph, not the record
    r, d = _json("term", "probe", "--record")
    assert r.returncode == 2 and d["_ogc"]["command"] == "term"


def test_r2_finding_17_contradictory_filters_are_usage_errors():
    for cmd in (["crosswalk", "--popper", "--class", "refined"], ["crosswalk", "--popper", "--source", "sevocab"], ["concerns", "--open", "--status", "ruled"], ["sources", "--uncited", "--rank", "1"]):
        r = run(*cmd)
        assert r.returncode == 2 and "these filters exclude each other" in r.stderr, (cmd, r.stderr)
    r = run("rulings", "--term", "probe", "--grep", "zzzz")
    assert r.returncode == 0 and "(none)" in r.stdout
    assert run("concerns", "--open", "--status", "open").returncode == 0 and run("sources", "--uncited", "--rank", "4").returncode == 0


def test_r2_finding_18_the_popper_row_count_is_stated_correctly():
    n = len(_json("crosswalk", "--popper")[1]["rows"])
    assert f"the {NUMBER_WORDS[n]} Popper rows" in run("crosswalk", "--help").stdout
    skill = SKILL.read_text()
    assert f"{NUMBER_WORDS[n]} Popperian elements" in skill and "six Popper" not in skill


def test_r2_finding_19_id_hints_give_examples_of_the_right_kind():
    r = run("concern", "C-999").stdout
    assert "C-24" in r and "c-024" in r and "R-16" not in r and "r-016" not in r
    r = run("sci", "SCI-99").stdout
    assert "SCI-07" in r and "sci-007" in r and "R-16" not in r
    r = run("ruling", "R-999").stdout
    assert "R-16" in r and "C-24" not in r


def test_r2_finding_21_coined_terms_say_coined_by():
    r = run("term", "DSO").stdout
    assert "coined by:" in r and not re.search(r"^canonical:\s*$", r, re.M)
    r = run("define", "DSO").stdout
    assert "coined by:" in r and "canonical: ," not in r
    r = run("check-word", "OG-CAIE").stdout
    assert "coined by:" in r and not re.search(r"canonical:\s*$", r, re.M)
    assert "(coined)" in run("list", "--class", "coined").stdout and "(coined)" in run("crosswalk", "--class", "coined").stdout
    assert all(x["source"] == "(coined)" for x in _json("list", "--class", "coined")[1]["rows"])
    assert not any(x["source"] == "(coined)" for x in _json("list", "--class", "adopted")[1]["rows"])


def test_r2_finding_22_crosswalk_citations_are_listed_by_verify_all_with_state_authors():
    r, d = _json("verify", "--all")
    rows = [x for x in d["rows"] if x["citation"] == "crosswalk"]
    n = len(_json("crosswalk", "--popper")[1]["rows"])
    assert len(rows) == n and {x["state"] for x in rows} == {"authors"} and {x["status"] for x in rows} == {"authors"} and d["summary"]["states"]["authors"] == n
    assert len(_json("verify", "--all", "--state", "authors")[1]["rows"]) == n and len(_json("verify", "--all", "--status", "authors")[1]["rows"]) == n
    r, d = _json("verify", "--all", "--status", "pending")
    assert r.returncode == 0 and d["rows"] == [] and d["summary"]["citations"] == 0
    assert run("verify", "--all", "--status", "pending").stdout.rstrip().endswith("(0 citations)")
    assert run("verify", "--all", "--state", "bogus").returncode == 1 and run("verify", "--all", "--status", "bogus").returncode == 1
    assert run("verify", "probe", "--status", "machine").returncode == 0
    skill = SKILL.read_text()
    assert "authors" in skill and "--status pending" in skill


def test_r2_finding_23_json_without_a_subcommand_is_a_json_usage_error():
    r, d = _json()
    assert r.returncode == 2 and r.stderr == "" and d["error"] == "usage" and d["_ogc"]["command"] == "ogc" and d["hint"]
    r = run()
    assert r.returncode == 2 and "usage" in r.stderr and r.stdout == ""


def test_r2_skill_carries_the_new_recipes_and_keeps_the_file_names_out_of_the_triggers():
    skill = SKILL.read_text()
    front, body = skill.split("\n---\n", 1)
    assert ".ttl" not in front
    assert "Never open these; they are what ogc reads" in body
    for needle in ("verify --all --status pending", "sysml:declaredName", "sysml:owner", "sysml:specializes", "elmt:", "no `rdfs:label`", "run:", "\\n"):
        assert needle in body, needle


def test_r3_finding_h1_offset_without_limit_returns_rows_from_the_offset():
    """Round three, machine user H1: OFFSET with no LIMIT and no ORDER BY crashed in the slice helper."""
    all_rows = run("sparql", "SELECT ?s WHERE { ?s a ogc:Ruling }")
    assert all_rows.returncode == 0
    r = run("sparql", "SELECT ?s WHERE { ?s a ogc:Ruling } OFFSET 47")
    assert r.returncode == 0 and "Traceback" not in r.stderr, r.stderr[-300:]
    assert "(2 rows)" in r.stdout, r.stdout[-200:]
    j = run("sparql", "SELECT ?s WHERE { ?s a ogc:Ruling } OFFSET 47", "--json")
    assert j.returncode == 0 and "Traceback" not in j.stderr


# ---------------------------------------------------------------- the third machine-user review (2026-09-06), one test each

def test_r3_finding_m1_model_query_without_the_flag_is_refused_with_a_hint():
    for q in ("SELECT ?s WHERE { ?s a sysml:PartDefinition }", "SELECT ?n WHERE { ?p sysml:declaredName ?n }", "SELECT ?s WHERE { ?s ?p ?o FILTER(STRSTARTS(STR(?s), 'https://w3id.org/og-caie/model#')) }",
              "DESCRIBE elmt:abc", "DESCRIBE ogm:assembly", "ASK { ?s a <https://www.omg.org/spec/SysML#PartDefinition> }"):
        r = run("sparql", q)
        assert r.returncode == 1 and "names the model graph" in r.stderr and "add --model" in r.stderr and r.stdout == "", (q, r.stdout, r.stderr)
        assert run("sparql", q, "--model").returncode == 0, q
    r, d = _json("sparql", "SELECT ?s WHERE { ?s a sysml:PartDefinition }")
    assert r.returncode == 1 and "sysml:PartDefinition" in d["hint"] and d["_ogc"]["command"] == "sparql"
    assert run("sparql", "SELECT ?s WHERE { ?s a epo:EpoStep }").returncode == 0  # the vocabulary answers this one


def test_r3_finding_m2_curie_prefixes_are_case_insensitive():
    for cmd in (["term", "TERM:PROBE"], ["term", "Term:probe"], ["define", "TERM:probe"], ["record", "RUN:MISSION-1"], ["ruling", "RUL:R-16"], ["concern", "Rul:C-30"],
                ["sci", "TR:SCI-07"], ["source", "SRC:sevocab"], ["shape", "OGC:S0-Population"], ["quote", "EPO:scope"], ["verify", "TERM:probe"], ["check-word", "TERM:probe"]):
        r = run(*cmd)
        assert r.returncode == 0, (cmd, r.stdout, r.stderr)
    assert "ids are case-insensitive, the prefix too" in " ".join(run("term", "--help").stdout.split())


def test_r3_finding_m3_r49_derives_the_renamed_headwords_and_ruling_refs_carry_labels():
    for term in ("authorized representative", "test item provider"):
        r, d = _json("term", term)
        ids = [x["id"] for x in d["rulings"]]
        assert "R-49" in ids, (term, ids)
        assert all(x["label"] for x in d["rulings"]), d["rulings"]
        assert "R-49 (" in run("term", term).stdout
    r, d = _json("ruling", "R-49")
    assert "authorized representative" in d["derived_terms"] and "test item provider" in d["derived_terms"]
    r, d = _json("term", "statement of work")
    assert d["rulings"] == [{"id": "R-40", "label": "the sponsor's decision to interview or represent each affected population had no item of its own"}]


def test_r3_finding_m4_a_curie_in_the_wrong_namespace_names_the_right_reader():
    cases = [(["term", "rul:R-16"], "ogc ruling R-16"), (["term", "rul:C-26"], "ogc concern C-26"), (["define", "epo:StakeholderRepresentation"], "ogc epo StakeholderRepresentation"),
             (["record", "term:probe"], "ogc term probe"), (["term", "run:mission-1"], "ogc record mission-1"), (["ruling", "term:probe"], "ogc term probe"),
             (["sci", "src:sevocab"], "ogc source sevocab"), (["source", "tr:SCI-07"], "ogc sci SCI-07"), (["shape", "epo:S3-PlanApproval"], "under ogc:, not epo:; try `ogc shape S3-PlanApproval`"),
             (["record", "ogc:S0-Layers"], "ogc shape S0-Layers"), (["term", "xw:falsifiability"], "ogc crosswalk --popper"), (["term", "elmt:abc"], "--model sparql"),
             (["epo", "term:probe"], "ogc term probe"), (["find", "rul:R-16"], "ogc ruling R-16"), (["check-word", "run:mission-1"], "ogc record mission-1")]
    for cmd, reader in cases:
        r = run(*cmd)
        assert r.returncode == 1 and reader in r.stdout and "candidate:" not in r.stdout, (cmd, r.stdout, r.stderr)
        r, d = _json(*cmd)
        assert r.returncode == 1 and reader in d["hint"] and d["candidates"] == [], cmd
    assert "rul: is a ruling or concern" in run("term", "rul:R-16").stdout
    assert run("term", "https://w3id.org/og-caie/rulings#R-16").returncode == 1 and "ogc ruling R-16" in run("term", "https://w3id.org/og-caie/rulings#R-16").stdout
    assert run("shape", "ogc:S3-PlanApproval").returncode == 0 and run("quote", "epo:scope").returncode == 0 and run("verify", "src:sevocab").returncode == 0


def test_r3_finding_m5_epo_reader_and_find_indexes_the_epo_labels():
    sys.path.insert(0, str(ROOT))
    from ogc import cli
    assert "epo" in cli.build_parser().command_names and "epo" in run("--help").stdout
    for name in ("StakeholderRepresentation", "epo:EngagementDecision", "ReportApproval", "conformanceverdict", "AuthorizedRepresentativeRole", "https://w3id.org/og-caie/epo#Report", "accountExecutiveRole"):
        r = run("epo", name)
        assert r.returncode == 0 and r.stdout.startswith("# ogc epo "), (name, r.stdout, r.stderr)
    r, d = _json("epo", "StakeholderRepresentation")
    assert d["id"] == "epo:StakeholderRepresentation" and d["kind"] == "class" and d["label"].startswith("stakeholder representation")
    assert d["superclasses"] == ["prov:Entity"] and d["pinned_at"]["id"] == "epo:evaluation" and d["pinned_at"]["label"]
    assert d["terms"] == [{"local": "stakeholder", "headword": "stakeholder"}]
    r, d = _json("epo", "AuthorizedRepresentativeRole")
    assert d["kind"] == "class" and d["terms"] == [{"local": "account-executive", "headword": "authorized representative"}]
    assert set(d["disjoint_with"]) == {"epo:DomainExpertRole", "epo:EvaluationOperatorRole"} and "epo:accountExecutiveRole" in d["instances"]
    assert d["superclasses"] == ["epo:ActorRole"] and d["pinned_at"] is None
    r, d = _json("epo", "accountExecutiveRole")
    assert d["kind"] == "role" and d["types"] == ["epo:AuthorizedRepresentativeRole"]
    r, d = _json("epo", "ReportApproval")
    assert d["terms"] == [] and d["comment"] and any(s["id"] == "S7-ReportApproval" for s in d["shapes"]) and any(s["id"] == "S8-Delivery" for s in d["shapes"])
    assert all({"id", "file", "where"} <= set(s) for s in d["shapes"])
    out = run("epo", "ConformanceVerdict").stdout
    assert "pinned at: epo:evaluation" in out and "term: conformance (conformance)" in out and "superclasses: earl:Assertion, prov:Activity" in out and "shapes mentioning it" in out
    r = run("epo", "scope")
    assert r.returncode == 1 and "ogc quote scope" in r.stdout
    r, d = _json("epo", "StakeholderRepresentatio")
    assert r.returncode == 1 and "epo:StakeholderRepresentation" in d["candidates"]
    assert run("epo", "").returncode == 2 and run("epo", "x", "--record").returncode == 2
    rows = _json("find", "report approval")[1]["rows"]
    hit = next(x for x in rows if x["via"] == "epo:ReportApproval")
    assert hit["match"] == "exact" and hit["class"] == "epo class" and hit["local"] == "epo:ReportApproval"
    out = run("find", "report approval").stdout
    assert "epo:ReportApproval" in out and "ogc epo" in out
    rows = _json("find", "authorized representative")[1]["rows"]
    assert any(x["via"] == "epo:accountExecutiveRole" and x["class"] == "epo role" for x in rows) and rows[0]["via"] != "epo:accountExecutiveRole"  # the term ranks first
    assert any(x["via"] == "epo:Probe" and x["match"] == "exact" for x in _json("find", "probe", "--no-quotes")[1]["rows"])  # labels only still indexes the EPO


def test_r3_finding_m7_record_lists_its_own_entity_first():
    rows = _json("record")[1]["rows"]
    rg = load("track/measles-run.ttl")
    subjects = {str(s).rsplit("#", 1)[-1] for s in rg.subjects() if str(s).startswith("https://w3id.org/og-caie/run/measles#")}
    assert {x["item"] for x in rows} == subjects
    assert rows[0]["item"] == "record" and rows[0]["group"] == "record" and rows[0]["label"].startswith("evaluation record")
    out = run("record").stdout.splitlines()
    assert out[1] == "## the record (1)" and out.index("## the record (1)") < next(i for i, l in enumerate(out) if l.startswith("## items by step"))
    assert run("record", "record").returncode == 0 and "Synthetic case" in run("record", "record").stdout


def test_r3_finding_l1_a_record_name_in_a_comment_is_not_a_reference():
    for q in ("# run: in a comment\nSELECT ?s WHERE { ?s a ogc:Ruling } LIMIT 1", "SELECT ?s WHERE { ?s a ogc:Ruling } # see run:mission-1\nLIMIT 1", "# ?a a epo:Attestation\nSELECT ?s WHERE { ?s a ogc:Ruling } LIMIT 1",
              "# sysml:PartDefinition\nSELECT ?s WHERE { ?s a ogc:Ruling } LIMIT 1"):
        r = run("sparql", q)
        assert r.returncode == 0 and "(1 rows)" in r.stdout, (q, r.stderr)
    r = run("sparql", 'SELECT ?s WHERE { ?s rdfs:label "#" } # run:\nLIMIT 1')
    assert r.returncode == 0
    assert run("sparql", "SELECT ?s WHERE { ?s ?p <https://w3id.org/og-caie/run/measles#mission-1> } # a real reference").returncode == 1


def test_r3_finding_l2_flags_only_where_they_change_the_answer():
    for cmd in (["view", "contracting", "--record"], ["views", "--record"], ["execute", "--record"], ["record", "--model"], ["--record", "views"]):
        r = run(*cmd)
        assert r.returncode == 2 and r.stdout == "" and "--model" in r.stderr and "--record" in r.stderr, (cmd, r.stdout, r.stderr)
        r, d = _json(*cmd)
        assert r.returncode == 2 and d["error"] == "usage"
    for cmd in (["record", "--record"], ["execute", "--model"], ["view", "nesting", "--model"], ["views", "--model"], ["sparql", "ASK { ?s ?p ?o }", "--record", "--model"]):
        assert run(*cmd).returncode == 0, cmd
    skill = SKILL.read_text()
    assert "`--model` where the model graph is read" in skill and "`--record` where the record is read" in skill


def test_r3_finding_l3_a_mutation_named_twice_is_a_usage_error():
    r = run("execute", "--mutate", "skip-approval", "--mutate", "skip-approval")
    assert r.returncode == 2 and "mutation named twice: skip-approval" in r.stderr and r.stdout == ""
    r = run("execute", "--mutate", "skip-approval", "--mutate", "Skip-Approval")
    assert r.returncode == 2 and "mutation named twice: skip-approval" in r.stderr
    r, d = _json("execute", "--mutate", "skip-access", "--mutate", "skip-access")
    assert r.returncode == 2 and d["error"] == "usage" and "skip-access" in d["hint"]
    assert run("execute", "--mutate", "skip-approval", "--mutate", "skip-access").returncode == 1


def test_r3_finding_l4_the_skill_names_every_mutation_the_executor_has():
    sys.path.insert(0, str(ROOT))
    from ogc import executor
    skill = SKILL.read_text()
    n = len(executor.MUTATIONS)
    assert f"The {NUMBER_WORDS[n]} mutations of `execute`" in skill and "eight mutations" not in skill
    for m in executor.MUTATIONS:
        assert f"`{m}`" in skill, m
    help_ = run("execute", "--help").stdout
    for m in executor.MUTATIONS:
        assert m in help_, m


def test_r3_finding_l5_a_stray_argument_is_kept_apart_from_the_query():
    q = "SELECT ?s WHERE { ?s a ogc:Ruling }"
    r, d = _json("sparql", q, "extra")
    assert r.returncode == 2 and d["error"] == "usage" and d["_ogc"]["args"] == q and "extra" in d["hint"] and "extra" not in d["_ogc"]["args"]
    r, d = _json("term", "probe", "probe")
    assert r.returncode == 2 and d["_ogc"]["args"] == "probe"
    r, d = _json("term", "probe", "--bogus")
    assert r.returncode == 2 and d["_ogc"]["args"] == "probe" and "--bogus" in d["hint"]


def test_r3_finding_l6_a_bare_at_is_a_usage_error_not_the_working_directory():
    for f in ("@", "@ ", "@  "):
        r = run("sparql", f)
        assert r.returncode == 2 and "no path after @" in r.stderr and "directory" not in r.stderr, (f, r.stderr)
    r, d = _json("sparql", "@")
    assert r.returncode == 2 and "no path after @" in d["hint"]
    r = run("sparql", "@.")
    assert r.returncode == 2 and "query file is a directory" in r.stderr


def test_r3_finding_l7_an_empty_root_is_a_usage_error():
    for cmd in (["--root", "", "term", "probe"], ["term", "probe", "--root", ""], ["--root=", "term", "probe"], ["--root", "  ", "schema"]):
        r = run(*cmd)
        assert r.returncode == 2 and "--root" in r.stderr and r.stdout == "", (cmd, r.stdout, r.stderr)
        r, d = _json(*cmd)
        assert r.returncode == 2 and d["error"] == "usage" and "--root" in d["hint"], cmd
    assert run("--root", "/nonexistent/path", "term", "probe").returncode == 2


def test_r3_finding_l8_the_header_is_the_canonical_form_of_the_invocation():
    a, b = run("sparql", "ASK { ?s ?p ?o }", "--record", "--model"), run("--model", "--record", "sparql", "ASK { ?s ?p ?o }")
    assert a.stdout.splitlines()[0] == b.stdout.splitlines()[0] and "--model --record" in a.stdout.splitlines()[0]
    help_ = " ".join(run("--help").stdout.split())
    assert "canonical form" in help_ and "canonical form" in " ".join(SKILL.read_text().split())


def test_r3_finding_l9_who_and_when_derive_through_the_generating_activity():
    r, d = _json("record", "report")
    assert d["who"] == ["report assembler (queries/coverage.rq)"] and d["when"] == "2026-08-12" and d["via"] == "coverage-computation"
    out = run("record", "report").stdout
    assert "who: report assembler (queries/coverage.rq)   when: 2026-08-12   (via coverage-computation)" in out
    rows = {x["item"]: x for x in _json("record")[1]["rows"]}
    assert rows["probe-1"]["who"] == ["test driver"] and rows["probe-1"]["when"] == "2026-08-03" and rows["probe-1"]["via"] == "derivation-1"
    assert rows["report"]["who"] == ["report assembler (queries/coverage.rq)"] and rows["report"]["via"] == "coverage-computation"
    assert rows["attestation-1"]["via"] is None and rows["test-plan"]["via"] is None  # attributed directly
    assert rows["turn-1"]["who"] is None and rows["annie"]["when"] is None  # nothing to derive from
    listing = run("record").stdout
    assert re.search(r"^probe-1\s+Probe\s+test driver \(via derivation-1\)\s+2026-08-03$", listing, re.M), listing
    assert re.search(r"^report\s+Report\s+report assembler \(queries/coverage.rq\) \(via coverage-computation\)\s+2026-08-12$", listing, re.M)


def test_r3_finding_l10_long_inputs_are_truncated_in_the_error_line():
    long = "a" * 5000
    r = run("term", long)
    head, err = r.stdout.splitlines()[0], r.stdout.splitlines()[1]
    assert r.returncode == 1 and long in head and long not in err and "..." in err and len(err) < 300, err
    r, d = _json("term", long)
    assert d["_ogc"]["args"] == long and long not in d["error"] and "..." in d["error"]
    r = run("record", long)
    assert long not in r.stdout.splitlines()[1] and "..." in r.stdout.splitlines()[1]
    r = run("term", "probe")
    assert "..." not in r.stdout.splitlines()[0]


def test_r3_skill_corrections():
    body = " ".join(SKILL.read_text().split("\n---\n", 1)[1].split())  # whitespace collapsed: the needles may straddle a line wrap
    for needle in ("`ogc epo", "term labels and quotes and EPO class labels", "nothing else", "rulings/sheets/", "provenance the tool does not read", "sheet 10-40", "works cited",
                   "`mutations`, `params`, `conforms`, `fired`, `missing`, `coverage`", "`term`, `definition`, `class`, `canonical`, `coined_by`, `status`, `resolved`",
                   "`group`", "`via`", "`triples`, `referenced_by`", "`name`, `title`, `focus`, `leaves_out`, `mermaid`", "## the record", "## items by step", "## items without a step", "## parties and machines",
                   "canonical form"):
        assert needle in body, needle
