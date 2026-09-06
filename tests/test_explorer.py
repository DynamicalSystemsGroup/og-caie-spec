"""The knowledge graph explorer (ruling R-39) is a view of the same graphs:
it regenerates byte-identically, every link joins two nodes, every view
states both halves of its perspective, every term, ruling, concern,
essential, shape, seam and record item is a node, every node names the
`ogc` command that prints it, the page carries no timestamp of its own,
and the appendix that embeds it is in the site's table of contents."""
import json
import re
import sys

import yaml
from rdflib import RDF, Namespace, URIRef

from conftest import ROOT, load

sys.path.insert(0, str(ROOT / "scripts"))
import render_explorer as rx  # noqa: E402

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
SH = Namespace("http://www.w3.org/ns/shacl#")
SYS = Namespace("https://www.omg.org/spec/SysML#")
OGC = Namespace("https://w3id.org/og-caie/")
RUN = "https://w3id.org/og-caie/run/measles#"
EXPECTED_VIEWS = ["vocabulary", "rulings", "process", "wiring", "record", "essentials", "crosswalk", "everything"]


def model():
    return json.loads((ROOT / "explorer" / "graph.json").read_text())


def test_explorer_regenerates_byte_identically():
    fresh = rx.Builder(rx.graph()).build()
    assert json.dumps(fresh, ensure_ascii=False, sort_keys=True, indent=1) + "\n" == (ROOT / "explorer" / "graph.json").read_text()
    assert rx.render(fresh) == (ROOT / "explorer" / "index.html").read_text()


def test_every_link_joins_two_nodes():
    m = model()
    ids = {n["id"] for n in m["nodes"]}
    assert len(ids) == len(m["nodes"])
    for l in m["links"]:
        assert l["source"] in ids and l["target"] in ids and l["rel"], l
    for nid, d in m["detail"].items():
        assert nid in ids
        for _, o in d["out"] + d["in"]:
            assert ("ref" in o and o["ref"] in ids) or ("text" in o), (nid, o)


def test_every_view_states_both_halves_of_its_perspective():
    m = model()
    assert [v["id"] for v in m["views"]] == EXPECTED_VIEWS
    ids = {n["id"] for n in m["nodes"]}
    for v in m["views"]:
        assert v["focus"].strip().endswith(".") and len(v["focus"].split()) >= 6, v["id"]
        assert v["leaves_out"].strip().endswith(".") and len(v["leaves_out"].split()) >= 6, v["id"]
        assert v["present"] and set(v["present"]) <= ids, v["id"]
    assert set(next(v for v in m["views"] if v["id"] == "everything")["present"]) == ids


def test_every_term_ruling_concern_essential_shape_seam_and_record_item_is_a_node():
    m = model()
    by_cls = {}
    for n in m["nodes"]:
        by_cls.setdefault(n["cls"], set()).add(n["id"])
    g = load("vocabulary/og-caie.ttl", "rulings/adjudications.ttl", "model/trace.ttl", "shapes/epo.shapes.ttl", "shapes/model.shapes.ttl")
    assert by_cls["term"] == {str(t) for t in g.subjects(RDF.type, SKOS.Concept)}
    assert by_cls["ruling"] == {str(r) for r in g.subjects(RDF.type, OGC.Ruling)}
    assert by_cls["concern"] == {str(c) for c in g.subjects(RDF.type, OGC.Concern)}
    assert by_cls["sci"] == {str(t) for t in g.subjects(RDF.type, OGC.Trace)}
    assert by_cls["shape"] == {str(s) for s in g.subjects(RDF.type, SH.NodeShape)}
    mg = load("model/og-caie.model.ttl")
    assert by_cls["seam"] == {str(s) for s in mg.subjects(RDF.type, SYS.InterfaceUsage)}
    assert by_cls["part"] == {str(s) for s in mg.subjects(RDF.type, SYS.PartDefinition)}
    rg = load("track/measles-run.ttl")
    record = {str(s) for s in rg.subjects() if isinstance(s, URIRef) and str(s).startswith(RUN)}
    assert by_cls["record"] | by_cls["agent"] == record
    assert len(by_cls["term"]) > 50 and len(by_cls["seam"]) > 30 and len(record) > 40


def test_no_node_lacks_an_ogc_command_or_a_description():
    for n in model()["nodes"]:
        assert n["ogc"].startswith("ogc "), n["id"]
        assert n["label"] and n["desc"], n["id"]
        assert n["page"] == "" or n["page"].startswith("../"), n["id"]


def test_the_page_carries_no_timestamp_of_its_own():
    """Dates in the page are the graph's own (rulings, the record); nothing
    is stamped at render time, so the same graphs give the same bytes."""
    html = (ROOT / "explorer" / "index.html").read_text()
    d3 = (ROOT / "explorer" / "vendor" / "d3.v7.min.js").read_text()
    assert d3 in html
    ours = html.replace(d3, "")  # the vendored library is a fixed blob, checked apart from what this repository writes
    sources = "".join((ROOT / f).read_text() for f in (*rx.SOURCE_FILES, rx.MODEL_FILE, rx.RECORD_FILE))
    for stamp in set(re.findall(r"(?<![\d-])\d{4}-\d{2}-\d{2}(?:T[\d:]+Z?)?", ours)):
        assert stamp in sources, stamp
    assert not re.search(r"(?i)(generated|rendered|built) (at|on) \d", ours)


def test_the_appendix_exists_is_in_the_toc_and_embeds_the_explorer():
    page = ROOT / "docs" / "appendix-explorer.md"
    assert page.exists()
    cfg = yaml.safe_load((ROOT / "myst.yml").read_text())
    files = [e.get("file") for e in cfg["project"]["toc"]]
    # the appendix follows the conclusion; the notebooks section (off the main path) closes the toc
    assert files[files.index("docs/conclusion.md") + 1] == "docs/appendix-explorer.md"
    text = page.read_text()
    assert text.startswith("# Appendix: the knowledge graph explorer")
    assert "```{iframe} explorer/index.html" in text and "(../explorer/index.html)" in text
    assert "—" not in text
    assert "appendix-explorer.md" in (ROOT / "generated" / "more-contracting.md").read_text()
