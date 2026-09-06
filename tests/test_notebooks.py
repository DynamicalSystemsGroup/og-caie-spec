"""The "Checked" notebooks are computational proof of the chapters' Checked
blocks: every shape the block names is exercised in the notebook it links
to, every counterexample the block describes is run there, the notebook
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
CHECKED_BLOCK = re.compile(r":::\{admonition\} Checked\n(.*?)\n:::", re.S)
SHAPE_ID = re.compile(r"\b[SM]\d-\w+\b")
SHAPE_RANGE = re.compile(r"\b([SM])(\d) to \1(\d)\b")  # "S1 to S8": every shape of those groups in its file
SHAPE_FILES = {"S": "shapes/epo.shapes.ttl", "M": "shapes/model.shapes.ttl"}
PROOF_LINK = re.compile(r"Computational proof: \[run the checks\]\(\.\./notebooks/(checked-[\w-]+\.ipynb)\)\.$")
CHAPTERS = ["contracting.md", "evaluation.md", "model.md", "guarantees.md"]
# The counterexamples each chapter's Checked block describes in prose, by file
# name, since the prose names the fault and not the file.
COUNTEREXAMPLES = {
    "contracting.md": ["requirements-before-agreement.ttl", "population-unrepresented.ttl", "no-obligation.sysml"],
    "evaluation.md": ["attestation-without-evidence.ttl", "attestation-off-plan.ttl", "attestation-off-turn.ttl",
                      "probe-before-requirements.ttl", "recommendation-untraced.ttl", "expert-administers-tests.ttl",
                      "executive-attests.ttl", "unwired-port.sysml", "expert-administers-tests.sysml"],
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
    m = CHECKED_BLOCK.search((ROOT / "docs" / name).read_text())
    assert m, f"{name}: no Checked block"
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
    block = checked_block(name)
    m = PROOF_LINK.search(block.rstrip())
    assert m, f"{name}: the Checked block does not end with the computational-proof sentence"
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
    last = toc[-1]
    assert last.get("title") == "Appendix B: computational proofs", last
    listed = {ROOT / e["file"] for e in last["children"]}
    assert listed == set(NOTEBOOKS)
    for entry in toc[:-1]:
        assert not str(entry.get("file", "")).startswith("notebooks/"), entry
