"""The "Checked" notebooks are computational proof of the chapters' Checked
sections: every shape the section names is exercised in the notebook its
Verdict box links to, every counterexample the section describes is run there, the notebook
executes cleanly with nbclient, its committed outputs equal a fresh
execution (the site renders the committed outputs), it ends with the
verdict line, and its outputs carry no date, path or object address."""
import re
import sys

import nbformat
import pytest
import yaml
from rdflib import RDF, Namespace

from conftest import ROOT, load
from ogc import executor

sys.path.insert(0, str(ROOT / "scripts"))
from execute_notebooks import NOTEBOOKS, VERDICT, execute, outputs, stale  # noqa: E402

SH = Namespace("http://www.w3.org/ns/shacl#")
CHECKED_SECTION = re.compile(r"\n## Checked\n(.*?)\n## There is more in the model\n", re.S)
CHECKED_BLOCK = re.compile(r":::\{admonition\} Verdict\n(.*?)\n:::", re.S)  # the verdict box inside the section
SHAPE_ID = re.compile(r"\b[SM]\d-\w+\b")
SHAPE_RANGE = re.compile(r"\b([SM])(\d) to \1(\d)\b")  # "S1 to S8": every shape of those groups in its file
SHAPE_FILES = {"S": "shapes/epo.shapes.ttl", "M": "shapes/model.shapes.ttl"}
PROOF_LINK = re.compile(r"Computational proof: \[run the checks\]\(\.\./notebooks/(checked-[\w-]+\.ipynb)\)\.$")
CHAPTERS = ["contracting.md", "evaluation.md", "model.md", "guarantees.md"]
# The counterexamples each chapter's Checked block describes in prose, by file
# name, since the prose names the fault and not the file.
COUNTEREXAMPLES = {
    "contracting.md": ["requirements-before-agreement.ttl", "population-unrepresented.ttl", "engagement-mismatch.ttl", "no-obligation.sysml",
                       "one-person-team.ttl", "independence-undeclared.ttl", "acceptance-by-organization.ttl", "member-untagged.ttl"],  # sheet 10: 10-13, 10-07, 10-06; round four, KG 9
    "evaluation.md": ["attestation-without-evidence.ttl", "attestation-off-plan.ttl", "attestation-off-turn.ttl",
                      "probe-before-requirements.ttl", "recommendation-untraced.ttl", "expert-administers-tests.ttl",
                      "executive-attests.ttl", "unwired-port.sysml", "expert-administers-tests.sysml",
                      "cherry-picked-determination.ttl", "insufficient-yet-failed.ttl", "requirement-set-unapproved.ttl", "deviation-unrecorded.ttl",
                      "deviation-by-expert.ttl", "session-on-another-item.ttl", "final-report-without-verdict.ttl", "verdict-without-digests.ttl", "coverage-without-digests.ttl",
                      "recommendation-unapproved.ttl", "draft-without-gaps.ttl", "draft-rates-from-later.ttl", "draft-approved.ttl",
                      "fit-despite-failure.ttl"],  # sheet 10: 10-14, 10-12, 10-01, 10-16, 10-17, 10-41, 10-18, 10-11; R-51 (10-48): the draft, the follow-up, the fitness
    "model.md": ["requirements-before-agreement.ttl"],
    "guarantees.md": [],  # its counterexamples are the executor's mutations, built in memory: see CHECKS
}
# The guarantees chapter's Checked block names checks and mutations rather
# than shapes; its notebook must call them by name.
CHECKS = {
    "guarantees.md": ["executor.demonstrate(", "executor.execute(", "isomorphic(", *(f'"{m}"' for m in executor.MUTATIONS)],
}
RETIRED = {"adequacy", "adequate", "inadequate"}


def checked_block(name):
    """The chapter's Checked section: the prose naming the shapes and the counterexamples, and the Verdict box."""
    m = CHECKED_SECTION.search((ROOT / "docs" / name).read_text())
    assert m, f"{name}: no Checked section"
    return m.group(1)


def named_shapes(block):
    """The shape ids a Checked block names, one by one or as a range such as
    'S1 to S8', which stands for every shape of those groups in its file."""
    names = set(SHAPE_ID.findall(block))
    for letter, lo, hi in SHAPE_RANGE.findall(block):
        for s in load(SHAPE_FILES[letter]).subjects(RDF.type, SH.NodeShape):
            n = str(s).rsplit("/", 1)[-1]
            if n[0] == letter and int(lo) <= int(n[1]) <= int(hi):
                names.add(n)
    return sorted(names)


