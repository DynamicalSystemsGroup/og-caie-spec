#!/usr/bin/env python3
"""The works-cited apparatus (ruling R-48), rendered from the graphs.

Three outputs, all deterministic (same graphs and pages, same bytes; the
gate regenerates and diffs them):

- ``references.bib``: one BibTeX entry per ``ogc:Source`` in the register,
  keyed by the source's local name. The register carries a label, a kind, a
  rank, a posture and a URL, not bibliographic fields, so the entry's type
  and fields are read off the label's form by the rules in ``parse_label``
  (a standard, a report, a paper, a book, an event, or a bare title) and
  nothing is invented: a year appears only when the label carries it. The
  entries the hand-written file carried before this renderer existed are
  kept in ``HAND_ENTRIES`` and merged in (a source the register lacks stays
  whole; a source the register has gains the fields its label cannot give,
  such as full author names, a DOI or a proceedings title).
- ``generated/cited-<page>.md`` for each main-path page: the sources that
  page cites, derived from the graph. The ``{term}`` roles on the page and
  on the fragments it includes resolve to terms, whose canonical and
  seeAlso citations name sources with locators; the steps tables name the
  steps' citations; the SCI tables name what each essential rests on; the
  crosswalk tables name the session and Popper. One line per source, with
  a ``{cite:p}`` role so MyST links the entry.
- ``generated/cited-all.md``: every source with the pages that cite it,
  for Appendix E.
"""
import re
import sys
from pathlib import Path

from rdflib import RDF, Graph, Namespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from render import TERM_ROLE, cell, referenced_terms  # noqa: E402

