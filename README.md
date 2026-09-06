# og-caie-spec

**Ontology-Grounded Contextual AI Evaluation (OG-CAIE) as an executable
specification.** Site: <https://dynamicalsystemsgroup.github.io/og-caie-spec/>

The process Humane Intelligence and Dynamical Systems Group use to evaluate a
deployed AI system against the needs of a specific domain, written down as:

- a **glossary** whose every term cites one canonical definition (ISO 9000:2026,
  SEVOCAB, NIST AI 700-2, W3C), with exactly three coined terms;
- a **SysML v2 model** (OpenSysML v0.4.3) of the Evaluation Process Ontology
  as a standard operating procedure and of the human and machine assemblage
  that runs it, with nine requirements each tagged machine-verified or
  human-validated;
- one **evaluation record** (PROV-O + EARL) of the measles chatbot example,
  checked by SHACL shapes, with counterexamples that must fail;
- a **rulings register** holding every interpretive choice verbatim.

## Status (2026-09-06)

- **Glossary: ratified.** 48 terms, 3 coined, settled through twenty rulings
  (R-01 to R-20) recorded verbatim in `rulings/adjudications.ttl`. Every quote
  is verified: 56 machine-located in content-hashed snapshots, 22 verified by
  Z against the ISO Online Browsing Platform screenshots or the browsing
  platforms themselves. No quote is pending.
- **Record and shapes: current.** The measles record, the EPO handle classes,
  shapes S1 to S8, the counterexamples and the two queries follow the rulings,
  including sessions and turns (R-13), the test plan and expected results
  (R-12), evidence as domain and determination as codomain (R-18, R-20), and
  conformance as the reclaimed word for the correctly constructed record
  (R-16).
- **Model: behind.** The SysML model was built before rulings R-12 to R-20 and
  has been patched to keep the gate green, not redesigned. Its part and port
  definitions do not yet, together, give the EPO structure that guarantees
  traceability and coverage as the end state given a DSO and a requirement
  set expressed in EPO and DSO concepts. That deep revision is the next task.
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
