#!/usr/bin/env python3
"""Render generated/toolchain.md, the tables of Appendix E, from the files
that pin the toolchain, never from prose: pyproject.toml and uv.lock (the
Python requirement, the direct dependencies with their locked versions, the
count of packages resolved), model/model_manifest.json and toolchain/ (the
pinned OpenSysML release, the per-platform digests, the converter
identity), the vendored browser libraries' NOTICE and header (versions and
licences as they state them), checks/run-checks.sh (the gate's steps in
order), .github/workflows/deploy.yml (the CI jobs and steps) and the
enforcement points (the pre-push hook, the gate on a detached worktree of
HEAD, CI). Deterministic: same files, same bytes; no timestamp is written.
The gate runs this and diffs generated/."""
from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated" / "toolchain.md"
PYPROJECT = ROOT / "pyproject.toml"
LOCK = ROOT / "uv.lock"
MANIFEST = ROOT / "model" / "model_manifest.json"
FETCH = ROOT / "toolchain" / "get-sysml.sh"
BINARIES = ROOT / "toolchain" / "sysml-binaries.sha256"
TARBALLS = ROOT / "toolchain" / "SHA256SUMS.pinned"
D3 = ROOT / "explorer" / "vendor" / "d3.v7.min.js"
OXIGRAPH_NOTICE = ROOT / "explorer" / "vendor" / "oxigraph" / "NOTICE.md"
GATE = ROOT / "checks" / "run-checks.sh"
GATE_HEAD = ROOT / "checks" / "gate-head.sh"
HOOK = ROOT / "checks" / "hooks" / "pre-push"
WORKFLOW = ROOT / ".github" / "workflows" / "deploy.yml"


def cell(s: object) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def dep_name(spec: str) -> str:
    """The distribution name of a PEP 508 requirement, in uv.lock's form."""
    return re.split(r"[<>=!~\[;@ ]", spec.strip(), maxsplit=1)[0].lower().replace("_", "-")


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def render_environment() -> str:
    project = tomllib.loads(PYPROJECT.read_text())
    lock = tomllib.loads(LOCK.read_text())
    name = project["project"]["name"]
    locked = {p["name"]: p["version"] for p in lock["package"]}
    groups = [("runtime", project["project"]["dependencies"]), ("dev", project["dependency-groups"]["dev"])]
    direct = [(g, dep_name(s), s[len(dep_name(s)):].strip() or "(any)") for g, specs in groups for s in specs]
    total = len(locked) - 1  # the project itself is in the lock but is not a dependency
    lines = ["## The Python environment\n",
             f"Python `{project['project']['requires-python']}` (`{rel(PYPROJECT)}`), pinned to `{(ROOT / '.python-version').read_text().strip()}` by `.python-version` so that `uv sync` installs the same interpreter everywhere. `uv sync` reproduces the environment "
             f"from `{rel(LOCK)}` (lockfile version {lock['version']}, revision {lock['revision']}): "
             f"{total} packages in all, {len(direct)} direct ({sum(1 for g, _, _ in direct if g == 'runtime')} runtime, "
             f"{sum(1 for g, _, _ in direct if g == 'dev')} dev) and {total - len(direct)} transitive, every one pinned to a version "
             f"and a content hash. The project `{name}` is installed editable and provides the `ogc` command.\n",
             "| Package | Group | Constraint (`pyproject.toml`) | Locked (`uv.lock`) |", "|---|---|---|---|"]
    for group, n, spec in direct:
        lines.append(f"| `{n}` | {group} | `{spec}` | `{locked[n]}` |")
    return "\n".join(lines) + "\n"


