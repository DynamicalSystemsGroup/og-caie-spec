"""Every quote in the glossary is where its citation says it is. Machine
quotes are located in the snapshot at the cited page (PDF) or in the HTML
text; pending quotes are transcriptions awaiting a named verification and
are allowed only for browsing-platform sources; counts are pinned so drift
in either direction fails. The precedence rule is enforced against the
committed ISO 9000:2026 headword list."""
import html
import logging
import re
from functools import lru_cache

import pytest
from pyshacl import validate
from rdflib import RDF, SKOS

from conftest import OGC, ROOT, load, normalized

logging.getLogger("pypdf").setLevel(logging.ERROR)

TERMS = 58
COINED = 3
MACHINE_QUOTES = 57
COMMITTED_MACHINE_QUOTES = 11  # NIST AI 700-2 (7), NIST AI 100-1 (1), NIST TN 1297 (2), W3C EARL (1): always locatable, in CI too
PENDING_QUOTES = 8
HUMAN_QUOTES = 23
PENDING_ALLOWED_SOURCES = {"iso-9000-2026", "iso-iec-17000-2020", "iec-60050-351"}


def union():
    return load("vocabulary/og-caie.ttl", "sources/sources.ttl", "rulings/adjudications.ttl")


def citations(g):
    for t in g.subjects(RDF.type, SKOS.Concept):
        for p in (OGC.canonical, OGC.seeAlso):
            for c in g.objects(t, p):
                yield t, c


@lru_cache(maxsize=None)
def pdf_pages(path: str):
    from pypdf import PdfReader
    r = PdfReader(path)
    return [normalized(p.extract_text() or "") for p in r.pages]


@lru_cache(maxsize=None)
def html_text(path: str):
    t = open(path, encoding="utf-8", errors="replace").read()
    t = re.sub(r"<[^>]+>", " ", t)
    return normalized(html.unescape(t))


def snapshot_file(g, source):
    for snap in g.objects(source, OGC.snapshot):
        f = ROOT / str(g.value(snap, OGC.file))
        if f.suffix in (".pdf", ".html"):
            return f
    return None


def test_glossary_conforms_to_shapes():
    g = union()
    ok, _, report = validate(g, shacl_graph=load("shapes/glossary.shapes.ttl"), advanced=True)
    assert ok, report


def test_counts_pinned():
    g = union()
    terms = list(g.subjects(RDF.type, SKOS.Concept))
    assert len(terms) == TERMS
    assert sum(1 for t in terms if str(g.value(t, OGC["class"])) == "coined") == COINED
    statuses = [str(g.value(c, OGC.quoteStatus)) for _, c in citations(g) if g.value(c, OGC.quote) is not None]
    assert statuses.count("machine") == MACHINE_QUOTES, statuses.count("machine")
    assert statuses.count("pending") == PENDING_QUOTES, statuses.count("pending")
    assert statuses.count("human") == HUMAN_QUOTES


@lru_cache(maxsize=None)
def digest_text(path: str):
    return normalized(open(path, encoding="utf-8").read())


def test_machine_quotes_are_located():
    """A machine quote is located in the snapshot when the file is present
    (always, for committed sources; locally, for held-locally sources). When a
    held-locally file is absent (CI), the quote must at least be present in
    the committed digest, and the committed count is pinned so CI can never
    pass on digests alone."""
    g = union()
    located_in_file = located_in_digest = 0
    for term, c in citations(g):
        if str(g.value(c, OGC.quoteStatus)) != "machine":
            continue
        src = g.value(c, OGC.cites)
        f = snapshot_file(g, src)
        assert f is not None, f"{term}: machine quote cites {src} with no pdf/html snapshot"
        q = normalized(str(g.value(c, OGC.quote)))
        posture = str(g.value(src, OGC.posture))
        if f.exists():
            if f.suffix == ".pdf":
                page = g.value(c, OGC.pdfPage)
                assert page is not None, f"{term}: pdf citation needs ogc:pdfPage"
                text = pdf_pages(str(f))[int(page) - 1]
                assert q in text, f"{term}: quote not found on {f.name} p.{page}: {q[:80]}"
            else:
                assert q in html_text(str(f)), f"{term}: quote not found in {f.name}: {q[:80]}"
            located_in_file += 1
        else:
            assert posture == "heldLocally", f"{term}: committed snapshot missing: {f}"
            d = ROOT / str(g.value(src, OGC.digest))
            assert q in digest_text(str(d)), f"{term}: held-locally file absent and quote not in digest {d.name}: {q[:80]}"
            located_in_digest += 1
    assert located_in_file >= COMMITTED_MACHINE_QUOTES, located_in_file
    assert located_in_file + located_in_digest == MACHINE_QUOTES


def test_pending_quotes_only_from_browsing_platform_sources():
    g = union()
    for term, c in citations(g):
        if str(g.value(c, OGC.quoteStatus)) == "pending":
            slug = str(g.value(c, OGC.cites)).rsplit("#", 1)[-1]
            assert slug in PENDING_ALLOWED_SOURCES, f"{term}: pending quote from {slug}"
            if slug == "iso-9000-2026":
                f = g.value(c, OGC.file)
                assert f is not None and "iso-9000-2026-obp-" in str(f), f"{term}: ISO 9000 quote must name its screenshot"


def test_human_quotes_are_attributed_and_dated():
    g = union()
    for term, c in citations(g):
        if str(g.value(c, OGC.quoteStatus)) == "human":
            assert g.value(c, OGC.verifiedBy) is not None and g.value(c, OGC.verifiedOn) is not None, term


def test_precedence_iso_9000_first():
    g = union()
    heads = {l.strip().lower() for l in (ROOT / "sources/digests/iso-9000-2026-headwords.txt").read_text().splitlines()
             if l.strip() and not l.startswith("#")}
    for t in g.subjects(RDF.type, SKOS.Concept):
        if str(g.value(t, OGC["class"])) != "adopted":
            continue
        label = str(g.value(t, SKOS.prefLabel)).lower()
        src = str(g.value(g.value(t, OGC.canonical), OGC.cites)).rsplit("#", 1)[-1]
        if label in heads:
            assert src == "iso-9000-2026", f"{label} is an ISO 9000:2026 headword but cites {src}"


def test_sevocab_permission_statement_present():
    g = union()
    stmt = None
    for s in g.subjects(RDF.type, OGC.Source):
        if str(s).endswith("#sevocab"):
            stmt = g.value(s, OGC.permissionStatement)
    assert stmt is not None and "IEEE" in str(stmt)
    assert str(stmt) in (ROOT / "sources/digests/sevocab.md").read_text()
