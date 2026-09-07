## The Python environment

Python `>=3.12` (`pyproject.toml`), pinned to `3.12` by `.python-version` so that `uv sync` installs the same interpreter everywhere. `uv sync` reproduces the environment from `uv.lock` (lockfile version 1, revision 3): 111 packages in all, 10 direct (3 runtime, 7 dev) and 101 transitive, every one pinned to a version and a content hash. The project `og-caie-spec` is installed editable and provides the `ogc` command.

| Package | Group | Constraint (`pyproject.toml`) | Locked (`uv.lock`) |
|---|---|---|---|
| `rdflib` | runtime | `>=7.0` | `7.6.0` |
| `pyshacl` | runtime | `>=0.27` | `0.40.1` |
| `pypdf` | runtime | `>=6.0` | `6.17.0` |
| `pytest` | dev | `>=8.0` | `9.1.1` |
| `pyyaml` | dev | `>=6.0` | `6.0.3` |
| `mystmd` | dev | `>=1.3` | `1.10.1` |
| `nbclient` | dev | `>=0.10` | `0.11.0` |
| `nbformat` | dev | `>=5.10` | `5.11.1` |
| `jupyter` | dev | `>=1.0` | `1.1.1` |
| `ipykernel` | dev | `>=6.29` | `7.3.0` |

## The pinned converter

| Setting | Value | Read from |
|---|---|---|
| Release | OpenSysML v0.4.3 | `model/model_manifest.json` |
| Fetched from | `https://github.com/Open-MBEE/OpenSysML/releases/download/v0.4.3` | `toolchain/get-sysml.sh` (`VER=v0.4.3`) |
| Invocation | `-convert ttl` | `model/model_manifest.json` |
| Digest file | `toolchain/sysml-binaries.sha256`, sha256 `8efae36144923a29a21aa57d59286442db5ffaaa9a3773fafcc57616ade6f961` | `model/model_manifest.json` |
| Authoring source | `model/og-caie.sysml`, sha256 `422d772eee9462fee81232c1e652a0a74e89256a119795a761bb1d278a26adfb` | `model/model_manifest.json` |
| Term map | `model/sysml_term_map.csv`, 59 terms, sha256 `76069cb93b389619ffe4a8836a6e015a72620c9f1d56316c6dcee18a40364ba9` | `model/model_manifest.json` |
| Canonical graph | `model/og-caie.model.ttl`, 4754 triples of 15898 converted (budget 5800, headroom 1046), sha256 `d8846769d629be308a0ab573e988f6d581f9ae160ecef0e2c00bfbee80ede444` | `model/model_manifest.json` |

Per platform, the digest the installed binary must hash to (`toolchain/sysml-binaries.sha256`) and the digest the release tarball must hash to before it is unpacked (`toolchain/SHA256SUMS.pinned`); `toolchain/get-sysml.sh` checks both on every run.

| Platform | Installed binary sha256 | Release tarball sha256 |
|---|---|---|
| darwin-arm64 | `a3298d68a08b863fba276bd6d0d72aad9947cdeb4b28103ce9b526400f8f475b` | `0927e2e7bbf86c6b6e546d275273c529808f98b6da9c525155e8a80bba4623bf` |
| darwin-amd64 | `712b6c8290aea0b0395f1ea313b6a2af0754202524055733824f2064b49dfe2c` | `95bfa593d773a5fabe99402dec8e860163d0673299ef8b038dd7c0d2e6f97350` |
| linux-amd64 | `1fba036a16367133e6f55026f254ca4749502bb35b0c6ae0e9990961e1461d30` | `661df51718d8506fff925d7b89d0cc119c5c1247f389f9bd9b87d6443ac4553d` |
| linux-arm64 | `571ab5f1bf0ba0d27732cbc1afed4d724cdc38ddd6ba7636ef67422a77648925` | `ceba7303c9ffd391b2849b4ae4e15ec52d9ccb951e81b8dc47b7359ee07cdc96` |

## The ontologies and vocabularies

What the graphs are written in, counted over the committed Turtle files (`vocabulary/og-caie.ttl`, `vocabulary/epo.ttl`, `vocabulary/crosswalk.ttl`, `sources/sources.ttl`, `rulings/adjudications.ttl`, `model/trace.ttl`, `model/og-caie.model.ttl`, `track/measles-run.ttl`, `shapes/epo.shapes.ttl`, `shapes/model.shapes.ttl`, `shapes/rulings.shapes.ttl`): the classes and properties of each vocabulary that the graphs actually use, and the subjects each names. The W3C and OMG vocabularies are adopted as published; the specification's own namespaces resolve under w3id.org.

