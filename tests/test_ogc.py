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
    assert not any(x["item"] == "record" for x in rows)  # the record's own entity is not one of its items
    who = next(x for x in rows if x["item"] == "attestation-1")
    assert who["who"] == ["Annie (domain expert)"] and who["when"] == "2026-08-11"
    assert any(x["item"] == "annie" and x["group"] == "party" for x in rows)


def test_record_item_prints_its_label_and_step():
    r = run("record", "mission-1")
    assert r.returncode == 0 and "C1 need" in r.stdout and "protect the health of county residents" in r.stdout
    d = json.loads(run("record", "mission-1", "--json").stdout)
    assert d["item"] == "mission-1" and d["step"] == "C1 need" and d["class"] == "Mission"
    assert any(t["predicate"] == "epo:regards" and t["object"] == "run:commuters" and t["label"].startswith("commuters") for t in d["out"])
    assert any(t["predicate"] == "epo:underMission" and t["subject"] == "run:need-1" for t in d["in"])
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
