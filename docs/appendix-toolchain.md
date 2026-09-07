# Appendix D: toolchain and reproducibility

This appendix says what the site and its proofs run on, so that a reader
can rebuild every page and verdict on their own machine: the environment
is a lockfile and the reviewer recipe is six lines.

## What executable specification means here

The graphs are the model: the vocabulary, the sources, the rulings, the
essentials, the pruned SysML rendering and the measles evaluation are
Turtle files under version control, and no page states what they cannot
answer by query. The scripts render every figure and table into
`generated/` and the explorer, and the gate regenerates them and diffs
them byte for byte, so a table cannot drift from its graph. The shapes and
the tests are the checks: SHACL over the record and the model graph,
pytest over the prose, the citations and the wiring. The gate is the only
verdict: one script, every step, one line. CI runs the same script on a
fresh runner and deploys the site only when it prints PASS.

The record is a PROV bundle every item and agent is a member of, and the
shapes and the record queries assume one default graph: the record, the
EPO vocabulary and the model graph loaded together, since an item's step
is derived through the model and every global rule is anchored on the
record its focus node belongs to. Two records in one graph do not collide.
A quad store with one named graph per file answers nothing; the explorer
ships one merged file, `explorer/data/all.ttl`, for that reason.

## The layers

From the bottom up. The virtual environment is managed by uv:
`pyproject.toml` declares the direct dependencies, `uv.lock` pins the whole
resolution to versions and content hashes, and `uv sync` reproduces it on
any machine. OpenSysML is not in that environment, on purpose: it is the
modelling tool, used at authoring time for strict validation of the SysML
source and its rendering to RDF, and everything downstream reads only the
RDF; `toolchain/get-sysml.sh` fetches the pinned release as a binary and
checks the tarball and the installed binary against committed digests.
rdflib and pySHACL parse the graphs and run the shapes; pypdf reads the
PDF sources for the quote checks. MyST, the `mystmd` package over Node.js,
builds the site from the pages and the included fragments. nbclient
re-executes the proof notebooks and compares their outputs with the
committed ones. The `ogc` command line reads the graphs for people and AI
assistants; its skill file, `.claude/skills/ogc-glossary/SKILL.md`, tells
an assistant to ask the graph and never to answer from memory. The
vendored d3 and oxigraph run Appendix A in the browser without the network.

The graphs are written in a small set of ontologies, none invented here
beyond the specification's own handles. PROV-O says who did what and when.
EARL says what was asserted, with an outcome of passed, failed or cannot
tell, which is why a determination is never a Boolean. SKOS holds the
glossary. OWL and RDF Schema declare the Evaluation Process Ontology's
classes and properties. SHACL states every check. The SysML v2 vocabulary
is OpenSysML's rendering of the OMG metamodel, with a few tool facts of
its own. The specification's namespaces under w3id.org name the terms, the
sources, the rulings, the essentials, the crosswalk, the derived ends of
the model graph and the measles evaluation. The table below counts what
each is used for.

```{include} ../generated/toolchain.md
```

## The reviewer recipe

From a git clone with git, uv and Node.js 20 or later installed. The
first run needs the network for the interpreter and the wheels, the
converter's tarball and the site theme; a second run is offline. The gate
takes three to four minutes on a laptop, most of it the test suite.

```bash
uv sync
bash toolchain/get-sysml.sh
bash checks/run-checks.sh
uv run -q ogc doctor
uv run myst build --html
bash scripts/copy_explorer.sh
uv run python -m http.server -d _build/html 8000
```

`uv sync` creates `.venv` from the lockfile. `get-sysml.sh` prints
`sysml installed+verified: sysml v0.4.3` on a first fetch and nothing when
the verified binary is in place; a digest mismatch exits 1. The gate prints
each step's name and `pass` or `FAIL`, then `CHECKS: PASS` or `CHECKS:
FAIL` with the commit it judged; that line is what the pre-push hook and
CI require, and a failing step prints its last lines. `ogc doctor` ends
with `VERDICT: PASS` with the commit it judged, after one line per check
and a note per fact that is not a fault. The notebook step prints one line
per notebook, `fresh` or `STALE`, then `NOTEBOOK: PASS` or `NOTEBOOK:
FAIL`; the kernel's warning about an unencrypted local transport is
expected. `myst build --html` writes the site under `_build/html`; the
gate copies Appendix A's explorer next to it, and serving that folder over
http is what makes Appendix A's frame and its SPARQL box work (`myst
start` serves the pages but not the explorer). The fetch script supports
macOS and Linux on x86-64 and arm64 and needs curl, tar and a sha256 tool;
the site build and the notebooks need free local ports.

## The first rung

The appendices are the first rung of backup; the repository is the richer
one, every graph, shape, script, test and notebook the site is rendered
from, with the gate that judges them. A reader need not trust the authors:
run the recipe and read the verdict.
