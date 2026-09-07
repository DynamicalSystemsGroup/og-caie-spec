"""Shared code for the "Checked" notebooks.

Each chapter page of the site closes its "Checked" block with a link to a
notebook that runs the checks the block claims. The notebooks stay short:
they name the shapes and the counterexamples and call the functions here.
Everything printed is produced by running the code; nothing is typed in.

The rules for what is printed: shape names sorted, focus nodes written as
prefixed names, messages taken from the shapes, no paths, no timestamps,
so that the committed outputs equal a fresh execution byte for byte (the
gate checks that).
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from pyshacl import validate
from rdflib import RDF, BNode, Graph, Namespace, URIRef

ROOT = Path(__file__).resolve().parents[1]
SH = Namespace("http://www.w3.org/ns/shacl#")
OGC = Namespace("https://w3id.org/og-caie/")  # shapes are named ogc:S0-Parties, ogc:M1-Parties, ...

# Every claim a notebook makes is registered here after its assert held;
# verdict() prints the count, so the reader sees how many claims ran.
_PASSED: list[str] = []


# ------------------------------------------------------------------ graphs

def load(*paths: str) -> Graph:
    """Parse one or more repository files (paths relative to the root) into one graph."""
    g = Graph()
    for p in paths:
        g.parse(ROOT / p)
    return g


def record() -> Graph:
    """The measles evaluation (track/measles-evaluation.ttl) with the EPO
    vocabulary and the model graph, exactly as tests/test_shacl.py loads it:
    one default graph, since the shapes derive an item's step through the
    model graph and anchor every global rule on the record (sheets 10-31,
    10-33)."""
    return load("vocabulary/epo.ttl", "model/og-caie.model.ttl", "track/measles-evaluation.ttl")


def counterexample(name: str) -> Graph:
    """One RDF counterexample from counterexamples/ (the record with one change), with the EPO vocabulary and the model graph."""
    return load("vocabulary/epo.ttl", "model/og-caie.model.ttl", f"counterexamples/{name}")


def model_graph() -> Graph:
    """The canonical model graph, the pruned RDF rendering of model/og-caie.sysml (R-22)."""
    return load("model/og-caie.model.ttl")


def toolchain() -> Path:
    """The pinned OpenSysML binary (toolchain/bin/sysml), fetched and
    digest-verified by toolchain/get-sysml.sh if absent."""
    binary = ROOT / "toolchain" / "bin" / "sysml"
    if not binary.exists():
        r = subprocess.run(["bash", "toolchain/get-sysml.sh"], cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError("the pinned sysml toolchain could not be fetched:\n" + r.stderr)
    return binary


def model_counterexample(name: str) -> Graph:
    """Build a model counterexample from its SysML source through the same
    pipeline that produces the canonical graph (scripts/prune_model.py's
    build: convert with the pinned OpenSysML, prune to the term map), as
    tests/test_model_graph.py does. The pinned toolchain is fetched if absent."""
    toolchain()
    sys.path.insert(0, str(ROOT / "scripts"))
    from prune_model import build  # noqa: E402

    source = ROOT / "counterexamples" / "model" / name
    with tempfile.TemporaryDirectory() as tmp:
        return build(source, Path(tmp) / (source.stem + ".ttl"), None)


# ------------------------------------------------------------------ shapes

def shapes(path: str, names: list[str]) -> Graph:
    """A shapes graph holding exactly the named shapes from one shapes file.

    Each shape is copied with its blank-node closure (property shapes and
    SPARQL constraints). A name that is not a sh:NodeShape in the file is
    an error: a chapter must not claim a shape that does not exist."""
    full = load(path)
    sub = Graph()
    for prefix, ns in full.namespaces():
        sub.bind(prefix, ns)
    for name in names:
        node = OGC[name]
        if (node, RDF.type, SH.NodeShape) not in full:
            raise KeyError(f"{name} is not a sh:NodeShape in {path}")
        _copy_closure(full, sub, node)
    return sub


def _copy_closure(src: Graph, dst: Graph, node) -> None:
    for p, o in src.predicate_objects(node):
        dst.add((node, p, o))
        if isinstance(o, BNode):
            _copy_closure(src, dst, o)


def _name(term) -> str:
    return str(term).rsplit("/", 1)[-1]


def _qname(g: Graph, term) -> str:
    """A prefixed name where the graph binds one, else the full term."""
    if isinstance(term, URIRef):
        try:
            return g.namespace_manager.normalizeUri(term)
        except Exception:  # an unbound namespace
            return str(term)
    return str(term)


def run(data: Graph, shapes_graph: Graph) -> tuple[bool, dict[str, list[tuple[str, str]]]]:
    """Validate data against the shapes graph, as the test suite does
    (advanced=True, no inference). Returns (conforms, fired) where fired maps
    each shape that produced a result to its sorted (focus node, message) pairs."""
    conforms, results, _ = validate(data, shacl_graph=shapes_graph, advanced=True)
    fired: dict[str, set[tuple[str, str]]] = {}
    for r in results.subjects(RDF.type, SH.ValidationResult):
        source = results.value(r, SH.sourceShape)
        if isinstance(source, BNode):  # a property shape: name the node shape that owns it, as the tests do
            source = next((ns for ns in shapes_graph.subjects(SH.property, source)), source)
        shape = _name(source)
        focus = _qname(data, results.value(r, SH.focusNode))
        message = str(results.value(r, SH.resultMessage) or "")
        fired.setdefault(shape, set()).add((focus, message))
    return conforms, {k: sorted(v) for k, v in sorted(fired.items())}


def report(label: str, data: Graph, shapes_graph: Graph) -> tuple[bool, dict[str, list[tuple[str, str]]]]:
    """Run the shapes and print one line per shape, then the results of any
    shape that fired. A shape 'passes' when it produced no validation result."""
    names = sorted(_name(s) for s in shapes_graph.subjects(RDF.type, SH.NodeShape))
    conforms, fired = run(data, shapes_graph)
    print(f"{label}: conforms = {conforms}")
    for n in names:
        print(f"  {n:<20} {'FAIL' if n in fired else 'pass'}")
    for shape, hits in fired.items():
        for focus, message in hits:
            print(f"  {shape} at {focus}:\n    {message}")
    return conforms, fired


# ----------------------------------------------------------------- verdict

def passed(claim: str) -> None:
    """Record a claim whose assert held in the cell above this call."""
    _PASSED.append(claim)
    print(f"ok: {claim}")


def verdict() -> None:
    """The one line the gate and the reader look for. It is printed only
    when at least one claim was recorded, which means every cell before this
    one ran and every assert in it held (a failing assert stops the notebook)."""
    print(f"claims checked: {len(_PASSED)}")
    for c in _PASSED:
        print(f"  {c}")
    print("NOTEBOOK: PASS" if _PASSED else "NOTEBOOK: FAIL (no claim was checked)")
