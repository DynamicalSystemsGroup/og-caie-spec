"""The source register is honest: every declared snapshot that is present on
disk hashes to its declared value; committed snapshots are always present;
held-locally snapshots are never committed; every source has a digest."""
import hashlib
import subprocess

from rdflib import RDF

from conftest import OGC, ROOT, load

COMMITTED = 7      # 3 NIST PDFs + 4 W3C HTML
HELD_LOCALLY = 9   # ISO 9000 screenshots (one source), SEVOCAB, GtWR, Hawkins, ISA 500, Gruber, Hogan, SEBoK, VIM


def _graph():
    return load("sources/sources.ttl")


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_posture_counts_pinned():
    g = _graph()
    postures = [str(g.value(s, OGC.posture)) for s in g.subjects(RDF.type, OGC.Source)]
    assert postures.count("committed") == COMMITTED
    assert postures.count("heldLocally") == HELD_LOCALLY


def test_committed_snapshots_present_and_hash():
    g = _graph()
    n = 0
    for s in g.subjects(RDF.type, OGC.Source):
        if str(g.value(s, OGC.posture)) != "committed":
            continue
        for snap in g.objects(s, OGC.snapshot):
            f = ROOT / str(g.value(snap, OGC.file))
            assert f.exists(), f
            assert _sha(f) == str(g.value(snap, OGC.contentHash)), f
            n += 1
    assert n >= COMMITTED


def test_held_locally_snapshots_hash_when_present():
    g = _graph()
    checked = declared = 0
    for s in g.subjects(RDF.type, OGC.Source):
        if str(g.value(s, OGC.posture)) != "heldLocally":
            continue
        for snap in g.objects(s, OGC.snapshot):
            declared += 1
            f = ROOT / str(g.value(snap, OGC.file))
            if f.exists():
                assert _sha(f) == str(g.value(snap, OGC.contentHash)), f
                checked += 1
    assert declared >= 37 + 8
    if checked:
        assert checked == declared, "some held-locally snapshots present, others missing"


def test_held_locally_files_are_not_tracked():
    out = subprocess.run(["git", "ls-files", "sources/local"], cwd=ROOT, capture_output=True, text=True).stdout
    assert out.strip() == "", out


def test_every_rank_is_an_integer_from_one_to_eight():
    from rdflib import Literal
    from rdflib.namespace import XSD
    g = _graph()
    ranks = [g.value(s, OGC.rank) for s in g.subjects(RDF.type, OGC.Source)]
    assert len(ranks) == 20 and all(isinstance(r, Literal) and r.datatype == XSD.integer and 1 <= int(r) <= 8 for r in ranks), ranks


def test_every_source_has_a_digest_file_or_is_internal():
    g = _graph()
    for s in g.subjects(RDF.type, OGC.Source):
        if int(g.value(s, OGC.rank)) == 8:  # the authors' own source (sheet 10-46: ordinal ranks, no reserve); an xsd:integer (round four, KG 11)
            continue
        d = g.value(s, OGC.digest)
        assert d is not None, s
        assert (ROOT / str(d)).exists(), d
