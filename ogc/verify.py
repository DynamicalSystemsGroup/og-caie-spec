"""The verbatim check, shared by the tests and `ogc verify`: the one
normalization for PDF text layers and screenshots' transcriptions, and
locate(), which says where a citation's quote was found: on the cited page
of a held or committed snapshot, in a committed HTML page, in the digest
when a held-locally file is absent, or by a named person on a date."""
from __future__ import annotations

import html
import logging
import re
from functools import lru_cache
from pathlib import Path

from rdflib import Graph

from .graph import OGC

logging.getLogger("pypdf").setLevel(logging.ERROR)


def normalized(text: str) -> str:
    """Quote-and-dash-folded, lowercase, whitespace-free, hyphen-free: PDF
    extractors split kerned words and leave line-end hyphenation."""
    t = text.replace("’", "'").replace("‘", "'")
    t = t.replace("“", '"').replace("”", '"')
    t = t.replace("–", "-").replace("—", "-").replace("­", "")
    t = t.replace("ﬁ", "fi").replace("ﬂ", "fl")
    t = t.replace("-", "")
    return re.sub(r"\s+", "", t).strip().lower()


@lru_cache(maxsize=None)
def pdf_pages(path: str) -> list[str]:
    from pypdf import PdfReader
    r = PdfReader(path)
    return [normalized(p.extract_text() or "") for p in r.pages]


@lru_cache(maxsize=None)
def html_text(path: str) -> str:
    t = open(path, encoding="utf-8", errors="replace").read()
    t = re.sub(r"<[^>]+>", " ", t)
    return normalized(html.unescape(t))


@lru_cache(maxsize=None)
def digest_text(path: str) -> str:
    return normalized(open(path, encoding="utf-8").read())


def snapshot_file(g: Graph, root: Path, source) -> Path | None:
    for snap in g.objects(source, OGC.snapshot):
        f = root / str(g.value(snap, OGC.file))
        if f.suffix in (".pdf", ".html"):
            return f
    return None


def locate(g: Graph, root: Path, citation) -> tuple[str, str]:
    """Return (state, where). States: verified, human, pending, cite-only,
    digest, NOT FOUND."""
    src = g.value(citation, OGC.cites)
    quote = g.value(citation, OGC.quote)
    status = str(g.value(citation, OGC.quoteStatus) or "")
    if quote is None:
        return "cite-only", "no quote carried"
    if status == "human":
        who = g.value(citation, OGC.verifiedBy)
        when = g.value(citation, OGC.verifiedOn)
        f = g.value(citation, OGC.file)
        where = f"verified by {str(who).rsplit('#', 1)[-1]} on {when}" + (f"; {Path(str(f)).name}" if f else "")
        return "human", where
    if status == "pending":
        return "pending", "transcribed; awaiting a named verification"
    q = normalized(str(quote))
    f = snapshot_file(g, root, src)
    if f is not None and f.exists():
        if f.suffix == ".pdf":
            page = g.value(citation, OGC.pdfPage)
            if page is None:
                return "NOT FOUND", "pdf citation without ogc:pdfPage"
            pages = pdf_pages(str(f))
            n = int(page)
            if 1 <= n <= len(pages) and q in pages[n - 1]:
                return "verified", f"{f.name} p. {n}"
            return "NOT FOUND", f"not on {f.name} p. {n}"
        if q in html_text(str(f)):
            return "verified", f.name
        return "NOT FOUND", f"not in {f.name}"
    d = g.value(src, OGC.digest)
    if d is not None and (root / str(d)).exists() and q in digest_text(str(root / str(d))):
        posture = str(g.value(src, OGC.posture))
        return "digest", f"{Path(str(d)).name} ({'held-locally file absent' if posture == 'heldLocally' else posture})"
    return "NOT FOUND", "no snapshot on disk and not in the digest"