def render_converter() -> str:
    m = json.loads(MANIFEST.read_text())
    ver = re.search(r'^VER="([^"]+)"', FETCH.read_text(), re.M).group(1)
    base = re.search(r'^BASE="([^"]+)"', FETCH.read_text(), re.M).group(1).replace("${VER}", ver)
    binaries = dict(reversed(line.split()) for line in BINARIES.read_text().split("\n") if line.strip())
    tarballs = dict(reversed(line.split()) for line in TARBALLS.read_text().split("\n") if line.strip())
    lines = ["## The pinned converter\n",
             "| Setting | Value | Read from |", "|---|---|---|",
             f"| Release | {cell(m['converter']['release'])} | `{rel(MANIFEST)}` |",
             f"| Fetched from | `{base}` | `{rel(FETCH)}` (`VER={ver}`) |",
             f"| Invocation | `{cell(m['converter']['invocation'])}` | `{rel(MANIFEST)}` |",
             f"| Digest file | `{cell(m['converter']['pinned_digests'])}`, sha256 `{cell(m['converter']['pinned_digests_sha256'])}` | `{rel(MANIFEST)}` |",
             f"| Authoring source | `{cell(m['source']['path'])}`, sha256 `{cell(m['source']['sha256'])}` | `{rel(MANIFEST)}` |",
             f"| Term map | `{cell(m['term_map']['path'])}`, {m['term_map']['terms']} terms, sha256 `{cell(m['term_map']['sha256'])}` | `{rel(MANIFEST)}` |",
             f"| Canonical graph | `{cell(m['artifact']['path'])}`, {m['artifact']['triples']} triples of {m['raw']['triples']} converted "
             f"(budget {m['triple_budget']['value']}, headroom {m['triple_budget']['headroom']}), sha256 `{cell(m['artifact']['sha256'])}` | `{rel(MANIFEST)}` |",
             "",
             f"Per platform, the digest the installed binary must hash to (`{rel(BINARIES)}`) and the digest the release "
             f"tarball must hash to before it is unpacked (`{rel(TARBALLS)}`); `{rel(FETCH)}` checks both on every run.\n",
             "| Platform | Installed binary sha256 | Release tarball sha256 |", "|---|---|---|"]
    for plat in binaries:
        lines.append(f"| {plat} | `{binaries[plat]}` | `{tarballs[f'opensysml-{plat}.tar.gz']}` |")
    return "\n".join(lines) + "\n"


def render_vendored() -> str:
    header = D3.read_text().split("\n", 1)[0]
    d3_version = re.search(r"\bv(\d+\.\d+\.\d+)\b", header).group(1)
    d3_licence = re.search(r"\b(MIT|ISC|BSD|Apache[^ ]*|GPL[^ ]*|licen[cs]e[^ ]*)\b", header, re.I)
    d3_copyright = re.search(r"Copyright .*$", header).group(0)
    notice = OXIGRAPH_NOTICE.read_text()
    ox_version = re.search(r"`oxigraph` (\d+\.\d+\.\d+)", notice).group(1)
    ox_licence = re.search(r"Licen[cs]e: ([^,\n]+)", notice).group(1)
    ox_source = re.search(r"Source: (\S+)", notice).group(1)
    ox_files = re.findall(r"`(web\w*\.\w+)`", notice)  # the vendored files, not the `web` target name
    lines = ["## The vendored browser libraries\n",
             "Appendix B runs in the browser on two libraries committed under `explorer/vendor/`, "
             "so the explorer loads nothing from the network; Appendix A's report draws with the same d3 file, "
             "loaded by the relative path `../explorer/vendor/d3.v7.min.js`, so there is one copy. Versions and licences are as the files state them.\n",
             "| Library | Version | Licence | Source or copyright | Stated in |", "|---|---|---|---|---|",
             f"| d3 | {d3_version} | {d3_licence.group(1) if d3_licence else 'not stated in the file'} | {cell(d3_copyright)} | `{rel(D3)}` (first line) |",
             f"| oxigraph (WebAssembly, `{'`, `'.join(ox_files)}`) | {ox_version} | {cell(ox_licence)} | <{ox_source}> | `{rel(OXIGRAPH_NOTICE)}` |"]
    return "\n".join(lines) + "\n"