| Prefix | Namespace | Whose | What it does here | Classes used | Properties used | Subjects | Reference |
|---|---|---|---|---|---|---|---|
| `rdf` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#` | W3C | RDF 1.1: typing (rdf:type) and lists | 0 | 3 | 0 | <https://www.w3.org/TR/rdf11-concepts/> |
| `rdfs` | `http://www.w3.org/2000/01/rdf-schema#` | W3C | RDF Schema: labels, comments, subclassing | 0 | 6 | 0 | <https://www.w3.org/TR/rdf-schema/> |
| `owl` | `http://www.w3.org/2002/07/owl#` | W3C | OWL 2: the EPO's classes and properties | 4 | 0 | 0 | <https://www.w3.org/TR/owl2-overview/> |
| `skos` | `http://www.w3.org/2004/02/skos/core#` | W3C | SKOS: the glossary's concepts, labels, definitions and notes | 2 | 5 | 0 | <https://www.w3.org/TR/skos-reference/> |
| `prov` | `http://www.w3.org/ns/prov#` | W3C | PROV-O: who did what and when in the record (agents, activities, entities, derivation, attribution) | 6 | 9 | 0 | <https://www.w3.org/TR/prov-o/> |
| `earl` | `http://www.w3.org/ns/earl#` | W3C | EARL 1.0: assertions with an assertor, a mode, a subject, a test and an outcome (passed, failed, cantTell) | 2 | 7 | 0 | <https://www.w3.org/TR/EARL10-Schema/> |
| `sh` | `http://www.w3.org/ns/shacl#` | W3C | SHACL: the shapes that check the record, the model graph and the rulings, including SHACL-SPARQL constraints | 1 | 16 | 0 | <https://www.w3.org/TR/shacl/> |
| `sysml` | `https://www.omg.org/spec/SysML#` | OMG | SysML v2 vocabulary as the OpenSysML converter renders the model: definitions, usages, ports, interfaces, actions, successions, flows | 27 | 18 | 0 | <https://www.omg.org/spec/SysML/2.0/> |
| `sysx` | `urn:opensysml:sysml:` | OpenSysML | the converter's own facts: the ends of a connection, the source text of a statement, a prefix keyword | 0 | 4 | 0 | <https://github.com/OpenMBEE/opensysml> |
| `elmt` | `urn:sysmlv2:element:` | OpenSysML | the converter's element identifiers, one per model element | 0 | 0 | 542 | <https://github.com/OpenMBEE/opensysml> |
| `expr` | `urn:opensysml:expr:` | OpenSysML | the converter's expression identifiers (end paths, multiplicity bounds) | 0 | 0 | 415 | <https://github.com/OpenMBEE/opensysml> |
| `ogc` | `https://w3id.org/og-caie/` | this specification | the register: citation classes and properties, shapes' names, concerns, rulings, crosswalk rows, trace essentials | 5 | 45 | 46 | <https://w3id.org/og-caie/> |
| `term` | `https://w3id.org/og-caie/terms#` | this specification | the glossary's terms | 0 | 0 | 62 | <https://w3id.org/og-caie/> |
| `src` | `https://w3id.org/og-caie/sources#` | this specification | the source register | 0 | 0 | 23 | <https://w3id.org/og-caie/> |
| `rul` | `https://w3id.org/og-caie/rulings#` | this specification | concerns and rulings | 0 | 0 | 106 | <https://w3id.org/og-caie/> |
| `epo` | `https://w3id.org/og-caie/epo#` | this specification | the Evaluation Process Ontology's handles: item classes, steps, layers, roles and their properties | 38 | 42 | 112 | <https://w3id.org/og-caie/> |
| `xw` | `https://w3id.org/og-caie/crosswalk#` | this specification | the crosswalk rows of the front page's bridge into the standards | 0 | 0 | 7 | <https://w3id.org/og-caie/> |
| `tr` | `https://w3id.org/og-caie/trace#` | this specification | the essentials SCI-01 to SCI-13 | 0 | 0 | 13 | <https://w3id.org/og-caie/> |
| `ogm` | `https://w3id.org/og-caie/model#` | this specification | the derived ends of the canonical model graph (resolved ports, flow ends, successions, relations) | 0 | 10 | 0 | <https://w3id.org/og-caie/> |
| `run` | `https://w3id.org/og-caie/run/measles#` | this specification | the measles record's items and agents | 0 | 0 | 49 | <https://w3id.org/og-caie/> |

