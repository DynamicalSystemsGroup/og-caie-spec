# og-caie-spec

**Ontology-Grounded Contextual AI Evaluation (OG-CAIE) as an executable
specification.** Site: <https://dynamicalsystemsgroup.github.io/og-caie-spec/>

The process Humane Intelligence and Dynamical Systems Group use to evaluate a
deployed AI system against the needs of a specific domain, written down as:

- a **glossary** whose every term cites one canonical definition (ISO 9000:2026,
  SEVOCAB, NIST AI 700-2, W3C), with exactly three coined terms;
- a **SysML v2 model** (OpenSysML v0.4.3) of the Evaluation Process Ontology
  as a standard operating procedure and of the human and machine assemblage
  that runs it, with twelve requirements each tagged machine-verified or
  human-validated;
- one **evaluation record** (PROV-O + EARL) of the measles chatbot example,
  checked by SHACL shapes, with counterexamples that must fail;
- a **rulings register** holding every interpretive choice verbatim.

## Status (2026-09-06)

- **Glossary: ratified, with nine party quotes pending.** 58 terms, 3 coined,
  settled through 26 rulings (R-01 to R-26) recorded verbatim in
  `rulings/adjudications.ttl`. 57 quotes are machine-located in content-hashed
  snapshots, 22 verified by Z; the nine quotes for the party terms added on
  2026-09-06 are on rulings sheet 03 awaiting Z's tick, one of them (contract)
  awaiting a screenshot (concern C-24). Concerns C-25 and C-26 are open.
- **Model: revised (R-21 to R-26).** SysML holds structure only; the pruned
  RDF rendering `model/og-caie.model.ttl` is the canonical structure (R-22),
  checked by wiring shapes M1 to M5 over kinds of parts and ports: four
  parties, three actor categories within the testing organization, the
  seven-step EPO as a process DAG, 47 ports and 27 seams, every input wired
  once and every output somewhere. Three model counterexamples fail their
  shape. The essentials SCI-01 to SCI-12 live in `model/trace.ttl`.
- **Record and shapes: current.** The measles record names the parties, the
  agreement, the access, the stakeholder input, the appropriateness
  assessment, the plan approval and the delivery; shapes S0 to S8 and nine
  RDF counterexamples follow the rulings; the traceback query reaches the
  parties.
- **Pending outside the repo.** The w3id redirect
  (perma-id/w3id.org#6652) is open; IRIs resolve nowhere until it merges. The
  paper draft and the term contract will be aligned to this glossary once the
  glossary is closed.

## Authors and citation

A collaboration between **Dynamical Systems Group** and **Humane Intelligence**,
co-authored by Michael Zargham (DSG) and Julie Hollek (HI). Cite it as such;
`CITATION.cff` carries the machine-readable form (GitHub shows it under
"Cite this repository").

## Run the gate

```bash
uv sync && bash checks/run-checks.sh
```

The only verdict is the `CHECKS: PASS|FAIL` line; details in `checks/out/`.

## IRIs

Ontology and record IRIs are authored under `https://w3id.org/og-caie/`.
Until the w3id redirect is merged they resolve nowhere and are used purely
as identifiers; the site above is the fallback.

## Licence

CC BY-SA 4.0 for the whole work. The licence does not extend to the quoted
source materials, which remain their publishers' property. This is an open
standards activity under development with a computational implementation
pathway. See `LICENSE.md`.
