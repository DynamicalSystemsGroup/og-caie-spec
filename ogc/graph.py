"""Load the OG-CAIE graphs into one rdflib Graph, with a cache keyed on the
source files. Never re-serialized here. Follows the authors' earlier
glossary tooling (ruling R-29)."""
from __future__ import annotations

import hashlib
import os
import pickle
import subprocess
from pathlib import Path

from rdflib import RDF, Graph, Namespace

OGC = Namespace("https://w3id.org/og-caie/")
TERM = Namespace("https://w3id.org/og-caie/terms#")
SRC = Namespace("https://w3id.org/og-caie/sources#")
RUL = Namespace("https://w3id.org/og-caie/rulings#")
EPO = Namespace("https://w3id.org/og-caie/epo#")
XW = Namespace("https://w3id.org/og-caie/crosswalk#")
TR = Namespace("https://w3id.org/og-caie/trace#")
OGM = Namespace("https://w3id.org/og-caie/model#")
EV = Namespace("https://w3id.org/og-caie/evaluation/measles#")  # the measles evaluation's namespace (track/measles-evaluation.ttl, loaded by --record; sheet 10-42)
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
PROV = Namespace("http://www.w3.org/ns/prov#")
EARL = Namespace("http://www.w3.org/ns/earl#")
SH = Namespace("http://www.w3.org/ns/shacl#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
PREFIXES = {"ogc": OGC, "term": TERM, "src": SRC, "rul": RUL, "epo": EPO, "xw": XW, "tr": TR, "ogm": OGM, "ev": EV,
            "skos": SKOS, "prov": PROV, "earl": EARL, "sh": SH, "rdfs": RDFS,
            "rdf": Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#"), "xsd": Namespace("http://www.w3.org/2001/XMLSchema#"),
            "sysml": Namespace("https://www.omg.org/spec/SysML#"), "sysx": Namespace("urn:opensysml:sysml:"), "elmt": Namespace("urn:sysmlv2:element:")}
SPARQL_PREFIXES = "".join(f"PREFIX {k}: <{v}>\n" for k, v in PREFIXES.items())
SOURCE_FILES = ["vocabulary/og-caie.ttl", "vocabulary/epo.ttl", "vocabulary/register.ttl", "vocabulary/ogm.ttl", "vocabulary/crosswalk.ttl", "sources/sources.ttl",
                "rulings/adjudications.ttl", "model/trace.ttl", "shapes/epo.shapes.ttl", "shapes/model.shapes.ttl"]  # every vocabulary (the register and the model predicates too, round four, KG 5), the sources, the rulings, the essentials, the two shape files over the record and the model
SHAPE_FILES = ["shapes/epo.shapes.ttl", "shapes/model.shapes.ttl", "shapes/rulings.shapes.ttl", "shapes/glossary.shapes.ttl"]  # every shape file; `ogc shapes`, `ogc shape` and the schema's shape count read them all
MODEL_FILE = "model/og-caie.model.ttl"
DERIVED_FILE = "vocabulary/derived.ttl"  # declares ogc:derivedStep, the one predicate infer_steps adds in memory; loaded with the record (round four, H3)
RECORD_FILE = "track/measles-evaluation.ttl"  # the worked example's record, the measles evaluation; read by `ogc record` and `--record` (C-44, ruling R-47; sheet 10-42)
DIGEST_FILES = {"shapesDigest": "shapes/epo.shapes.ttl", "ontologyDigest": "vocabulary/epo.ttl", "queryDigest": "queries/coverage.rq"}  # what is named by sha256 (tool qualification, sheet 10-18): the verdict names the shapes and the ontology it ran and the record it judged (epo:recordDigest, computed by record_digest), the coverage computation the shapes, the ontology and the query
VERDICT_DIGESTS = ("shapesDigest", "ontologyDigest", "recordDigest")
COVERAGE_DIGESTS = ("shapesDigest", "ontologyDigest", "queryDigest")
DOCTOR_FILES = SOURCE_FILES + [f for f in SHAPE_FILES if f not in SOURCE_FILES] + [MODEL_FILE, DERIVED_FILE, RECORD_FILE]  # every file the tool reads; `ogc doctor` parses each


def find_root(start: Path | None = None) -> Path:
    env = os.environ.get("OGC_ROOT")
    if env:
        return Path(env).resolve()
    p = (start or Path.cwd()).resolve()
    for cand in (p, *p.parents):
        if (cand / "vocabulary" / "og-caie.ttl").exists() and (cand / "sources" / "sources.ttl").exists():
            return cand
    return Path(__file__).resolve().parents[1]


def files(root: Path, model: bool = False, record: bool = False) -> list[Path]:
    """The files to load. The record brings the model graph with it (sheet
    10-33): an item's step is derived through the model, so the record is
    never read without it."""
    out = [root / f for f in SOURCE_FILES]
    if (model or record) and (root / MODEL_FILE).exists():
        out.append(root / MODEL_FILE)
    if record and (root / RECORD_FILE).exists():
        if (root / DERIVED_FILE).exists():
            out.append(root / DERIVED_FILE)
        out.append(root / RECORD_FILE)
    return out


def digests(root: Path | None = None) -> dict[str, str]:
    """sha256 of the shapes, the ontology and the coverage query as they
    stand in the checkout: what a conformance verdict and a coverage
    computation name (sheet 10-18), what `ogc doctor` compares the record's
    digests with, and what the executor writes."""
    root = root or find_root()
    return {k: hashlib.sha256((root / f).read_bytes()).hexdigest() for k, f in DIGEST_FILES.items()}


def record_digest(g: Graph, record, cutoff, exclude=()) -> str:
    """The record digest a conformance verdict carries (round four, KG 8):
    the sha256 of the canonical N-Triples of the record's member triples
    generated at or before the cutoff, the verdict's own time. A member is
    the record itself or a node with ogc:inRecord the record; a member
    dated (prov:generatedAtTime, else prov:startedAtTime, else
    prov:endedAtTime) after the cutoff is left out, an undated member
    (a requirement, a trajectory, an agent) is in; the nodes in `exclude`
    (the verdict) are left out; a blank node reachable from a member's
    triples (an earl:result) comes with it. Canonical: rdflib's
    to_canonical_graph relabels the blank nodes deterministically, and the
    N-Triples lines are sorted before hashing, so the value does not depend
    on the file's layout, comments or prefixes. Written by
    scripts/stamp_digests.py and the executor, checked by `ogc doctor`."""
    from rdflib import BNode
    from rdflib.compare import to_canonical_graph
    cut = cutoff.toPython() if hasattr(cutoff, "toPython") else cutoff
    members = set(g.subjects(OGC.inRecord, record)) | {record}
    sub = Graph()

    def take(s):
        for p, o in g.predicate_objects(s):
            if p == OGC.derivedStep:  # derived in memory by infer_steps, never the record's own (sheet 10-33)
                continue
            sub.add((s, p, o))
            if isinstance(o, BNode):
                take(o)
    for s in members:
        if s in exclude:
            continue
        when = g.value(s, PROV.generatedAtTime) or g.value(s, PROV.startedAtTime) or g.value(s, PROV.endedAtTime)
        if when is not None and when.toPython() > cut:
            continue
        take(s)
    lines = sorted(l for l in to_canonical_graph(sub).serialize(format="nt").splitlines() if l.strip())
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def verdict_digest(g: Graph) -> dict:
    """(verdict, record digest) per conformance verdict of a loaded record:
    the digest recomputed over the record as it stood at the verdict, the
    verdict itself excluded; what `ogc doctor` compares with the stored
    epo:recordDigest and the tests assert."""
    out = {}
    for v in g.subjects(RDF.type, EPO.ConformanceVerdict):
        rec = g.value(v, OGC.inRecord)
        out[v] = record_digest(g, rec, g.value(v, PROV.generatedAtTime), exclude={v})
    return out


def infer_steps(g: Graph) -> int:
    """Derive the step of every record item in memory (sheet 10-33, R-50) and
    add it as `ogc:derivedStep` (declared in vocabulary/derived.ttl; round
    four, H3: under its own name, so a DESCRIBE shows it as derived); the
    number of triples added. No record file asserts a step. The derivation: the item's class is realized by an item
    kind of the model (ogm:realizes, written by scripts/prune_model.py), the
    item kind is an out parameter of a step of the model, and that step
    realizes an EPO step. An activity with no model element of its own (a
    probe derivation, a coverage computation) takes the step of the item it
    generated; a member with neither takes the step of what contains it
    (the containment rule below). A kind two steps may produce (the plan
    deviation) carries both; a listing shows the earlier. The model graph
    must be loaded."""
    q = """
        PREFIX ogm: <https://w3id.org/og-caie/model#>
        PREFIX sysml: <https://www.omg.org/spec/SysML#>
        SELECT DISTINCT ?item ?step WHERE {
            ?item a ?cls . ?kind ogm:realizes ?cls .
            ?p sysml:type ?kind ; sysml:direction "out" ; sysml:owner ?act . ?act ogm:realizes ?step .
        }"""
    n = 0
    for item, step in g.query(q):
        if (item, OGC.derivedStep, step) not in g:
            g.add((item, OGC.derivedStep, step)); n += 1
    for act in list(g.subjects(RDF.type, PROV.Activity)) + [a for a in g.objects(None, PROV.wasGeneratedBy)]:
        if g.value(act, OGC.derivedStep) is not None:
            continue
        for produced in g.subjects(PROV.wasGeneratedBy, act):
            for step in g.objects(produced, OGC.derivedStep):
                if (act, OGC.derivedStep, step) not in g:
                    g.add((act, OGC.derivedStep, step)); n += 1
    # The containment rule (round four, KG 6): a member with no model element
    # of its own takes the step of what contains it, to a fixpoint: a
    # requirement that of its requirement set (epo:partOf), a trajectory
    # that of the session that generated it (prov:wasGeneratedBy), an
    # engagement decision that of the statement of work that decides it
    # (epo:decides, inverse), a consistency check that of the probe it
    # checks (earl:subject). Agents carry no step.
    changed = True
    while changed:
        changed = False
        for item in set(g.subjects(OGC.inRecord, None)):
            if g.value(item, OGC.derivedStep) is not None or (item, RDF.type, PROV.Agent) in g:
                continue
            containers = list(g.objects(item, EPO.partOf)) + list(g.objects(item, PROV.wasGeneratedBy)) + list(g.subjects(EPO.decides, item)) + list(g.objects(item, EARL.subject))
            for c in containers:
                for step in g.objects(c, OGC.derivedStep):
                    if (item, OGC.derivedStep, step) not in g:
                        g.add((item, OGC.derivedStep, step)); n += 1; changed = True
    return n


def _key(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for p in paths:
        st = p.stat()
        h.update(f"{p}:{st.st_mtime_ns}:{st.st_size};".encode())
    return h.hexdigest()[:16]


def load(root: Path | None = None, model: bool = False, cache: bool = True, record: bool = False) -> Graph:
    # The pickle cache holds only graphs this tool parsed itself from the
    # checkout's own Turtle files, written under the gitignored .cache/ and
    # keyed on those files' mtimes; nothing untrusted is ever unpickled.
    root = root or find_root()
    paths = files(root, model, record)
    cache_dir = root / ".cache"
    key = _key(paths)
    cp = cache_dir / f"ogc-graph-{key}.pkl"
    if cache and cp.exists():
        try:
            with cp.open("rb") as f:
                return pickle.load(f)
        except Exception:
            pass
    g = Graph()
    for k, v in PREFIXES.items():
        g.bind(k, v, replace=True)
    for p in paths:
        g.parse(p)
    if record:
        infer_steps(g)  # the step is derived, never asserted (sheet 10-33)
    if cache:
        try:
            cache_dir.mkdir(exist_ok=True)
            for old in cache_dir.glob("ogc-graph-*.pkl"):
                old.unlink()
            with cp.open("wb") as f:
                pickle.dump(g, f)
        except Exception:
            pass
    return g


def git_sha(root: Path | None = None) -> str:
    root = root or find_root()
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"