def linked_notebook(name):
    box = CHECKED_BLOCK.search(checked_block(name))
    assert box, f"{name}: no Verdict box in the Checked section"
    m = PROOF_LINK.search(box.group(1).rstrip())
    assert m, f"{name}: the Verdict box does not end with the computational-proof sentence"
    path = ROOT / "notebooks" / m.group(1)
    assert path.exists(), path
    return path


def source(nb):
    return "\n".join(c.source for c in nb.cells if c.cell_type == "code")


@pytest.fixture(scope="module")
def executed():
    """{path: freshly executed notebook}; execution raises on any failing cell."""
    return {path: execute(path) for path in NOTEBOOKS}


def test_there_is_a_notebook_per_chapter():
    assert {linked_notebook(c) for c in CHAPTERS} == set(NOTEBOOKS)


@pytest.mark.parametrize("chapter", CHAPTERS)
def test_every_named_shape_and_counterexample_is_exercised(chapter):
    nb = nbformat.read(linked_notebook(chapter), as_version=4)
    code = source(nb)
    required = [f'"{s}"' for s in named_shapes(checked_block(chapter))] + CHECKS.get(chapter, [])
    assert required, chapter
    missing = [t for t in required if t not in code]
    assert not missing, f"{chapter}: claimed but not exercised: {missing}"
    for cx in COUNTEREXAMPLES[chapter]:
        assert f'"{cx}"' in code, f"{chapter}: counterexample {cx} not exercised"
        assert (ROOT / "counterexamples" / cx).exists() or (ROOT / "counterexamples" / "model" / cx).exists(), cx


def test_committed_outputs_equal_fresh_execution_and_end_with_the_verdict(executed):
    for path, fresh in executed.items():
        assert not stale(path, fresh), stale(path, fresh)
        assert outputs(fresh)[-1].rstrip().endswith(VERDICT)


def test_every_claim_is_an_assert_and_is_counted(executed):
    for path, fresh in executed.items():
        cells = [c for c in fresh.cells if c.cell_type == "code"]
        claims = 0
        for c in cells:
            n = c.source.count("checked.passed(")
            if n:
                assert "assert " in c.source, f"{path.name}: a claim without an assert in the same cell"
                claims += n
        assert claims >= 1, path.name
        assert f"claims checked: {claims}" in outputs(fresh)[-1], path.name


def test_outputs_are_deterministic_in_kind(executed):
    for path, fresh in executed.items():
        text = "\n".join(outputs(fresh))
        assert not re.search(r"\b\d{4}-\d{2}-\d{2}\b", text), f"{path.name}: a date in the outputs"
        assert not re.search(r"(^|[\s(\"'])/(Users|home|tmp|private|var|opt)/", text), f"{path.name}: an absolute path"
        assert " at 0x" not in text, f"{path.name}: an object address"


def test_notebook_prose_follows_the_house_rules():
    for path in NOTEBOOKS:
        nb = nbformat.read(path, as_version=4)
        prose = "\n".join(c.source for c in nb.cells if c.cell_type == "markdown")
        assert "—" not in prose, f"{path.name}: em-dash"
        for w in RETIRED:
            assert not re.search(rf"\b{w}\b", prose, re.I), f"{path.name}: retired word {w}"
        assert nb.cells[0].cell_type == "markdown" and nb.cells[0].source.startswith("# Checked: "), path.name


def test_notebooks_are_the_last_toc_section_off_the_main_path():
    toc = yaml.safe_load((ROOT / "myst.yml").read_text())["project"]["toc"]
    files = [e.get("file") for e in toc]
    blocks = [e for e in toc if e.get("title") == "Appendix C: computational proofs"]  # C since the sample report became Appendix A (sheet 10 item 10-44)
    assert len(blocks) == 1, toc
    last = blocks[0]
    # off the main path: after the conclusion, Appendix A (the report) and Appendix B (the explorer); only Appendix D (the rulings), Appendix E (the toolchain) and Appendix F (works cited, R-48) follow
    assert toc.index(last) > files.index("docs/appendix-explorer.md") > files.index("docs/appendix-report.md") > files.index("docs/conclusion.md")
    assert [e.get("file") for e in toc[toc.index(last) + 1:]] == ["docs/rulings.md", "docs/appendix-toolchain.md", "docs/appendix-works-cited.md"]
    listed = {ROOT / e["file"] for e in last["children"]}
    assert listed == set(NOTEBOOKS)
    for entry in toc[:-1]:
        assert not str(entry.get("file", "")).startswith("notebooks/"), entry
