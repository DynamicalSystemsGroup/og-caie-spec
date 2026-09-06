"""The `ogc` navigation tool (ruling R-29): every command is deterministic,
carries the invocation and commit in its first line, exits 0 / 1 / 2 as
documented, resolves every glossary label to one term, refuses to write,
and its doctor passes on the committed graphs."""
import json
import subprocess
import sys

import pytest
from rdflib import RDF

from conftest import OGC, ROOT, load

SKOS = "http://www.w3.org/2004/02/skos/core#"
COMMANDS = [
    ["schema"], ["find", "probe"], ["term", "probe"], ["define", "conformance"], ["quote", "attestation"],
    ["list", "--class", "coined"], ["source", "sevocab"], ["sources"], ["ruling", "r-16"], ["rulings", "--grep", "conformance"],
    ["concern", "c-24"], ["concerns", "--open"], ["sci"], ["sci", "SCI-11"], ["steps"], ["crosswalk", "--class", "refined"], ["crosswalk", "--popper"],
    ["check-word", "adequacy", "evidence", "probe"], ["verify", "conformance"], ["verify", "sevocab"],
    ["sparql", 'SELECT ?l WHERE { ?t a skos:Concept ; ogc:class "coined" ; skos:prefLabel ?l }'],
]


def run(*args):
    return subprocess.run([sys.executable, "-m", "ogc", "--no-cache", *args], cwd=ROOT, capture_output=True, text=True)


def test_every_command_is_deterministic_and_exits_zero():
    for cmd in COMMANDS:
        a, b = run(*cmd), run(*cmd)
        assert a.returncode == 0, (cmd, a.stdout, a.stderr)
        assert a.stdout == b.stdout, cmd
        assert a.stdout.startswith("# ogc "), cmd


def test_json_twin_parses():
    for cmd in COMMANDS:
        r = run(*cmd, "--json")
        assert r.returncode == 0, (cmd, r.stderr)
        json.loads(r.stdout)


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
    d = json.loads(r.stdout)[0]
    assert d["retired"] and not d["registered"]
    r = run("check-word", "system under test", "--json")
    d = json.loads(r.stdout)[0]
    assert d["registered"] and d["matched_as"] == "alt" and d["term"] == "test item"
    assert "{term}`system under test <test item>`" in d["advice"]


def test_verify_agrees_with_the_citation_tests():
    r = run("verify", "--all", "--json")
    rows = json.loads(r.stdout)
    states = {x["state"] for x in rows}
    assert "NOT FOUND" not in states, [x for x in rows if x["state"] == "NOT FOUND"]
    assert sum(1 for x in rows if x["state"] == "pending") == 7  # the 17000 step quotes on sheet 04


def test_doctor_passes():
    r = run("doctor")
    assert r.returncode == 0, r.stdout
    assert r.stdout.rstrip().splitlines()[-1].startswith("VERDICT: PASS")