## The vendored browser libraries

Appendix A runs in the browser on two libraries committed under `explorer/vendor/`, so the explorer loads nothing from the network. Versions and licences are as the files state them.

| Library | Version | Licence | Source or copyright | Stated in |
|---|---|---|---|---|
| d3 | 7.9.0 | not stated in the file | Copyright 2010-2023 Mike Bostock | `explorer/vendor/d3.v7.min.js` (first line) |
| oxigraph (WebAssembly, `web.js`, `web_bg.wasm`) | 0.5.11 | MIT OR Apache-2.0 | <https://github.com/oxigraph/oxigraph> | `explorer/vendor/oxigraph/NOTICE.md` |

## The gate

`checks/run-checks.sh` runs 9 steps, every one, in this order; a step passes when its exit code is the expected one. The only summary is the `CHECKS: PASS` or `CHECKS: FAIL` line and `checks/out/report.json`; each step's full output is in `checks/out/last.log`. Nothing is optional and nothing fails quietly.

| # | Step | Expected exit | Command |
|---|---|---|---|
| 1 | toolchain: pinned sysml v0.4.3, digest-verified | 0 | `bash toolchain/get-sysml.sh` |
| 2 | model: validate -strict (authoring view and model counterexamples) | 0 | `toolchain/bin/sysml model/og-caie.sysml counterexamples/model/unwired-port.sysml counterexamples/model/expert-administers-tests.sysml counterexamples/model/missing-accountable.sysml counterexamples/model/no-obligation.sysml -validate -strict` |
| 3 | model graph: convert, prune, byte-identical to the committed canonical graph | 0 | `uv run python scripts/prune_model.py && git diff --quiet -- model/og-caie.model.ttl model/model_manifest.json` |
| 4 | ogc: doctor (labels unambiguous, quotes located, record consistent) | 0 | `uv run -q ogc doctor --no-cache` |
| 5 | notebooks: executed by nbclient, outputs equal the committed ones, verdict NOTEBOOK: PASS | 0 | `uv run python scripts/execute_notebooks.py --check` |
| 6 | tests: full suite | 0 | `uv run pytest -q` |
| 7 | generated/ and explorer/: regenerate byte-identically | 0 | `bash checks/regen.sh (uv run python scripts/render.py && uv run python scripts/render_diagrams.py && uv run python scripts/render_explorer.py && uv run python scripts/render_toolchain.py) && git diff --quiet -- generated/ explorer/` |
| 8 | site: myst build --html | 0 | `uv run myst build --html` |
| 9 | site: the explorer copied next to the built site | 0 | `bash scripts/copy_explorer.sh` |

## Continuous integration

`.github/workflows/deploy.yml` (workflow `checks-and-deploy`) runs on push (branches: main), pull_request, workflow_dispatch. The `checks` job runs the same gate script; the `deploy` job needs it and runs only when `github.ref == 'refs/heads/main' && github.event_name != 'pull_request'`.

| Job | Step | Runs |
|---|---|---|
| checks | actions/checkout@v4 | `actions/checkout@v4` |
| checks | astral-sh/setup-uv@v5 | `astral-sh/setup-uv@v5` |
| checks | actions/setup-node@v4 | `actions/setup-node@v4` (node-version: 20) |
| checks | python environment | `uv sync` |
| checks | full gate | `bash checks/run-checks.sh` |
| checks | build the site for Pages | `BASE_URL="/${REPO_NAME}" uv run myst build --html` |
| checks | the knowledge graph explorer next to the site | `bash scripts/copy_explorer.sh` |
| checks | actions/upload-pages-artifact@v3 | `actions/upload-pages-artifact@v3` (path: _build/html) |
| deploy | actions/deploy-pages@v4 | `actions/deploy-pages@v4` |

## Enforcement points

The same script gives the verdict at three points; none can be skipped by editing a page.

| Where | What runs | Read from |
|---|---|---|
| Before every push, in the author's checkout | `bash checks/gate-head.sh` (installed with `git config core.hooksPath checks/hooks`) | `checks/hooks/pre-push` |
| On the committed HEAD, in a detached worktree at `.cache/gate-head.XXXXXX`, never on the working tree | `bash checks/run-checks.sh` | `checks/gate-head.sh` |
| In CI, on a fresh runner, before any deploy | `bash checks/run-checks.sh`; `deploy` needs `checks` | `.github/workflows/deploy.yml` |
