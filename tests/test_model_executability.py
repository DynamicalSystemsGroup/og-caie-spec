"""The SysML model validates strictly, every SCI requirement holds on the
measles run, and the counterexample fails on exactly the requirement it is
built to violate. Exit codes are those of the sysml process itself."""
import subprocess

import pytest

from conftest import ROOT

SYSML = ROOT / "toolchain" / "bin" / "sysml"
MODEL = ROOT / "model" / "og-caie.sysml"
COUNTER = ROOT / "counterexamples" / "untested-counted-covered.sysml"
SCI = [f"sci0{i}" for i in range(1, 10)]


def run(*args):
    return subprocess.run([str(SYSML), *args], cwd=ROOT, capture_output=True, text=True)


@pytest.fixture(scope="module", autouse=True)
def toolchain():
    if not SYSML.exists():
        r = subprocess.run(["bash", "toolchain/get-sysml.sh"], cwd=ROOT, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr


def test_model_validates_strictly():
    r = run(str(MODEL), "-validate", "-strict")
    assert r.returncode == 0, r.stdout + r.stderr


def test_every_sci_requirement_holds_on_measles_run():
    r = run(str(MODEL), "-satisfy=OGCAIE::Runs")
    assert r.returncode == 0, r.stdout + r.stderr
    for s in SCI:
        assert f"satisfy {s} holds" in r.stdout, s
    assert "could not be evaluated" not in r.stdout


def test_counterexample_validates_and_fails_on_sci07_only():
    r = run(str(MODEL), str(COUNTER), "-validate", "-strict")
    assert r.returncode == 0, r.stdout + r.stderr
    r = run(str(MODEL), str(COUNTER), "-satisfy=UntestedCountedCovered")
    assert r.returncode != 0
    assert "satisfy sci07 fails" in r.stdout
    assert "a3.covered implies" in r.stdout and "attestationCount >= 1" in r.stdout


def test_nine_requirement_defs_each_tagged_machine_or_human():
    text = MODEL.read_text()
    import re
    blocks = re.findall(r"requirement def <'(SCI-\d\d)'> \w+ \{\s*doc /\*(.*?)\*/", text, re.S)
    assert [b[0] for b in blocks] == [f"SCI-0{i}" for i in range(1, 10)]
    for sid, doc in blocks:
        head = doc.strip().split(".")[0]
        assert head.startswith("machine") or head.startswith("human"), f"{sid}: doc must open with the tag"
