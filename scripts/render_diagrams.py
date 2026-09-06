#!/usr/bin/env python3
"""Render model-derived fragments under generated/: the layered OG-CAIE
figure, the assemblage wiring diagram, the SCI table and the satisfy
receipts. Everything is read from model/og-caie.sysml (and the sysml binary
for the receipts), never hand-drawn, so the figures cannot drift from the
model. Deterministic: same model, same bytes."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "model" / "og-caie.sysml"
COUNTER = ROOT / "counterexamples" / "untested-counted-covered.sysml"
SYSML = ROOT / "toolchain" / "bin" / "sysml"
OUT = ROOT / "generated"


def text() -> str:
    return MODEL.read_text()


def steps():
    body = re.search(r"enum def EpoStep \{.*?\*/(.*?)\n    \}", text(), re.S).group(1)
    return re.findall(r"^\s+(\w+);", body, re.M)


def parts():
    humans = re.findall(r"part def (\w+) :> HumanAgent", text())
    machines = re.findall(r"part def (\w+) :> MachineAgent", text())
    return humans, machines


def assembly():
    body = re.search(r"part def OgCaieEvaluation \{(.*?)\n    \}", text(), re.S).group(1)
    usages = dict(re.findall(r"^\s+part (\w+) : (\w+);", body, re.M))
    ifaces = re.findall(r"interface (\w+) : (\w+) connect (\w+)\.(\w+) to (\w+)\.(\w+);", body)
    return usages, ifaces


def sci():
    rows = []
    for sid, name, doc in re.findall(r"requirement def <'(SCI-\d\d)'> (\w+) \{\s*doc /\*(.*?)\*/", text(), re.S):
        doc = re.sub(r"\s+", " ", doc).strip()
        tag, _, statement = doc.partition(". ")
        rows.append((sid, name, tag.strip(), statement.strip()))
    return rows


def facets():
    doc = re.search(r"item def Recommendation \{\s*doc /\*(.*?)\*/", text(), re.S).group(1)
    return re.sub(r"\s+", " ", doc).strip()


def mermaid(block: str) -> str:
    return "```{mermaid}\n" + block.strip() + "\n```\n"


def render_layers() -> str:
    humans, machines = parts()
    st = steps()
    chain = " --> ".join(f"s{i}[{s}]" for i, s in enumerate(st))
    m = f"""flowchart TB
  subgraph EPO["Evaluation Process Ontology: the standard operating procedure, fixed across domains"]
    direction LR
    {chain}
  end
  subgraph DSO["Domain-Specific Ontology: the expert-supplied parameter, one per domain"]
    direction LR
    de[DomainExpert] -- supplies or approves --> dso[(DsoRelease)]
  end
  subgraph EXEC["Execution: the human and machine assemblage performs EPO with DSO"]
    direction LR
    H["humans: {', '.join(humans)}"]
    M["machines: {', '.join(machines)}"]
    H --- rec[(evaluation record)]
    M --- rec
  end
  subgraph INTERP["Interpretation: named humans judge; every judgment traces back"]
    direction LR
    att[attestations: outcome, appropriateness, sufficiency] --> recmd[recommendation]
    recmd -. evidence .-> rec
    recmd -. experiments run .-> rec
    recmd -. assessments and who made them .-> att
    recmd -. DSO release and who approved it .-> dso
    recmd -. EPO step .-> EPO
  end
  EPO ==> EXEC
  DSO ==> EXEC
  EXEC ==> INTERP
"""
    return "## The layers\n\n" + mermaid(m)


def render_wiring() -> str:
    humans, machines = parts()
    usages, ifaces = assembly()
    lines = ["flowchart LR"]
    for u, t in usages.items():
        shape = f'{u}(["{u} : {t}"])' if t in humans else f'{u}[["{u} : {t}"]]'
        lines.append("  " + shape)
    for name, itype, a, pa, b, pb in ifaces:
        lines.append(f"  {a} -- \"{name}\" --> {b}")
    lines.append("  classDef human fill:#e8f5e9,stroke:#2e7d32;")
    lines.append("  classDef machine fill:#fce4ec,stroke:#ad1457;")
    lines.append("  class " + ",".join(u for u, t in usages.items() if t in humans) + " human;")
    lines.append("  class " + ",".join(u for u, t in usages.items() if t in machines) + " machine;")
    return "## The assemblage\n\nHumans are rounded (green), machines are boxed (red); every edge is one interface usage, named as in the model.\n\n" + mermaid("\n".join(lines))


def render_sci() -> str:
    lines = ["| ID | Name | Checked by | Statement |", "|---|---|---|---|"]
    for sid, name, tag, statement in sci():
        lines.append(f"| {sid} | {name} | {tag} | {statement} |")
    n = len(sci())
    human = sum(1 for r in sci() if "human" in r[2])
    return f"## The essentials\n\n{n} requirements: {n - human} verified by machine alone; {human} checked by machine for form, with the judgment itself made by a named person.\n\n" + "\n".join(lines) + "\n"


def receipt(args, title):
    r = subprocess.run([str(SYSML), *args], cwd=ROOT, capture_output=True, text=True)
    body = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if l.strip())
    return f"### {title}\n\n```text\n$ sysml {' '.join(str(a) for a in args)}\n{body}\n(exit {r.returncode})\n```\n"


def render_receipts() -> str:
    rel = lambda p: str(Path(p).relative_to(ROOT)) if isinstance(p, Path) else p
    return ("## Receipts\n\n"
            + receipt([rel(MODEL), "-validate", "-strict"], "Strict validation")
            + receipt([rel(MODEL), "-satisfy=OGCAIE::Runs"], "Every requirement holds on the measles run")
            + receipt([rel(MODEL), rel(COUNTER), "-satisfy=UntestedCountedCovered"], "The counterexample fails, as it must"))


def main() -> int:
    OUT.mkdir(exist_ok=True)
    (OUT / "layers.md").write_text(render_layers())
    (OUT / "wiring.md").write_text(render_wiring())
    (OUT / "sci.md").write_text(render_sci())
    (OUT / "receipts.md").write_text(render_receipts())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