def gate_steps() -> list[tuple[str, str, str]]:
    """(name, expected exit, command) per `step` line of the gate, with a
    helper function's body shown in place of its name."""
    text = GATE.read_text()
    helpers = {m.group(1): " ".join(l.strip() for l in m.group(2).strip().splitlines())
               for m in re.finditer(r"^(\w+)\(\) \{\n(.*?)\n\}", text, re.M | re.S)}
    regen = ROOT / "checks" / "regen.sh"
    inline = " && ".join(l.strip() for l in regen.read_text().splitlines() if l.strip().startswith("uv run")) if regen.exists() else ""
    steps = []
    for name, expect, cmd in re.findall(r'^step "([^"]+)" (\d+) (.+)$', text, re.M):
        cmd = helpers.get(cmd, cmd)
        if inline:
            cmd = cmd.replace("bash checks/regen.sh", f"bash checks/regen.sh ({inline})")
        steps.append((name, expect, cmd))
    return steps


def render_gate() -> str:
    text = GATE.read_text()
    steps = gate_steps()
    verdict = re.search(r'echo "(CHECKS: )\$RESULT', text).group(1)
    log = re.search(r"^LOG=(\S+)", text, re.M).group(1)
    report = re.search(r"> (checks/out/report\.json)", text).group(1)
    lines = ["## The gate\n",
             f"`{rel(GATE)}` runs {len(steps)} steps, every one, in this order; a step passes when its exit code is the expected one. "
             f"The only summary is the `{verdict}PASS` or `{verdict}FAIL` line and `{report}`; each step's full output is in `{log}`. "
             "Nothing is optional and nothing fails quietly.\n",
             "| # | Step | Expected exit | Command |", "|---|---|---|---|"]
    for i, (name, expect, cmd) in enumerate(steps, 1):
        lines.append(f"| {i} | {name} | {expect} | `{cell(cmd)}` |")
    return "\n".join(lines) + "\n"


def render_ci() -> str:
    wf = yaml.safe_load(WORKFLOW.read_text())
    on = wf.get("on") or wf.get(True)  # PyYAML reads a bare `on:` key as boolean True
    def plain(v):
        return ", ".join(map(str, v)) if isinstance(v, list) else str(v)
    triggers = ", ".join(f"{k} ({', '.join(f'{a}: {plain(b)}' for a, b in v.items())})" if isinstance(v, dict) and v else k for k, v in on.items())
    lines = ["## Continuous integration\n",
             f"`{rel(WORKFLOW)}` (workflow `{wf['name']}`) runs on {triggers}. The `checks` job runs the same gate script; "
             f"the `deploy` job needs it and runs only when `{wf['jobs']['deploy']['if']}`.\n",
             "| Job | Step | Runs |", "|---|---|---|"]
    for job, spec in wf["jobs"].items():
        for step in spec["steps"]:
            label = step.get("name") or step["uses"]
            if "run" in step:
                what = f"`{cell(step['run'])}`"
            else:
                what = f"`{step['uses']}`" + (f" ({', '.join(f'{k}: {' '.join(str(v).split())}' for k, v in step['with'].items())})" if step.get("with") else "")
            lines.append(f"| {job} | {cell(label)} | {what} |")
    return "\n".join(lines) + "\n"


def render_enforcement() -> str:
    hook = HOOK.read_text()
    hook_cmd = re.search(r"^bash \S+$", hook, re.M).group(0)
    install = re.search(r"#\s+(git config core\.hooksPath \S+)", hook).group(1)
    gh = GATE_HEAD.read_text()
    m = re.search(r"^WT=\$\(mktemp -d (\S+)\)", gh, re.M) or re.search(r"^WT=(\S+)", gh, re.M)
    wt = m.group(1)  # one worktree per run: the mktemp template names the place
    gh_cmd = re.search(r"cd \"\$WT\" && (bash \S+)", gh).group(1)
    wf = yaml.safe_load(WORKFLOW.read_text())
    ci_cmd = next(s["run"] for s in wf["jobs"]["checks"]["steps"] if s.get("run", "").startswith("bash checks/"))
    lines = ["## Enforcement points\n",
             "The same script gives the verdict at three points; none can be skipped by editing a page.\n",
             "| Where | What runs | Read from |", "|---|---|---|",
             f"| Before every push, in the author's checkout | `{hook_cmd}` (installed with `{install}`) | `{rel(HOOK)}` |",
             f"| On the committed HEAD, in a detached worktree at `{wt}`, never on the working tree | `{gh_cmd}` | `{rel(GATE_HEAD)}` |",
             f"| In CI, on a fresh runner, before any deploy | `{ci_cmd}`; `deploy` needs `{wf['jobs']['deploy']['needs']}` | `{rel(WORKFLOW)}` |"]
    return "\n".join(lines) + "\n"


