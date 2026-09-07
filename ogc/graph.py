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
SOURCE_FILES = ["vocabulary/og-caie.ttl", "vocabulary/epo.ttl", "vocabulary/crosswalk.ttl", "sources/sources.ttl",
                "rulings/adjudications.ttl", "model/trace.ttl", "shapes/epo.shapes.ttl", "shapes/model.shapes.ttl"]
SHAPE_FILES = ["shapes/epo.shapes.ttl", "shapes/model.shapes.ttl", "shapes/rulings.shapes.ttl", "shapes/glossary.shapes.ttl"]  # every shape file; `ogc shapes`, `ogc shape` and the schema's shape count read them all
MODEL_FILE = "model/og-caie.model.ttl"
DERIVED_FILE = "vocabulary/derived.ttl"  # declares ogc:derivedStep, the one predicate infer_steps adds in memory; loaded with the record (round four, H3)
RECORD_FILE = "track/measles-evaluation.ttl"  # the worked example's record, the measles evaluation; read by `ogc record` and `--record` (C-44, ruling R-47; sheet 10-42)
DIGEST_FILES = {"shapesDigest": "shapes/epo.shapes.ttl", "ontologyDigest": "vocabulary/epo.ttl", "queryDigest": "queries/coverage.rq"}  # what the verdict names by sha256 (tool qualification, sheet 10-18)
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


def infer_steps(g: Graph) -> int:
    """Derive the step of every record item in memory (sheet 10-33, R-50) and
    add it as `ogc:derivedStep` (declared in vocabulary/derived.ttl; round
    four, H3: under its own name, so a DESCRIBE shows it as derived); the
    number of triples added. No record file asserts a step. The derivation: the item's class is realized by an item
    kind of the model (ogm:realizes, written by scripts/prune_model.py), the
    item kind is an out parameter of a step of the model, and that step
    realizes an EPO step. An activity with no model element of its own (a
    probe derivation, a coverage computation) takes the step of the item it
    generated. A kind two steps may produce (the plan deviation) carries
    both; a listing shows the earlier. The model graph must be loaded."""
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
