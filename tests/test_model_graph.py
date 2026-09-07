"""The canonical model graph (ruling R-22): the SysML source validates
strictly, its pruned RDF rendering regenerates byte-identically, stays
within the parsimony budget with a manifest that matches it, uses exactly
the mapped terms, conforms to the wiring shapes M1 to M5, and each model
counterexample fails on the shape it is built to violate."""
import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest
from pyshacl import validate
from rdflib import RDF, Graph, Namespace

from conftest import ROOT, load

sys.path.insert(0, str(ROOT / "scripts"))
from prune_model import OGM, SYS, SYSX, TRIPLE_BUDGET, build  # noqa: E402

SYSML = ROOT / "toolchain" / "bin" / "sysml"
MODEL = ROOT / "model" / "og-caie.sysml"
GRAPH = ROOT / "model" / "og-caie.model.ttl"
MANIFEST = ROOT / "model" / "model_manifest.json"
TERM_MAP = ROOT / "model" / "sysml_term_map.csv"
SH = Namespace("http://www.w3.org/ns/shacl#")
COUNTEREXAMPLES = {
    "unwired-port": "M2-Part",
    "expert-administers-tests": "M5-PortsBelongToRoles",
    "missing-accountable": "M1-Parties",
    "no-obligation": "M1-Obligation",
}


def run(*args):
    return subprocess.run([str(SYSML), *args], cwd=ROOT, capture_output=True, text=True)


@pytest.fixture(scope="module", autouse=True)
def toolchain():
    if not SYSML.exists():
        r = subprocess.run(["bash", "toolchain/get-sysml.sh"], cwd=ROOT, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr


@pytest.fixture(scope="module")
def graph():
    return load("model/og-caie.model.ttl")


@pytest.fixture(scope="module")
def shapes():
    return load("shapes/model.shapes.ttl")


def test_model_and_counterexamples_validate_strictly():
    for f in [MODEL, *sorted((ROOT / "counterexamples" / "model").glob("*.sysml"))]:
        r = run(str(f), "-validate", "-strict")
        assert r.returncode == 0, f.name + "\n" + r.stdout + r.stderr


def test_model_graph_regenerates_byte_identically(tmp_path):
    out, manifest = tmp_path / "model.ttl", tmp_path / "manifest.json"
    build(MODEL, out, manifest)
    assert out.read_bytes() == GRAPH.read_bytes(), "model/og-caie.model.ttl is stale: run scripts/prune_model.py"
    fresh, committed = json.loads(manifest.read_text()), json.loads(MANIFEST.read_text())
    fresh["artifact"]["path"] = committed["artifact"]["path"]
    assert fresh == committed, "model/model_manifest.json is stale"


def test_model_graph_within_budget_and_manifest_matches(graph):
    m = json.loads(MANIFEST.read_text())
    assert len(graph) <= TRIPLE_BUDGET, f"{len(graph)} > {TRIPLE_BUDGET}: bump TRIPLE_BUDGET in scripts/prune_model.py with a rationale"
    assert m["artifact"]["triples"] == len(graph)
    assert m["triple_budget"]["value"] == TRIPLE_BUDGET and m["triple_budget"]["rationale"]
    assert m["raw"]["triples"] > len(graph)


def test_terms_used_are_exactly_the_term_map(graph):
    with TERM_MAP.open() as f:
        rows = list(csv.DictReader(f))
    ns = {"omg": SYS, "opensysml": SYSX, "derived": OGM}
    mapped = {ns[r["source"]][r["term"]] for r in rows}
    used = {t for _, t in graph.subject_objects(RDF.type)} | (set(graph.predicates()) - {RDF.type})
    assert used <= mapped, {str(u) for u in used - mapped}
    assert mapped <= used, {str(u) for u in mapped - used}


def test_model_graph_conforms_to_wiring_shapes(graph, shapes):
    ok, _, report = validate(graph, shacl_graph=shapes, advanced=True)
    assert ok, report


def test_model_realizes_the_epo(graph):
    """Sheet 10-33: the model's join to the EPO is explicit. Every EPO class
    or step whose local name is a model item def or step name carries
    ogm:realizes from that element; every item definition realizes at most
    one class; a class realized by no item kind is one the record derives
    no step for."""
    epo = load("vocabulary/epo.ttl")
    OWL_CLASS = Namespace("http://www.w3.org/2002/07/owl#").Class
    EPO = Namespace("https://w3id.org/og-caie/epo#")
    classes = {str(c).rsplit("#", 1)[-1]: c for c in epo.subjects(RDF.type, OWL_CLASS) if str(c).startswith(str(EPO))}
    steps = {str(s).rsplit("#", 1)[-1]: s for t in (EPO.EpoStep, EPO.ContractingStep) for s in epo.subjects(RDF.type, t)}
    realized = dict(graph.subject_objects(OGM.realizes))
    for d in graph.subjects(RDF.type, SYS.ItemDefinition):
        n = str(graph.value(d, SYS.declaredName))
        if n in classes:
            assert realized.get(d) == classes[n], n
        assert len(list(graph.objects(d, OGM.realizes))) <= 1, n
    for u in graph.subjects(RDF.type, SYS.ActionUsage):
        n = str(graph.value(u, SYS.declaredName))
        if n in steps and (graph.value(u, SYS.owner), RDF.type, SYS.ActionDefinition) in graph:
            assert realized.get(u) == steps[n], n
    assert len(realized) == 43  # 30 item kinds and 13 steps (the perform usage and the two nested actions realize nothing)


@pytest.mark.parametrize("name,shape", sorted(COUNTEREXAMPLES.items()))
def test_model_counterexample_fails_on_its_shape(name, shape, shapes, tmp_path):
    g = build(ROOT / "counterexamples" / "model" / f"{name}.sysml", tmp_path / f"{name}.ttl", None)
    ok, rg, report = validate(g, shacl_graph=shapes, advanced=True)
    assert not ok, f"{name} conforms but must not"
    fired = {str(s).rsplit("/", 1)[-1] for s in rg.objects(None, SH.sourceShape)}
    assert shape in fired, f"{name}: expected {shape}, fired {sorted(fired)}\n{report}"
