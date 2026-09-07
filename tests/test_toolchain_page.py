"""Appendix D (toolchain and reproducibility) is rendered from the files that
pin the toolchain, never typed: the fragment regenerates byte-identically;
every direct dependency of pyproject.toml appears with the version uv.lock
pins; the pinned converter digests appear; every step of the gate appears in
the gate's order; the page exists, closes the table of contents, starts
with its title, and keeps the house rules (no em-dash, no retired word)."""
import re
import sys
import tomllib

import yaml

from conftest import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import render_toolchain as rt  # noqa: E402

PAGE = ROOT / "docs" / "appendix-toolchain.md"
FRAGMENT = ROOT / "generated" / "toolchain.md"
RETIRED = {"adequacy", "adequate", "inadequate"}
RECIPE = ["uv sync", "bash toolchain/get-sysml.sh", "bash checks/run-checks.sh", "uv run -q ogc doctor", "uv run myst start", "bash scripts/copy_explorer.sh"]


def fragment() -> str:
    return FRAGMENT.read_text()


def test_fragment_regenerates_byte_identically():
    assert rt.render() == fragment()


def test_every_direct_dependency_appears_with_its_locked_version():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    lock = tomllib.loads((ROOT / "uv.lock").read_text())
    locked = {p["name"]: p["version"] for p in lock["package"]}
    direct = [rt.dep_name(d) for d in project["project"]["dependencies"]] + \
             [rt.dep_name(d) for d in project["dependency-groups"]["dev"]]
    assert len(direct) >= 10
    rows = {m.group(1): m.group(2) for m in re.finditer(r"^\| `([^`]+)` \| (?:runtime|dev) \| [^|]+ \| `([^`]+)` \|$", fragment(), re.M)}
    for name in direct:
        assert name in locked, name
        assert rows.get(name) == locked[name], (name, rows.get(name), locked[name])
    assert set(rows) == set(direct), set(rows) ^ set(direct)
    assert f"`{project['project']['requires-python']}`" in fragment()
    assert f"{len(locked) - 1} packages in all, {len(direct)} direct" in fragment()  # the project itself is not a dependency


def test_the_pinned_converter_digests_appear():
    text = fragment()
    for line in (ROOT / "toolchain" / "sysml-binaries.sha256").read_text().splitlines():
        digest, platform = line.split()
        assert re.search(rf"^\| {platform} \| `{digest}` \| `[0-9a-f]{{64}}` \|$", text, re.M), platform
    for line in (ROOT / "toolchain" / "SHA256SUMS.pinned").read_text().splitlines():
        digest, _ = line.split()
        assert f"`{digest}`" in text, digest
    assert "OpenSysML v0.4.3" in text and "`-convert ttl`" in text


def test_every_gate_step_appears_in_order():
    names = re.findall(r'^step "([^"]+)" \d+ ', ((ROOT / "checks" / "run-checks.sh").read_text() + (ROOT / "checks" / "regen.sh").read_text()), re.M)
    assert len(names) >= 8
    text = fragment()
    positions = [text.find(f"| {i} | {n} |") for i, n in enumerate(names, 1)]
    assert all(p >= 0 for p in positions), dict(zip(names, positions))
    assert positions == sorted(positions)
    assert "scripts/render_toolchain.py" in ((ROOT / "checks" / "run-checks.sh").read_text() + (ROOT / "checks" / "regen.sh").read_text())


def test_ci_steps_and_enforcement_points_appear():
    wf = yaml.safe_load((ROOT / ".github" / "workflows" / "deploy.yml").read_text())
    text = fragment()
    for job, spec in wf["jobs"].items():
        for step in spec["steps"]:
            assert (step.get("name") or step["uses"]) in text, step
    assert "checks/hooks/pre-push" in text and "checks/gate-head.sh" in text and ".cache/gate-head" in text
    assert "github.ref == 'refs/heads/main'" in text


def test_the_page_exists_closes_the_toc_and_keeps_the_house_rules():
    assert PAGE.exists()
    toc = yaml.safe_load((ROOT / "myst.yml").read_text())["project"]["toc"]
    assert toc[-1] == {"file": "docs/appendix-toolchain.md"}
    assert toc[-2] == {"file": "docs/rulings.md"}
    text = PAGE.read_text()
    assert text.startswith("# Appendix D: toolchain and reproducibility\n")
    assert "```{include} ../generated/toolchain.md" in text
    for p in (PAGE, FRAGMENT):
        assert "—" not in p.read_text(), p.name
        for w in RETIRED:
            assert not re.search(rf"\b{w}\b", p.read_text(), re.I), (p.name, w)
    prose = re.sub(r"```.*?```", "", text, flags=re.S)  # the include and the recipe are not prose
    prose = re.sub(r"^#.*$", "", prose, flags=re.M)  # nor are the headings
    assert 350 <= len(prose.split()) <= 900, len(prose.split())  # raised for the ontologies section (R-45) and the reviewer notes
    recipe = re.search(r"```bash\n(.*?)```", text, re.S)
    assert recipe and recipe.group(1).splitlines() == RECIPE, recipe and recipe.group(1)
    assert "CHECKS: PASS" in text and "VERDICT: PASS" in text


def test_every_namespace_in_use_is_registered_and_listed():
    """The ontologies table names every vocabulary the committed graphs use
    (R-45); an unregistered namespace renders as such and fails here."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import render_toolchain as rt
    text = fragment()
    assert "## The ontologies and vocabularies" in text
    assert "(unregistered)" not in text
    for prefix in ("prov", "earl", "skos", "sh", "owl", "sysml", "sysx", "epo", "ogc", "run"):
        assert f"| `{prefix}` |" in text, prefix
    page = (ROOT / "docs" / "appendix-toolchain.md").read_text()
    assert "PROV-O" in page and "EARL" in page and "not in that environment" in page