# The vocabularies the graphs are written in. The register names each
# namespace and its standard; every count below is computed from the
# committed Turtle files, and a namespace in use but not registered here is
# rendered as such so the test catches it.
GRAPH_FILES = ["vocabulary/og-caie.ttl", "vocabulary/epo.ttl", "vocabulary/crosswalk.ttl", "vocabulary/register.ttl", "vocabulary/ogm.ttl", "sources/sources.ttl",
               "rulings/adjudications.ttl", "model/trace.ttl", "model/og-caie.model.ttl", "track/measles-run.ttl",
               "shapes/epo.shapes.ttl", "shapes/model.shapes.ttl", "shapes/rulings.shapes.ttl"]
ONTOLOGIES = [
    ("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "W3C", "RDF 1.1: typing (rdf:type) and lists", "https://www.w3.org/TR/rdf11-concepts/"),
    ("rdfs", "http://www.w3.org/2000/01/rdf-schema#", "W3C", "RDF Schema: labels, comments, subclassing", "https://www.w3.org/TR/rdf-schema/"),
    ("owl", "http://www.w3.org/2002/07/owl#", "W3C", "OWL 2: the EPO's classes and properties", "https://www.w3.org/TR/owl2-overview/"),
    ("xsd", "http://www.w3.org/2001/XMLSchema#", "W3C", "XML Schema datatypes: dates, decimals, booleans", "https://www.w3.org/TR/xmlschema11-2/"),
    ("skos", "http://www.w3.org/2004/02/skos/core#", "W3C", "SKOS: the glossary's concepts, labels, definitions and notes", "https://www.w3.org/TR/skos-reference/"),
    ("prov", "http://www.w3.org/ns/prov#", "W3C", "PROV-O: who did what and when in the record (agents, activities, entities, derivation, attribution)", "https://www.w3.org/TR/prov-o/"),
    ("earl", "http://www.w3.org/ns/earl#", "W3C", "EARL 1.0: assertions with an assertor, a mode, a subject, a test and an outcome (passed, failed, cantTell)", "https://www.w3.org/TR/EARL10-Schema/"),
    ("sh", "http://www.w3.org/ns/shacl#", "W3C", "SHACL: the shapes that check the record, the model graph and the rulings, including SHACL-SPARQL constraints", "https://www.w3.org/TR/shacl/"),
    ("sysml", "https://www.omg.org/spec/SysML#", "OpenSysML (after the OMG SysML v2 metamodel)", "SysML v2 vocabulary as the OpenSysML converter renders the model: definitions, usages, ports, interfaces, actions, successions, flows", "https://www.omg.org/spec/SysML/2.0/"),
    ("sysx", "urn:opensysml:sysml:", "OpenSysML", "the converter's own facts: the ends of a connection, the source text of a statement, a prefix keyword", "https://github.com/OpenMBEE/opensysml"),
    ("elmt", "urn:sysmlv2:element:", "OpenSysML", "the converter's element identifiers, one per model element", "https://github.com/OpenMBEE/opensysml"),
    ("expr", "urn:opensysml:expr:", "OpenSysML", "the converter's expression identifiers (end paths, multiplicity bounds)", "https://github.com/OpenMBEE/opensysml"),
    ("ogc", "https://w3id.org/og-caie/", "this specification", "the register: citation classes and properties, shapes' names, concerns, rulings, crosswalk rows, trace essentials", "https://w3id.org/og-caie/"),
    ("term", "https://w3id.org/og-caie/terms#", "this specification", "the glossary's terms", "https://w3id.org/og-caie/"),
    ("src", "https://w3id.org/og-caie/sources#", "this specification", "the source register", "https://w3id.org/og-caie/"),
    ("rul", "https://w3id.org/og-caie/rulings#", "this specification", "concerns and rulings", "https://w3id.org/og-caie/"),
    ("epo", "https://w3id.org/og-caie/epo#", "this specification", "the Evaluation Process Ontology's handles: item classes, steps, layers, roles and their properties", "https://w3id.org/og-caie/"),
    ("xw", "https://w3id.org/og-caie/crosswalk#", "this specification", "the crosswalk rows of the front page's bridge into the standards", "https://w3id.org/og-caie/"),
    ("tr", "https://w3id.org/og-caie/trace#", "this specification", "the essentials SCI-01 to SCI-13", "https://w3id.org/og-caie/"),
    ("ogm", "https://w3id.org/og-caie/model#", "this specification", "the derived ends of the canonical model graph (resolved ports, flow ends, successions, relations)", "https://w3id.org/og-caie/"),
    ("run", "https://w3id.org/og-caie/run/measles#", "this specification", "the measles record's items and agents", "https://w3id.org/og-caie/"),
]


def render_ontologies() -> str:
    from rdflib import Graph, RDF, URIRef
    g = Graph()
    for f in GRAPH_FILES:
        g.parse(ROOT / f)

    def ns_of(iri: str) -> str:
        hits = [ns for _, ns, *_ in ONTOLOGIES if iri.startswith(ns)]
        if hits:
            return max(hits, key=len)  # the longest prefix: epo# over og-caie/
        return iri.rsplit("#", 1)[0] + "#" if "#" in iri else iri.rsplit("/", 1)[0] + "/"

    classes, preds, subjects = {}, {}, {}
    for s_, p_, o in g:
        preds.setdefault(ns_of(str(p_)), set()).add(str(p_))
        if p_ == RDF.type and isinstance(o, URIRef):
            classes.setdefault(ns_of(str(o)), set()).add(str(o))
        if isinstance(s_, URIRef):
            subjects.setdefault(ns_of(str(s_)), set()).add(str(s_))
    used = set(classes) | set(preds) | set(subjects)
    lines = ["## The ontologies and vocabularies", "",
             "What the graphs are written in, counted over the committed Turtle files (" + ", ".join(f"`{f}`" for f in GRAPH_FILES) + "): "
             "the classes and properties of each vocabulary that the graphs actually use, and the subjects each names. "
             "The W3C vocabularies are adopted as published; the SysML namespace is OpenSysML's rendering of the OMG SysML v2 metamodel, not a vocabulary OMG publishes at that IRI; the specification's own namespaces resolve under w3id.org.\n",
             "| Prefix | Namespace | Whose | What it does here | Classes used | Properties used | Subjects | Reference |", "|---|---|---|---|---|---|---|---|"]
    for prefix, ns, whose, what, ref in ONTOLOGIES:
        if ns not in used:
            continue
        lines.append(f"| `{prefix}` | `{ns}` | {whose} | {what} | {len(classes.get(ns, ()))} | {len(preds.get(ns, ()))} | {len(subjects.get(ns, ()))} | <{ref}> |")
    for ns in sorted(used - {n for _, n, *_ in ONTOLOGIES}):
        lines.append(f"| (unregistered) | `{ns}` | | **not in the register: add it** | {len(classes.get(ns, ()))} | {len(preds.get(ns, ()))} | {len(subjects.get(ns, ()))} | |")
    return "\n".join(lines) + "\n"


def render() -> str:
    return "\n".join([render_environment(), render_converter(), render_ontologies(), render_vendored(), render_gate(), render_ci(), render_enforcement()])


def main() -> int:
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(render())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
