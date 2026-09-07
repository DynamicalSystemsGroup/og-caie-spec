"""The knowledge graph explorer (ruling R-39) is a view of the same graphs:
it regenerates byte-identically, every link joins two nodes, every view
states both halves of its perspective, every term, ruling, concern,
essential, shape, seam and record item is a node, every node names the
`ogc` command that prints it, the page carries no timestamp of its own,
the appendix that embeds it is in the site's table of contents, and focus
mode (ruling R-48: a node and its neighbourhood, everything else faded or
hidden) is a matter of the page alone, never of the data."""
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
EV = "https://w3id.org/og-caie/evaluation/measles#"
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
    rg = load("track/measles-evaluation.ttl")
    record = {str(s) for s in rg.subjects() if isinstance(s, URIRef) and str(s).startswith(EV)}
    assert by_cls["record"] | by_cls["agent"] == record
    assert len(by_cls["term"]) > 50 and len(by_cls["seam"]) > 30 and len(record) > 40


def test_record_nodes_carry_the_synthetic_tag_and_the_model_realizes_the_epo():
    """Sheet 10-43: every record node says whether it is synthetic (the measles evaluation is, wholly), so the page can filter on it;
    no other node carries the attribute. Sheet 10-33: the join between the model and the EPO is the graph's own realizes link."""
    m = model()
    for n in m["nodes"]:
        if n["cls"] in ("record", "agent"):
            assert n["synthetic"] is True, n["id"]
        else:
            assert "synthetic" not in n, n["id"]
    rels = {l["rel"] for l in m["links"]}
    assert "realizes" in rels and "corresponds" not in rels
    assert sum(1 for l in m["links"] if l["rel"] == "realizes") == 43


def test_the_merged_data_file_is_every_graph_in_one():
    """Sheet 10-31: explorer/data/all.ttl holds every data file in one default graph, the precondition of the shapes and the queries;
    it is the one file the SPARQL box loads, and it parses to the sum of the parts."""
    from rdflib import Graph
    parts = Graph()
    for f in (*rx.SOURCE_FILES, rx.MODEL_FILE, rx.RECORD_FILE):
        parts.parse(ROOT / f)
    merged = Graph().parse(ROOT / "explorer" / "data" / rx.MERGED_FILE)
    assert len(merged) == len(parts) and len(merged) > 10000
    assert rx.data_files() == [rx.MERGED_FILE]
    assert (ROOT / "explorer" / "data" / "measles-evaluation.ttl").exists() and not (ROOT / "explorer" / "data" / "measles-run.ttl").exists()


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
    assert text.startswith("# Appendix A: the knowledge graph explorer")
    assert "```{iframe} explorer/index.html" in text and "(../explorer/index.html)" in text
    assert "—" not in text
    assert "appendix-explorer.md" in (ROOT / "generated" / "more-contracting.md").read_text()


def test_the_page_has_focus_mode_and_the_data_does_not():
    """Ruling R-48: focus on a node and see only its local neighbourhood.
    The page carries the controls (a depth control 1, 2, 3, a fade or hide
    toggle, an unfocus control), the shortcuts (double-click, Escape, the
    arrows), the legend count of what is shown, and the deep-link parameters
    focus and depth; graph.json is the data and knows nothing of it."""
    html = (ROOT / "explorer" / "index.html").read_text()
    for control in ('id="focusbar"', 'data-depth="1"', 'data-depth="2"', 'data-depth="3"', 'id="unfocus"', 'id="hidemode"', 'id="count"'):
        assert control in html, control
    for key in ('"Escape"', '"ArrowRight"', '"ArrowLeft"', '"dblclick"', 'p.get("focus")', 'p.get("depth")', 'p.set("focus","1")', 'p.set("depth"'):
        assert key in html, key
    assert "of ${nodes.length} nodes" in html  # the legend counts what is shown against the view
    assert "double-click to focus" in html
    m = model()
    assert set(m) == {"detail", "families", "links", "nodes", "title", "views"}
    assert not any("focus" in n or "depth" in n for n in m["nodes"])
    assert set(m["views"][0]) == {"id", "label", "focus", "leaves_out", "present"}  # a view's focus is its perspective, not the mode
    assert "focus" in (ROOT / "docs" / "appendix-explorer.md").read_text().lower()
