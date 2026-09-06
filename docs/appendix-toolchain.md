# Appendix D: toolchain and reproducibility

Appendix A opens the model, Appendix B runs its proofs and Appendix C
records the judgments it rests on. This appendix says what all of it runs
on, so that a reader can rebuild every page and verdict on their own
machine: the environment is a lockfile and the reviewer recipe is five
lines.

## What executable specification means here

The graphs are the model: the vocabulary, the sources, the rulings, the
essentials, the pruned SysML rendering and the measles record are Turtle
files under version control, and no page states what they cannot answer by
query. The scripts render every figure and table into `generated/` and the
explorer, and the gate regenerates them and diffs them byte for byte, so a
table cannot drift from its graph. The shapes and the tests are the checks:
SHACL over the record and the model graph, pytest over the prose, the
citations and the wiring. The gate is the only verdict: one script, every
step, one line. CI runs the same script on a fresh runner and deploys the
site only when it prints PASS.

## The layers

From the bottom up. The virtual environment is managed by uv:
`pyproject.toml` declares the direct dependencies, `uv.lock` pins the whole
resolution to versions and content hashes, and `uv sync` reproduces it on
any machine. OpenSysML is not in that environment, and on purpose: it is
the modelling tool, not a runtime dependency. It is used at authoring time
for two jobs, strict validation of the SysML source and its rendering to
RDF, and everything downstream reads only the RDF. So `toolchain/get-sysml.sh`
fetches the pinned release as a binary and checks the tarball and the
installed binary against committed digests, outside the lockfile. rdflib and pySHACL
parse the graphs and run the shapes; pypdf reads the PDF sources for the
quote checks. MyST, the `mystmd` package over Node.js, builds the site from
the pages and the included fragments. nbclient re-executes the proof
notebooks and compares their outputs with the committed ones. The `ogc`
command line, provided by the project package, reads the graphs for people
and AI assistants; its skill file, `.claude/skills/ogc-glossary/SKILL.md`,
tells an assistant to ask the graph and never to answer from memory. The
vendored d3 and oxigraph run Appendix A in the browser without the network.

The graphs themselves are written in a small set of ontologies, none
invented here beyond the specification's own handles. PROV-O says who did
what and when: agents, activities, entities, attribution and derivation.
EARL says what was asserted: an assertor, a mode, a subject, a test and an
outcome of passed, failed or cannot tell, which is why a determination is
never a Boolean. SKOS holds the glossary as concepts with labels,
definitions and notes. OWL and RDF Schema declare the Evaluation Process
Ontology's classes and properties. SHACL states every check, over the
record, the model graph and the rulings. The OMG SysML v2 vocabulary is what
the converter renders the model into, with a few tool facts of its own. The
specification's namespaces under w3id.org name the terms, the sources, the
rulings, the essentials, the crosswalk, the derived ends of the model graph
and the measles record. The table below counts what each is used for.

```{include} ../generated/toolchain.md
```

## The reviewer recipe

From a clone of the repository with uv and Node.js installed:

```bash
uv sync
bash toolchain/get-sysml.sh
bash checks/run-checks.sh
uv run -q ogc doctor
uv run myst start
```

`uv sync` creates `.venv` from the lockfile and reports the packages it
installed. `get-sysml.sh` prints `sysml installed+verified` on a first
fetch and nothing when the verified binary is already in place; a digest
mismatch exits 1. The gate prints one line per step, `pass` or `FAIL`, and
ends with `CHECKS: PASS` or `CHECKS: FAIL` followed by the commit it
judged; that line is what the pre-push hook and CI require. `ogc doctor`
prints its checks and ends with `VERDICT: PASS`. `myst start` builds the
site and prints the local address to open it at.

## The first rung

The appendices are the first rung of backup: the explorer, the proofs, the
rulings and this review of the toolchain. The repository is the richer one:
every graph, shape, script, test and notebook the site is rendered from,
with the gate that judges them. A reader need not trust the authors. They
can run the recipe and read the verdict themselves.
