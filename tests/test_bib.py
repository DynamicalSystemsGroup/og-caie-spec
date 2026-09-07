"""The works-cited apparatus (ruling R-48): references.bib is rendered from
the source register, every registered source has an entry under its own
key, the file parses, every main-path page closes with a "Sources cited"
section whose fragment names exactly the sources the page's terms and
tables cite, the aggregate table lists every source, Appendix F is the last
page of the table of contents and cites every entry, and the site builds
without a citation warning."""
import re
import subprocess
import sys

import yaml
from rdflib import RDF

from conftest import OGC, ROOT, load

sys.path.insert(0, str(ROOT / "scripts"))
import render_bib as rb  # noqa: E402

BIB = ROOT / "references.bib"
APPENDIX = ROOT / "docs" / "appendix-works-cited.md"
CITE = re.compile(r"\{cite:p\}`([^`]+)`")
RETIRED = {"adequacy", "adequate", "inadequate"}


def sources():
    g = load("sources/sources.ttl")
    return sorted(str(s).rsplit("#", 1)[-1] for s in g.subjects(RDF.type, OGC.Source))


def test_bib_regenerates_byte_identically():
    assert rb.render_bib() == BIB.read_text()


def test_every_source_has_an_entry_under_its_own_key():
    entries = rb.parse_bib(BIB.read_text())
    for key in sources():
        assert key in entries, key
        kind, fields = entries[key]
        assert kind in {"misc", "techreport", "book", "article", "inproceedings"}, (key, kind)
        assert fields.get("title"), key
        assert "note" in fields and "posture " in fields["note"] and "rank " in fields["note"], (key, fields.get("note"))


def test_the_bib_parses_and_is_sorted_and_free_of_invented_years():
    text = BIB.read_text()
    entries = rb.parse_bib(text)
    keys = re.findall(r"^@\w+\{([^,]+),$", text, re.M)
    assert keys == sorted(keys) and len(keys) == len(set(keys)), keys
    assert len(entries) == len(keys)
    g = load("sources/sources.ttl")
    for s in g.subjects(RDF.type, OGC.Source):
        key = str(s).rsplit("#", 1)[-1]
        kind, fields = entries[key]
        label = str(g.value(s, rb.RDFS.label))
        if "year" in fields:
            assert fields["year"] in label, (key, fields["year"], label)  # a year comes from the register's label or not at all
        url = g.value(s, OGC.url)
        assert fields.get("url") == (str(url) if url is not None else None), key


def test_hand_written_entries_are_kept():
    entries = rb.parse_bib(BIB.read_text())
    for key in rb.HAND_ENTRIES:
        assert key in entries, key
    # the fields the hand-written file carried and the register lacks travel into the merged entries
    assert entries["hawkins-2011"][1]["booktitle"].startswith("Advances in Systems Safety")
    assert entries["nist-ai-700-2"][1]["doi"] == "10.6028/NIST.AI.700-2"


def test_every_page_closes_with_sources_cited_and_its_fragment_matches_the_graph():
    for page, path in rb.PAGES.items():
        text = path.read_text()
        rel = "generated" if path.parent == ROOT else "../generated"
        tail = f"\n## Sources cited\n\n```{{include}} {rel}/cited-{page}.md\n```\n"
        assert text.endswith(tail), (page, text[-200:])
        assert text.count("\n## Sources cited\n") == 1, page
        headings = re.findall(r"^## (.+)$", text, re.M)
        assert headings[-1] == "Sources cited", (page, headings)
        frag = (ROOT / "generated" / f"cited-{page}.md").read_text()
        assert frag == rb.render_cited(page), page
        cited = CITE.findall(frag)
        assert cited == sorted(cited, key=rb.rank_key) and len(cited) == len(set(cited)), (page, cited)
        assert set(cited) == set(rb.page_citations(page)), (page, set(cited) ^ set(rb.page_citations(page)))
        assert cited, page
        assert set(cited) <= set(sources()), page


def test_the_bookends_cite_the_session_and_popper():
    for page in ("index", "conclusion"):
        cited = set(rb.page_citations(page))
        assert {"scipy-2026-bof", "popper-1959"} <= cited, (page, cited)


def test_the_aggregate_table_lists_every_source_with_its_pages():
    frag = (ROOT / "generated" / "cited-all.md").read_text()
    assert frag == rb.render_cited_all()
    cited = CITE.findall(frag)
    assert set(sources()) <= set(cited), set(sources()) - set(cited)
    assert set(cited) == set(rb.parse_bib(BIB.read_text())), set(cited) ^ set(rb.parse_bib(BIB.read_text()))
    for page, path in rb.PAGES.items():
        title = path.read_text().splitlines()[0].lstrip("# ")
        for key in rb.page_citations(page):
            row = next(l for l in frag.splitlines() if f"{{cite:p}}`{key}`" in l)
            assert title in row, (key, page, row)


def test_appendix_f_exists_is_last_in_the_toc_and_keeps_the_house_rules():
    assert APPENDIX.exists()
    toc = yaml.safe_load((ROOT / "myst.yml").read_text())["project"]["toc"]
    assert toc[-1] == {"file": "docs/appendix-works-cited.md"}
    assert toc[-2] == {"file": "docs/appendix-toolchain.md"}
    cfg = yaml.safe_load((ROOT / "myst.yml").read_text())["project"]
    assert cfg["bibliography"] == ["references.bib"]
    text = APPENDIX.read_text()
    assert text.startswith("# Appendix F: works cited\n")  # F since the sample report became Appendix A (sheet 10 item 10-44)
    assert "```{include} ../generated/cited-all.md" in text
    assert "```{bibliography}\n```" in text
    assert "—" not in text  # the fragments may carry a source's own title verbatim; the prose may not
    for p in (APPENDIX, *sorted((ROOT / "generated").glob("cited-*.md"))):
        for w in RETIRED:
            assert not re.search(rf"\b{w}\b", p.read_text(), re.I), (p.name, w)


def test_the_site_builds_without_a_citation_warning():  # needs the network once, for the MyST theme (sheet 10-39)
    r = subprocess.run(["uv", "run", "myst", "build", "--html"], cwd=ROOT, capture_output=True, text=True)
    out = r.stdout + r.stderr
    assert r.returncode == 0, out[-2000:]
    noisy = [l for l in out.splitlines() if ("⚠" in l or "warn" in l.lower() or "error" in l.lower())
             and re.search(r"cit|bib", l, re.I)]
    assert not noisy, noisy


def test_every_source_names_its_bibtex_key_and_the_cited_through_list_regenerates():
    """Sheet 10-40 (R-50): the register carries the key the bibliography uses; the standards quoted through
    SEVOCAB and the SEBoK are listed from the locators (the professor's M14)."""
    g = rb.graph()
    for s in g.subjects(RDF.type, OGC.Source):
        assert str(g.value(s, OGC.bibkey)) == rb.local(s), s
    keys = set(rb.entries(g))
    assert all(str(g.value(s, OGC.bibkey)) in keys for s in g.subjects(RDF.type, OGC.Source))
    text = rb.render_cited_through(g)
    assert text == (ROOT / "generated" / "cited-through.md").read_text()
    assert "ISO/IEC/IEEE 29119-2:2021" in text and "| sevocab |" in text