OGC = Namespace("https://w3id.org/og-caie/")
EPO = Namespace("https://w3id.org/og-caie/epo#")
SRC = Namespace("https://w3id.org/og-caie/sources#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
OUT = ROOT / "generated"
GRAPH_FILES = ("vocabulary/og-caie.ttl", "vocabulary/epo.ttl", "vocabulary/crosswalk.ttl", "sources/sources.ttl", "model/trace.ttl")
PAGES = {"index": ROOT / "index.md", "glossary": ROOT / "docs" / "glossary.md", "contracting": ROOT / "docs" / "contracting.md",
         "evaluation": ROOT / "docs" / "evaluation.md", "model": ROOT / "docs" / "model.md",
         "guarantees": ROOT / "docs" / "guarantees.md", "conclusion": ROOT / "docs" / "conclusion.md"}
RANK_ORDER = {"1": 0, "2": 1, "3": 2, "4": 3, "reserve": 4, "internal": 5}
FIELD_ORDER = ["title", "author", "organization", "institution", "number", "booktitle", "journal", "volume", "publisher", "address",
               "howpublished", "year", "doi", "url", "note"]
INCLUDE = re.compile(r"```\{include\}\s+(\S+)")
FULLER = {"author", "organization", "institution", "booktitle"}  # the hand-written file's full forms beat the label's short ones
CORPORATE = {"organization", "institution"}  # a body's name is one name: doubly braced so a citation processor never splits it on "and"

# The entries of the hand-written references.bib this renderer replaced, kept whole where the register has no such
# source (the toolchain) and merged where it has (the register's label gives surnames, a number and a title; the
# hand-written entry adds the full author list, the DOI, the proceedings title and the bodies' full names).
HAND_ENTRIES = {
    "opensysml043": ("misc", {"title": "OpenSysML v0.4.3", "organization": "Open-MBEE", "year": "2026",
                              "url": "https://github.com/Open-MBEE/OpenSysML/releases/tag/v0.4.3",
                              "note": "kept from the hand-written references.bib; the toolchain of Appendix D, not a registered source"}),
    "iso-9000-2026": ("misc", {"organization": "International Organization for Standardization"}),
    "sevocab": ("misc", {"organization": "IEEE Computer Society and ISO/IEC JTC 1/SC 7"}),
    "nist-ai-700-2": ("techreport", {"author": "Amironesei, Razvan and Godil, Afzal and Greenberg, Craig and Greene, Kristen and Hall, Patrick and Jensen, Theodore and Fiscus, Jonathan and Schulman, Noah",
                                     "institution": "National Institute of Standards and Technology", "doi": "10.6028/NIST.AI.700-2"}),
    "gruber-1993": ("article", {"author": "Gruber, Thomas R.", "journal": "Knowledge Acquisition", "volume": "5", "number": "2", "pages": "199--220", "doi": "10.1006/knac.1993.1008"}),
    "hogan-2021": ("article", {"author": "Hogan, Aidan and Blomqvist, Eva and Cochez, Michael and d'Amato, Claudia and de Melo, Gerard and Gutierrez, Claudio and Kirrane, Sabrina and Labra Gayo, Jos\\'e Emilio and Navigli, Roberto and Neumaier, Sebastian and Ngonga Ngomo, Axel-Cyrille and Polleres, Axel and Rashid, Sabbir M. and Rula, Anisa and Schmelzeisen, Lukas and Sequeda, Juan and Staab, Steffen and Zimmermann, Antoine",
                              "journal": "ACM Computing Surveys", "volume": "54", "number": "4", "pages": "71:1--71:37", "doi": "10.1145/3447772"}),
    "popper-1959": ("book", {"author": "Popper, Karl R.", "publisher": "Hutchinson", "address": "London"}),
    "nist-tn-1297": ("techreport", {"author": "Taylor, Barry N. and Kuyatt, Chris E.", "institution": "National Institute of Standards and Technology"}),
    "sebok-2-14": ("misc", {"editor": "{SEBoK Editorial Board}", "publisher": "The Trustees of the Stevens Institute of Technology", "address": "Hoboken, NJ"}),
    "hawkins-2011": ("inproceedings", {"author": "Hawkins, Richard and Kelly, Tim and Knight, John and Graydon, Patrick",
                                       "booktitle": "Advances in Systems Safety: Proceedings of the Nineteenth Safety-Critical Systems Symposium"}),
    "scipy-2026-bof": ("misc", {"author": "Hollek, Julie and Zargham, Michael"}),  # Julie Hollek first author (Z, 2026-09-07)
    "isa-500": ("misc", {"organization": "International Auditing and Assurance Standards Board"}),
    "w3c-prov-o": ("misc", {"organization": "W3C"}),
    "w3c-earl": ("misc", {"organization": "W3C"}),
    "w3c-shacl": ("misc", {"organization": "W3C"}),
    "w3c-skos": ("misc", {"organization": "W3C"}),
}


def graph() -> Graph:
    g = Graph()
    for f in GRAPH_FILES:
        g.parse(ROOT / f)
    return g


def local(n) -> str:
    return str(n).rsplit("#", 1)[-1]


# --- the label's forms -------------------------------------------------------------------------------------------

SURNAMES = re.compile(r"^[A-Z][A-Za-z'-]+( et al\.| and [A-Z][A-Za-z'-]+)?$")
YEAR = re.compile(r"\b(1[5-9]\d\d|20\d\d)\b")


def parse_label(label: str, kind: str) -> tuple[str, dict, str]:
    """Read the entry type, its fields and a short name for the body or author off the register's label.
    Returns (type, fields, who, extra): the fields carry only what the label states; who is None when the
    label is a bare title; extra is the label's trailing parenthetical, for the note."""
    f = {}
    # ISO 9000:2026(en) Title (Platform); ISO/IEC 17000:2020(en) Title (Platform)
    m = re.match(r"^((ISO(?:/IEC)?) [\d-]+:(\d{4}))\(en\) (.+?)(?: \((.+)\))?$", label)
    if m:
        f.update(title=f"{m.group(1)} {m.group(4)}", organization=m.group(2), year=m.group(3))
        return "misc", f, m.group(2), m.group(5)
    # IEC 60050-351:2013 Title (Platform)
    m = re.match(r"^((IEC) [\d-]+:(\d{4})) (.+?)(?: \((.+)\))?$", label)
    if m:
        f.update(title=f"{m.group(1)} {m.group(4)}", organization=m.group(2), year=m.group(3))
        return "misc", f, m.group(2), m.group(5)
    # JCGM 200:2012 Title (BIPM)
    m = re.match(r"^((JCGM) [\d-]+:(\d{4})) (.+?) \((BIPM)\)$", label)
    if m:
        f.update(title=f"{m.group(1)} {m.group(4)}", organization=m.group(2), publisher=m.group(5), year=m.group(3))
        return "misc", f, m.group(2), None
    # NIST AI 700-2, Title (Month 2025); NIST AI 100-1, Title, Month 2023; NIST Technical Note 1297, Title, 1994 edition
    m = re.match(r"^((NIST) (?:AI [\d-]+|Technical Note \d+)), (.+?)(?:, | \()(?:[A-Z][a-z]+ )?(\d{4})(?: edition)?\)?$", label)
    if m:
        f.update(title=m.group(3), institution=m.group(2), number=m.group(1), year=m.group(4))
        return "techreport", f, m.group(2), None
    # W3C, Title, Recommendation 30 April 2013; W3C, Title, Working Group Note 2 February 2017
    m = re.match(r"^(W3C), (.+), ((?:Recommendation|Working Group Note) \d{1,2} [A-Z][a-z]+ (\d{4}))$", label)
    if m:
        f.update(title=m.group(2), organization=m.group(1), year=m.group(4))
        return "misc", f, m.group(1), m.group(3)
    # IEEE Computer Society, Title (SEVOCAB), PDF export (481 pp.)
    m = re.match(r"^(IEEE Computer Society), (.+), PDF export \((.+)\)$", label)
    if m:
        f.update(title=m.group(2), organization=m.group(1))
        return "misc", f, m.group(1), f"PDF export, {m.group(3)}"
    # IAASB, Title (effective 15 December 2009)
    m = re.match(r"^(IAASB), (.+) \((effective .+ (\d{4}))\)$", label)
    if m:
        f.update(title=m.group(2), organization=m.group(1), year=m.group(4))
        return "misc", f, m.group(1), m.group(3)
    # INCOSE Guide to Writing Requirements v4, Summary Sheet (INCOSE-TP-2010-006-04, June 2023)
    m = re.match(r"^(INCOSE) (.+) \((INCOSE-TP-\S+), [A-Z][a-z]+ (\d{4})\)$", label)
    if m:
        f.update(title=m.group(2), organization=m.group(1), number=m.group(3), year=m.group(4))
        return "misc", f, m.group(1), None
    # Papers, books and events: Surnames, Title, Venue [volume(number)], Year (note); or Surname, Title, Place: Publisher, Year
    parts = label.split(", ")
    authors = []
    while parts and SURNAMES.match(parts[0]):
        authors.append(parts.pop(0))
    if authors and len(parts) >= 2:
        title, rest = parts[0], ", ".join(parts[1:])
        who = ", ".join(authors)
        f["title"] = title
        f["author"] = " and ".join(a.replace(" et al.", " and others") for a in authors)
        note = None
        m = re.match(r"^(.*?)(?: \((.+)\))?$", rest)
        rest, note = m.group(1), m.group(2)
        m = re.match(r"^(.+?) (\d+)\((\d+)\), (\d{4})$", rest)  # journal volume(number), year
        if m:
            f.update(journal=m.group(1), volume=m.group(2), number=m.group(3), year=m.group(4))
            return "article", f, who, note
        m = re.match(r"^([^:]+): ([^,]+), (\d{4})$", rest)  # place: publisher, year
        if m:
            f.update(publisher=m.group(2), address=m.group(1), year=m.group(3))
            return "book", f, who, note
        m = re.match(r"^(.+? Symposium) (\d{4})$", rest)  # a symposium and its year
        if m:
            f.update(booktitle=m.group(1), year=m.group(2))
            return "inproceedings", f, who, note
        m = re.match(r"^(.+ (\d{4}))$", rest)  # an event: how it was presented, with its year
        if m:
            f.update(howpublished=m.group(1), year=m.group(2))
            return "misc", f, who, note
        f["howpublished"] = rest
        return "misc", f, who, note
    return "misc", {"title": label}, None, None


def entries(g: Graph | None = None) -> dict[str, tuple[str, dict]]:
    """Every entry of the bibliography: the register's sources, merged with the hand-written entries."""
    g = g or graph()
    out = {}
    for s in g.subjects(RDF.type, OGC.Source):
        key = local(s)
        kind, fields, _who, extra = parse_label(str(g.value(s, RDFS.label)), str(g.value(s, OGC.kind)))
        url = g.value(s, OGC.url)
        if url is not None:
            fields["url"] = str(url)
        note = [f"posture {g.value(s, OGC.posture)}", f"rank {g.value(s, OGC.rank)}"]
        if extra:
            note.append(extra)
        status = g.value(s, OGC.status)
        if status is not None:
            note.append(str(status))
        fields["note"] = "; ".join(note)
        hand = HAND_ENTRIES.get(key)
        if hand:
            for k, v in hand[1].items():
                if k in FULLER or k not in fields:  # the label gives surnames and abbreviations; the hand-written file gives the full names
                    fields[k] = v
        out[key] = (kind, fields)
    for key, (kind, fields) in HAND_ENTRIES.items():
        if key not in out:
            out[key] = (kind, dict(fields))
    return dict(sorted(out.items()))


def who(g: Graph, key: str) -> str | None:
    """The short name a works-cited line leads with: the body for a standard or report, the surnames for a paper,
    nothing when the label is a bare title."""
    s = SRC[key]
    if (s, RDF.type, OGC.Source) not in g:
        return HAND_ENTRIES[key][1].get("organization")
    return parse_label(str(g.value(s, RDFS.label)), str(g.value(s, OGC.kind)))[2]


def head(g: Graph, key: str) -> str:
    """Who and title, or the title alone."""
    w = who(g, key)
    return f"{w}, {cell(title_of(g, key))}" if w else cell(title_of(g, key))


def render_bib(g: Graph | None = None) -> str:
    lines = []
    for key, (kind, fields) in entries(g).items():
        lines.append(f"@{kind}{{{key},")
        ordered = [k for k in FIELD_ORDER if k in fields] + sorted(k for k in fields if k not in FIELD_ORDER)
        body = [f"  {k} = {{{'{' + fields[k] + '}' if k in CORPORATE else fields[k]}}}" for k in ordered]
        lines.append(",\n".join(body))
        lines.append("}")
    return "\n".join(lines) + "\n"


def parse_bib(text: str) -> dict[str, tuple[str, dict]]:
    """A small reader for the file this renderer writes: one field per line, braces delimit values."""
    out = {}
    for m in re.finditer(r"^@(\w+)\{([^,]+),\n(.*?)\n\}$", text, re.M | re.S):
        fields = {k: v[1:-1] if v.startswith("{") and v.endswith("}") else v  # a doubly braced corporate name reads as one name
                  for k, v in re.findall(r"^\s*(\w+) = \{(.*)\},?$", m.group(3), re.M)}
        out[m.group(2)] = (m.group(1), fields)
    return out


# --- what each page cites ----------------------------------------------------------------------------------------

def rank_key(key: str, g: Graph | None = None) -> tuple:
    g = g or _G()
    rank = g.value(SRC[key], OGC.rank)
    return (RANK_ORDER.get(str(rank), 9), key)


_cache = {}


def _G() -> Graph:
    if "g" not in _cache:
        _cache["g"] = graph()
    return _cache["g"]


def citations_of(g: Graph, subject) -> list[tuple[str, str]]:
    """The (source key, locator) pairs a term or a step cites, canonical first."""
    out = []
    for pred in (OGC.canonical, OGC.seeAlso):
        for c in g.objects(subject, pred):
            src = g.value(c, OGC.cites)
            if src is not None:
                out.append((local(src), str(g.value(c, OGC.locator) or "")))
    return out


def page_text(page: str) -> tuple[str, list[str]]:
    """The page's prose and the names of the fragments it includes, the works-cited fragment excepted."""
    path = PAGES[page]
    text = path.read_text().split("\n## Sources cited\n")[0]
    fragments = [Path(inc).name for inc in INCLUDE.findall(text) if not Path(inc).name.startswith("cited-")]
    return text, fragments


def page_citations(page: str, g: Graph | None = None) -> dict[str, dict]:
    """Source key -> {"locators": [...], "essentials": [...]} for one page, from the roles on the page, the roles on
    the fragments it includes, and the graph objects those fragments render."""
    g = g or _G()
    text, fragments = page_text(page)
    texts = [text] + [(OUT / f).read_text() for f in fragments if (OUT / f).exists()]
    labels = {}
    for t in g.subjects(RDF.type, SKOS.Concept):
        for pred in (SKOS.prefLabel, SKOS.altLabel):
            for l in g.objects(t, pred):
                labels.setdefault(str(l).lower(), set()).add(t)
    subjects = set()
    for t in texts:
        for m in TERM_ROLE.finditer(t):
            key = m.group(1)
            if "<" in key:
                key = key[key.rindex("<") + 1:].rstrip(">").strip()
            hits = labels.get(key.lower(), set())
            if len(hits) != 1:
                raise SystemExit(f"{page}: unresolved {{term}} role {key!r}")
            subjects.add(next(iter(hits)))
    if "key-terms.md" in fragments:  # the glossary page renders every referenced term with its citation
        found, unresolved = referenced_terms(g)
        if unresolved:
            raise SystemExit(f"unresolved {{term}} roles: {unresolved}")
        subjects |= set(found)
    if "steps-contracting.md" in fragments or "steps.md" in fragments:
        subjects |= set(g.subjects(RDF.type, EPO.ContractingStep)) | {EPO.ContractingStep}
    if "steps-evaluation.md" in fragments or "steps.md" in fragments:
        subjects |= set(g.subjects(RDF.type, EPO.EpoStep))
    cites = {}

    def add(key, locator=None, essential=None):
        d = cites.setdefault(key, {"locators": set(), "essentials": set()})
        if locator:
            d["locators"].add(locator)
        if essential:
            d["essentials"].add(essential)

    for s in subjects:
        for key, loc in citations_of(g, s):
            add(key, loc)
    for f in fragments:
        m = re.match(r"^sci-(\w+)\.md$", f)
        if m:
            for t in g.subjects(RDF.type, OGC.Trace):
                if str(g.value(t, OGC.page)) == m.group(1):
                    for src in g.objects(t, OGC.restsOn):
                        if (src, RDF.type, OGC.Source) in g:
                            add(local(src), essential=local(t))
        if f in ("popper.md", "popper-back.md"):
            for r in g.subjects(RDF.type, OGC.Crosswalk):
                src = g.value(r, OGC.cites)
                if src is not None:
                    add(local(src), str(g.value(r, OGC.locator) or ""))
                for also in g.objects(r, OGC.also):
                    add(local(also), "as the source of those definitions")
    return {k: {"locators": sorted(v["locators"]), "essentials": sorted(v["essentials"])}
            for k, v in sorted(cites.items(), key=lambda kv: rank_key(kv[0], g))}


def title_of(g: Graph, key: str) -> str:
    if "entries" not in _cache:
        _cache["entries"] = entries(g)
    return _cache["entries"][key][1]["title"]


def cite_line(g: Graph, key: str, d: dict) -> str:
    where = list(d["locators"])
    if d["essentials"]:
        where.append("essentials " + ", ".join(d["essentials"]))
    locator = f" ({cell('; '.join(where))})" if where else ""
    return f"- {head(g, key)}{locator} {{cite:p}}`{key}`"


def render_cited(page: str, g: Graph | None = None) -> str:
    g = g or _G()
    cites = page_citations(page, g)
    lines = [cite_line(g, key, d) for key, d in cites.items()]
    return "\n".join(lines) + "\n"


def render_cited_all(g: Graph | None = None) -> str:
    g = g or _G()
    by_source = {}
    titles = {}
    for page, path in PAGES.items():
        titles[page] = path.read_text().splitlines()[0].lstrip("# ")
        for key in page_citations(page, g):
            by_source.setdefault(key, []).append(page)
    keys = sorted((local(s) for s in g.subjects(RDF.type, OGC.Source)), key=lambda k: rank_key(k, g))
    lines = ["| Rank | Source | Cited on |", "|---|---|---|"]
    for key in keys:
        pages = by_source.get(key, [])
        links = ", ".join(f"[{titles[p]}]({'../index.md' if p == 'index' else p + '.md'})" for p in pages) or "no page: in the register, cited by no term, step or essential a page renders"
        lines.append(f"| {cell(g.value(SRC[key], OGC.rank))} | {head(g, key)} {{cite:p}}`{key}` | {links} |")
    extra = [k for k in entries(g) if k not in keys]
    if extra:
        lines += ["", "Also in the bibliography, kept from the hand-written file and cited by no page's terms or tables: "
                  + "; ".join(f"{head(g, k)} {{cite:p}}`{k}`" for k in extra) + "."]
    return "\n".join(lines) + "\n"


def main() -> int:
    g = _G()
    (ROOT / "references.bib").write_text(render_bib(g))
    OUT.mkdir(exist_ok=True)
    for page in PAGES:
        (OUT / f"cited-{page}.md").write_text(render_cited(page, g))
    (OUT / "cited-all.md").write_text(render_cited_all(g))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
